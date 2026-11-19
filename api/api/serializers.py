"""Session 16: validation (field, object and model rules), nested and related data, and booking."""
from datetime import time

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from clinic.models import Appointment, Doctor, Report, Speciality, TimeSlot
from clinic.services import SlotTaken, book_slot

OPENS, CLOSES = time(8, 0), time(20, 0)                     # the same hours as the slot_in_opening_hours constraint


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ["id", "name", "slug"]


class DoctorSerializer(serializers.ModelSerializer):
    speciality = SpecialitySerializer(read_only=True)        # nested: shown as an object when reading
    speciality_slug = serializers.SlugRelatedField(           # related: sent as a slug when writing
        source="speciality", slug_field="slug", queryset=Speciality.objects.all(), write_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "name", "speciality", "speciality_slug", "fee", "bio", "is_active"]

    def validate_fee(self, value):                           # field-level: validate_<field name>
        if value <= 0:
            raise serializers.ValidationError("The fee must be more than zero.")
        return value


class FeeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    currency = serializers.CharField()


class DoctorV2Serializer(DoctorSerializer):
    """Version 2 (Session 20): the fee is an object with a currency. Version 1 clients keep the old shape."""
    fee = serializers.SerializerMethodField()

    @extend_schema_field(FeeSerializer)                      # tells the schema what the method returns
    def get_fee(self, doctor):
        return {"amount": f"{doctor.fee:.2f}", "currency": "INR"}


class MeSerializer(serializers.Serializer):
    """The answer of /me/ (Session 18), written down for the schema."""
    username = serializers.CharField()
    role = serializers.CharField()
    groups = serializers.ListField(child=serializers.CharField())
    is_patient = serializers.BooleanField()
    authenticated_by = serializers.CharField()


class SlotSerializer(serializers.ModelSerializer):
    booked = serializers.BooleanField(read_only=True)
    start_time = serializers.TimeField(format="%H:%M")
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)   # related data through source=

    class Meta:
        model = TimeSlot
        fields = ["id", "doctor", "doctor_name", "date", "start_time", "booked"]

    def validate_start_time(self, value):                    # one field, alone
        if value.minute not in (0, 30) or value.second:
            raise serializers.ValidationError("Slots start on the hour or at half past.")
        return value

    def validate(self, data):                                # the whole object, after every field passed
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        if start and not OPENS <= start <= CLOSES:
            raise serializers.ValidationError(
                {"start_time": f"The clinic is open from {OPENS:%H:%M} to {CLOSES:%H:%M}."})
        return data


class SlotSummarySerializer(serializers.ModelSerializer):
    """A small slot for nesting inside an appointment."""
    start_time = serializers.TimeField(format="%H:%M")
    doctor = serializers.CharField(source="doctor.name")

    class Meta:
        model = TimeSlot
        fields = ["id", "doctor", "date", "start_time"]


class AppointmentSerializer(serializers.ModelSerializer):
    """Reading: the slot is nested, so a client needs one request, not three."""
    slot = SlotSummarySerializer(read_only=True)
    patient = serializers.StringRelatedField()

    class Meta:
        model = Appointment
        fields = ["id", "slot", "patient", "status", "reason", "created_at"]
        read_only_fields = fields


class BookingSerializer(serializers.Serializer):
    """Writing: the client sends a slot id and a reason; the patient is the logged-in user."""
    slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    # Session 19: "only patients" moved to the IsPatient permission, which runs before any validation

    def create(self, validated_data):
        patient = self.context["request"].user.patient
        try:
            return book_slot(validated_data["slot"], patient, validated_data["reason"].strip())
        except SlotTaken:                                    # the database constraint said no (Session 06)
            raise serializers.ValidationError({"slot": ["This time slot is already booked."]})


# Module 9, Session 07: a report file for an appointment (the model of Session 12).
class ReportSerializer(serializers.ModelSerializer):
    """The model field's validators run here too: type, size and first bytes."""
    class Meta:
        model = Report
        fields = ["id", "file", "original_name", "size", "uploaded_at"]
        read_only_fields = ["original_name", "size", "uploaded_at"]
        extra_kwargs = {"file": {"write_only": True}}  # never send a path back

    def create(self, validated_data):
        upload = validated_data["file"]
        return Report.objects.create(
            appointment=self.context["appointment"],
            original_name=upload.name[:200],  # shown to people, never a path
            size=upload.size,
            **validated_data)
