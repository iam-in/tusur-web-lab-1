from pathlib import Path
import sys

from pypdf import PdfReader


def repair_mojibake(text: str) -> str:
    try:
        return text.encode("cp1251", errors="replace").decode("utf-8", errors="replace")
    except UnicodeError:
        return text


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: extract_pdf.py <input.pdf> <output.txt>", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    reader = PdfReader(str(source))

    lines: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = repair_mojibake(page.extract_text() or "")
        lines.append(f"\n\n--- PAGE {index} ---\n")
        lines.append(text)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Extracted {len(reader.pages)} pages to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


