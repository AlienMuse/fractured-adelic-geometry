"""Certificate serialisation and independent-checker regressions."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from bsdkit.certificates import Certificate, make_ap_certificate, make_rank_lower_certificate
from bsdkit.data import get_curve


class CertificateTests(unittest.TestCase):
    def _check_independently(self, certificate: Certificate) -> dict[str, object]:
        checker = Path(__file__).resolve().parents[2] / "verify" / "check.py"
        path = Path(__file__).resolve().parent / "checker-certificate.json"
        try:
            path.write_text(certificate.to_json(), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(checker), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_round_trip_and_independent_ap_checker(self) -> None:
        certificate = make_ap_certificate(get_curve("11.a1").curve, 7)
        restored = Certificate.from_json(certificate.to_json())
        self.assertEqual(restored, certificate)
        self.assertEqual(restored.content_hash, certificate.content_hash)
        result = self._check_independently(certificate)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["content_hash"], certificate.content_hash)

    def test_independent_rank_lower_checker(self) -> None:
        record = get_curve("37.a1")
        certificate = make_rank_lower_certificate(record.curve, record.generators)
        self.assertEqual(certificate.rigour, "proved")
        result = self._check_independently(certificate)
        self.assertTrue(result["accepted"])

    def test_tampering_is_rejected(self) -> None:
        certificate = make_ap_certificate(get_curve("11.a1").curve, 5)
        value = json.loads(certificate.to_json())
        value["evidence"][0]["data"]["ap"] += 1
        with self.assertRaises(ValueError):
            Certificate.from_json(json.dumps(value))


if __name__ == "__main__":
    unittest.main()
