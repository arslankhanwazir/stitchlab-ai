"""
M6B.2 Done-check Unit Test for Data Masking.
Tests reversible masking on D05 contacts table.
Asserts:
1. All emails, phone numbers, and names in D05 are masked.
2. None of the original names/emails/phones remain in the masked text.
3. Unmasking restores the original text exactly.
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from masking import mask_data, unmask_data

D05_FILE = (
    paths.REPO_ROOT
    / "documents"
    / "fictional-brightpath"
    / "extracted"
    / "D05-escalation-contacts.md"
)


class TestMasking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not D05_FILE.exists():
            raise FileNotFoundError(f"D05 file not found at {D05_FILE}")
        cls.d05_content = D05_FILE.read_text(encoding="utf-8")

    def test_d05_contacts_table_masked_and_restored(self):
        original = self.d05_content

        # 1. Apply masking
        masked, mapping = mask_data(original)
        print("\n=== MASKED D05 TEXT (SAMPLE) ===")
        print(masked[:400])
        print("\n=== MAPPING TOKENS ===")
        for k, v in mapping.items():
            print(f"{k} -> {v}")

        # Assert all expected names in D05 are masked
        d05_names = ["Tom Reyes", "Daniel Okafor", "Priya Shah", "Sam Whitfield"]
        for name in d05_names:
            self.assertNotIn(name, masked, f"Name {name} should be masked!")

        # Assert emails are masked
        d05_emails = [
            "tom.reyes@brightpath-demo.example",
            "daniel.okafor@brightpath-demo.example",
            "priya.shah@brightpath-demo.example",
            "sam.whitfield@brightpath-demo.example",
        ]
        for email in d05_emails:
            self.assertNotIn(email, masked, f"Email {email} should be masked!")

        # Assert phone numbers are masked
        d05_phones = ["+1 555 0142", "+1 555 0136", "+1 555 0129", "+1 555 0177"]
        for phone in d05_phones:
            self.assertNotIn(phone, masked, f"Phone {phone} should be masked!")

        # Assert tokens are present
        self.assertTrue(any("PERSON_NAME" in k for k in mapping.keys()))
        self.assertTrue(any("EMAIL_ADDR" in k for k in mapping.keys()))
        self.assertTrue(any("PHONE_NUM" in k for k in mapping.keys()))

        # 2. Unmask and assert exact restoration
        restored = unmask_data(masked, mapping)
        self.assertEqual(
            restored,
            original,
            "Unmasked text must match original source text exactly!",
        )


if __name__ == "__main__":
    unittest.main()
