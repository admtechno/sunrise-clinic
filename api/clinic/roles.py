"""The clinic's groups and their permissions (Session 11). Session 22 moved them here from setup_roles.py,
so the script and the API tests make exactly the same groups."""
from django.contrib.auth.models import Group, Permission

ROLES = {
    "Reception": ["view_doctor", "view_speciality", "view_patient", "add_patient", "view_appointment",
                  "add_appointment", "change_appointment",
                  "view_timeslot", "add_timeslot", "change_timeslot", "delete_timeslot"],
    "Doctors": ["view_patient", "view_appointment", "view_timeslot"],
}


def create_groups():
    """Create or update the groups; returns {name: group}."""
    groups = {}
    for name, codenames in ROLES.items():
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set(Permission.objects.filter(content_type__app_label="clinic", codename__in=codenames))
        groups[name] = group
    return groups
