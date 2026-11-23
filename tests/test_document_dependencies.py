"""Offline integration checks for the contract document dependency stack."""
import io
import ssl
import tempfile
import unittest
from pathlib import Path

import anyio
import certifi
from PIL import Image
from app.pdf_report import generate_contract_pdf
from app.pdf_utils import extract_text_from_pdf


class DocumentDependencyTests(unittest.TestCase):
    def test_contract_report_remains_readable(self):
        report = generate_contract_pdf({
            "contract_id": "synthetic-001",
            "filename": "synthetic-contract.pdf",
            "contract_type": "saas",
            "risk_assessment": {
                "overall_risk_level": "low",
                "overall_risk_score": 10,
                "executive_summary": "Synthetic contract integration check.",
            },
        })
        self.assertTrue(report.startswith(b"%PDF-"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.pdf"
            path.write_bytes(report)
            text = extract_text_from_pdf(path)
        self.assertIn("synthetic-001", text)
        self.assertIn("Synthetic contract integration check", text)

    def test_image_decoders_preserve_dimensions_and_pixels(self):
        for format_name in ("PNG", "TIFF", "JPEG"):
            with self.subTest(format=format_name):
                stream = io.BytesIO()
                Image.new("RGB", (12, 8), (80, 120, 160)).save(stream, format=format_name)
                stream.seek(0)
                with Image.open(stream) as decoded:
                    decoded.load()
                    self.assertEqual(decoded.size, (12, 8))
                    pixel = decoded.convert("RGB").getpixel((0, 0))
                    self.assertTrue(all(abs(a - b) <= 3 for a, b in zip(pixel, (80, 120, 160))))

    def test_async_document_work_and_trust_store(self):
        async def read_document():
            with tempfile.TemporaryDirectory() as directory:
                path = anyio.Path(directory) / "synthetic.txt"
                await path.write_text("synthetic document", encoding="utf-8")
                self.assertEqual(await path.read_text(encoding="utf-8"), "synthetic document")
            async with anyio.create_task_group() as tasks:
                tasks.start_soon(anyio.sleep, 0)
        anyio.run(read_document)
        context = ssl.create_default_context(cafile=certifi.where())
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertGreater(len(context.get_ca_certs()), 0)


if __name__ == "__main__":
    unittest.main()
