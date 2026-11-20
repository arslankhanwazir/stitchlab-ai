"""
M2.1: Verify extraction fidelity.
Compares source markdown documents against Docling-extracted markdown files.
Checks:
1. All # and ## headings identical.
2. Numbered items (D01 sec 3.3 = 6 steps, D04 sec 1 = 8 fields).
3. Every table cell in D05, D06, company-profile.
4. Key strings present ($15,000, $10,000, $4,800, 45, +1 555 0177, "5 working days", "30 calendar days", "3 working days").
5. Section numbers like 3.3 / 4.2 preserved.
6. "FICTIONAL" label present in all eight files.
"""

import sys
import re
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

DOCS_DIR = paths.REPO_ROOT / "documents" / "fictional-brightpath"
EXTRACTED_DIR = DOCS_DIR / "extracted"

FILES = [
    "company-profile.md",
    "D01-client-onboarding-sop.md",
    "D02-enterprise-refund-process.md",
    "D03-campaign-approval-rules.md",
    "D04-paid-social-brief-template.md",
    "D05-escalation-contacts.md",
    "D06-retainer-pricing-cancellation.md",
    "D07-client-faq.md",
]


def extract_headings(text: str):
    headings = []
    for line in text.splitlines():
        line_s = line.strip()
        if line_s.startswith("# ") or line_s.startswith("## "):
            headings.append(line_s)
    return headings


