import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "TEST_REPORT.md"
OUT_PDF = ROOT / "TEST_REPORT.pdf"
LOG = ROOT / "test_output.txt"


def read_log(path: Path) -> str:
    text = None
    # Try common encodings
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            return text
        except Exception:
            continue
    # fallback: binary decode
    return path.read_bytes().decode(errors="replace")


def parse_tests(output: str):
    lines = [ln.strip() for ln in output.splitlines()]
    test_lines = []
    summary_lines = []
    capture = False
    for ln in lines:
        if re.search(r"\bFAILED\b|\bPASSED\b|\bSKIPPED\b|\bERROR\b", ln):
            test_lines.append(ln)
    # Try to capture the final summary section
    for i, ln in enumerate(lines[-200:]):
        if ln.startswith("=") and "short test summary info" in ln.lower():
            summary_lines = lines[-200+i:]
            break

    # tally by file/module
    tally = {}
    total = {"PASSED":0,"FAILED":0,"SKIPPED":0,"ERROR":0}
    for ln in test_lines:
        m = re.match(r"(tests/[^:]+):.*\b(PASSED|FAILED|SKIPPED|ERROR)\b", ln)
        if not m:
            # try alternate pattern
            parts = ln.split()
            status = parts[-1] if parts else ""
            # try to extract test path
            path_match = re.match(r"(tests/[^:\s]+)", ln)
            file = path_match.group(1) if path_match else "unknown"
        else:
            file = m.group(1)
            status = m.group(2)
        module = file.replace("tests/","")
        tally.setdefault(module, {"PASSED":0,"FAILED":0,"SKIPPED":0,"ERROR":0})
        if status in total:
            tally[module][status]+=1
            total[status]+=1

    return {
        "lines": lines,
        "tally": tally,
        "total": total,
        "summary": "\n".join(summary_lines)
    }


def write_md(report, out: Path):
    with out.open("w", encoding="utf-8") as f:
        f.write("# Test Report\n\n")
        f.write("## Summary\n\n")
        tot = report["total"]
        passed = tot.get("PASSED",0)
        failed = tot.get("FAILED",0)
        skipped = tot.get("SKIPPED",0)
        error = tot.get("ERROR",0)
        f.write(f"- **Passed:** {passed}\n")
        f.write(f"- **Failed:** {failed}\n")
        f.write(f"- **Errors:** {error}\n")
        f.write(f"- **Skipped:** {skipped}\n\n")

        f.write("## Breakdown by test file (module)\n\n")
        for mod, counts in sorted(report["tally"].items()):
            f.write(f"- **{mod}**: Passed={counts['PASSED']}, Failed={counts['FAILED']}, Error={counts['ERROR']}, Skipped={counts['SKIPPED']}\n")

        f.write("\n## Raw pytest summary (tail)\n\n")
        f.write("```")
        f.write(report.get("summary",""))
        f.write("```\n\n")

        f.write("\n## Full raw output attached separately as `test_output.txt`\n")


def write_pdf(md_path: Path, pdf_path: Path):
    text = md_path.read_text(encoding="utf-8")
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    lines = text.splitlines()
    c.setFont("Helvetica", 10)
    for ln in lines:
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - margin
        c.drawString(margin, y, ln[:110])
        y -= 12
    c.save()


def main():
    if not LOG.exists():
        print("test_output.txt not found. Run pytest and save output to test_output.txt")
        return
    raw = read_log(LOG)
    report = parse_tests(raw)
    write_md(report, OUT_MD)
    write_pdf(OUT_MD, OUT_PDF)
    print(f"Wrote {OUT_MD} and {OUT_PDF}")


if __name__ == "__main__":
    main()
