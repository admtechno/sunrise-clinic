"""Run from the project folder: python make_samples.py
Session 12: makes five sample files in samples/ to test the report upload (nothing real inside)."""
import struct
import zlib
from pathlib import Path

folder = Path("samples")
folder.mkdir(exist_ok=True)


def pdf(text):
    """A tiny but valid one-page PDF that shows one line of text."""
    stream = f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
               b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = b"%PDF-1.4\n", []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    return out + b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)


def png(width=40, height=40):
    """A small grey square as a real PNG image."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\x00" + b"\x99" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


files = {
    "blood_test.pdf": pdf("Blood test - sample file for the Django module"),
    "xray.png": png(),
    "big_scan.pdf": pdf("Big scan") + b"\n%" + b"0" * (3 * 1024 * 1024),      # a real PDF start, but 3 MB
    "long_scan.pdf": pdf("Long scan") + b"\n%" + b"0" * (1536 * 1024),    # Module 9: 1.5 MB, allowed
    "not_really.pdf": b"<html><script>alert('hello')</script></html>",       # HTML with a .pdf name
    "setup.exe": b"MZ" + b"\x00" * 510,                                       # a Windows program
}
for name, data in files.items():
    (folder / name).write_bytes(data)
    print(f"{name:15} {len(data):>9} bytes  starts with {data[:5]!r}")