def run_checks():
    failures = []
    passes = []

    print("=== M2.1 Extraction Verification ===")

    # 1. Headings check
    print("\n[Check 1] Checking # and ## headings identical across source and extracted...")
    for fname in FILES:
        src = (DOCS_DIR / fname).read_text(encoding="utf-8")
        ext = (EXTRACTED_DIR / fname).read_text(encoding="utf-8")
        src_h = extract_headings(src)
        ext_h = extract_headings(ext)
        if src_h == ext_h:
            passes.append(f"Headings match for {fname}: {len(src_h)} headings")
        else:
            failures.append(f"Headings mismatch in {fname}:\n  Source: {src_h}\n  Extracted: {ext_h}")

    # 2. Numbered items
    print("\n[Check 2] Checking numbered items in D01 (sec 3.3 = 6 steps) and D04 (sec 1 = 8 fields)...")
    d01_text = (EXTRACTED_DIR / "D01-client-onboarding-sop.md").read_text(encoding="utf-8")
    d01_steps = re.findall(r"^\s*([1-6])\.\s+(.+)$", d01_text, re.MULTILINE)
    if len(d01_steps) == 6:
        passes.append(f"D01 sec 3.3 has exactly 6 numbered steps: {[s[0] for s in d01_steps]}")
    else:
        failures.append(f"D01 sec 3.3 expected 6 steps, found {len(d01_steps)}: {d01_steps}")

    d04_text = (EXTRACTED_DIR / "D04-paid-social-brief-template.md").read_text(encoding="utf-8")
    d04_fields = re.findall(r"^\s*([1-8])\.\s+(.+)$", d04_text, re.MULTILINE)
    if len(d04_fields) == 8:
        passes.append(f"D04 sec 1 has exactly 8 numbered fields: {[f[0] for f in d04_fields]}")
    else:
        failures.append(f"D04 sec 1 expected 8 fields, found {len(d04_fields)}: {d04_fields}")

    # 3. Every table cell in D05, D06, company-profile
    print("\n[Check 3] Checking every table cell in D05, D06, company-profile...")
    
    # company-profile
    cp_text = (EXTRACTED_DIR / "company-profile.md").read_text(encoding="utf-8")
    cp_cells = [
        "Role", "Name",
        "Managing Director", "Maya Chen",
        "Marketing Director", "Daniel Okafor",
        "Head of Client Services", "Priya Shah",
        "Finance Lead", "Tom Reyes",
        "Systems Lead (IT)", "Sam Whitfield",
        "Account Leads", "Six people, named in ClickUp"
    ]
    cp_missing = [c for c in cp_cells if c not in cp_text]
    if not cp_missing:
        passes.append("company-profile: all 14 table cells present")
    else:
        failures.append(f"company-profile missing table cells: {cp_missing}")

    # D05
    d05_text = (EXTRACTED_DIR / "D05-escalation-contacts.md").read_text(encoding="utf-8")
    d05_cells = [
        "Issue", "Contact", "Email", "Phone",
        "Account questions", "Account Lead on the client's Space", "(named in ClickUp)", "(named in ClickUp)",
        "Billing dispute", "Tom Reyes, Finance Lead", "tom.reyes@brightpath-demo.example", "+1 555 0142",
        "Creative or approvals", "Daniel Okafor, Marketing Director", "daniel.okafor@brightpath-demo.example", "+1 555 0136",
        "Client services concerns", "Priya Shah, Head of Client Services", "priya.shah@brightpath-demo.example", "+1 555 0129",
        "Platform or server outage", "Sam Whitfield, Systems Lead (on-call)", "sam.whitfield@brightpath-demo.example", "+1 555 0177"
    ]
    d05_missing = [c for c in d05_cells if c not in d05_text]
    if not d05_missing:
        passes.append("D05: all 24 table cells present")
    else:
        failures.append(f"D05 missing table cells: {d05_missing}")

    # D06
    d06_text = (EXTRACTED_DIR / "D06-retainer-pricing-cancellation.md").read_text(encoding="utf-8")
    d06_cells = [
        "Tier", "Monthly fee", "Included hours",
        "Essentials", "$2,500", "20",
        "Growth", "$4,800", "45",
        "Enterprise", "$9,500", "100"
    ]
    d06_missing = [c for c in d06_cells if c not in d06_text]
    if not d06_missing:
        passes.append("D06: all 12 table cells present")
    else:
        failures.append(f"D06 missing table cells: {d06_missing}")

    # 4. Key strings present exactly
    print("\n[Check 4] Checking key strings present exactly...")
    all_extracted_text = "\n".join((EXTRACTED_DIR / f).read_text(encoding="utf-8") for f in FILES)
    key_strings = [
        "$15,000",
        "$10,000",
        "$4,800",
        "45",
        "+1 555 0177",
        "5 working days",
        "30 calendar days",
        "3 working days"
    ]
    for ks in key_strings:
        if ks in all_extracted_text:
            passes.append(f"Key string found: '{ks}'")
        else:
            failures.append(f"Key string missing: '{ks}'")

    # 5. Section numbers like 3.3 / 4.2 preserved
    print("\n[Check 5] Checking section numbers preserved...")
    sample_sections = [
        ("D01-client-onboarding-sop.md", ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "5.1", "5.2"]),
        ("D02-enterprise-refund-process.md", ["2.1", "2.2", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1", "5.2"]),
        ("D03-campaign-approval-rules.md", ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1", "5.2"]),
    ]
    for doc_name, sec_list in sample_sections:
        content = (EXTRACTED_DIR / doc_name).read_text(encoding="utf-8")
        for sec in sec_list:
            if sec in content:
                passes.append(f"{doc_name} section {sec} preserved")
            else:
                failures.append(f"{doc_name} section {sec} missing")

    # 6. "FICTIONAL" label present in all eight
    print("\n[Check 6] Checking 'FICTIONAL' label present in all 8 documents...")
    for fname in FILES:
        content = (EXTRACTED_DIR / fname).read_text(encoding="utf-8")
        if "FICTIONAL" in content:
            passes.append(f"'FICTIONAL' present in {fname}")
        else:
            failures.append(f"'FICTIONAL' missing in {fname}")

    # Summary
    print("\n" + "=" * 50)
    print(f"VERIFICATION SUMMARY: {len(passes)} PASSED, {len(failures)} FAILED")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\nRESULT: ALL CHECKS PASS")
        return True


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
