"""Offline regressions for the HTTP/document parser dependency updates."""
import io
import tempfile
import unittest
from pathlib import Path

import idna
from dotenv import dotenv_values, set_key
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.testclient import TestClient
from lxml import etree
from pydantic_settings import NestedSecretsSettingsSource

from app.pdf_report import generate_contract_pdf
from app.pdf_utils import extract_text_from_pdf


class ParserSecurityTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()

        @app.post("/form")
        async def form(request: Request):
            return dict(await request.form(max_fields=1, max_files=1))

        @app.post("/upload")
        async def upload(file: UploadFile = File(...)):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "document.pdf"
                path.write_bytes(await file.read())
                return {"filename": file.filename, "text": extract_text_from_pdf(path)}

        self.client = TestClient(app)

    def test_urlencoded_field_limit_and_legitimate_control(self):
        headers = {"content-type": "application/x-www-form-urlencoded"}
        for body in ("one=1&two=2", "%6fne=1&%74wo=2"):
            with self.subTest(body=body):
                response = self.client.post("/form", content=body, headers=headers)
                self.assertEqual(response.status_code, 400)
                self.assertIn("Too many fields", response.text)
        response = self.client.post("/form", content="one=a%26b", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"one": "a&b"})

    def test_multipart_field_limit(self):
        response = self.client.post("/form", files=[("one", (None, "1")), ("two", (None, "2"))])
        self.assertEqual(response.status_code, 400)
        self.assertIn("Too many fields", response.text)

    def test_multipart_pdf_upload_preserves_document_content(self):
        report = generate_contract_pdf({"contract_id": "parser-control", "filename": "contract.pdf"})
        response = self.client.post("/upload", files={"file": ("contract.pdf", report, "application/pdf")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "contract.pdf")
        self.assertIn("parser-control", response.json()["text"])

    def test_xml_default_parsers_do_not_expand_local_external_entities(self):
        with tempfile.TemporaryDirectory() as directory:
            secret = Path(directory) / "synthetic.txt"
            secret.write_text("synthetic-external-content", encoding="utf-8")
            xml = f'<!DOCTYPE doc [<!ENTITY ext SYSTEM "{secret.as_uri()}">]><doc>&ext;</doc>'.encode()
            for parse in (
                lambda data: etree.fromstring(data, etree.ETCompatXMLParser()),
                lambda data: list(etree.iterparse(io.BytesIO(data))),
            ):
                with self.subTest(parser=parse):
                    with self.assertRaises(etree.XMLSyntaxError):
                        parse(xml)
            self.assertEqual(etree.fromstring(b"<doc>ordinary</doc>").text, "ordinary")

    def test_dotenv_update_does_not_overwrite_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "outside.env"
            target.write_text("VALUE=original\n", encoding="utf-8")
            link = Path(directory) / ".env"
            link.symlink_to(target)
            set_key(link, "VALUE", "updated")
            self.assertEqual(target.read_text(encoding="utf-8"), "VALUE=original\n")
            self.assertFalse(link.is_symlink())
            self.assertEqual(dotenv_values(link)["VALUE"], "updated")

    def test_idna_preserves_valid_domains_and_rejects_oversized_labels(self):
        self.assertEqual(idna.encode("bücher.example"), b"xn--bcher-kva.example")
        for label in ("a" * 64, "ä" * 64):
            with self.subTest(label=label):
                with self.assertRaises(idna.IDNAError):
                    idna.encode(label + ".example")

    def test_nested_settings_do_not_follow_external_secret_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            secrets = root / "secrets"
            secrets.mkdir()
            (secrets / "allowed").write_text("local-value", encoding="utf-8")
            outside = root / "outside"
            outside.write_text("synthetic-external-value", encoding="utf-8")
            (secrets / "linked").symlink_to(outside)
            self.assertEqual(NestedSecretsSettingsSource.load_secrets(secrets), {"allowed": "local-value"})


if __name__ == "__main__":
    unittest.main()
