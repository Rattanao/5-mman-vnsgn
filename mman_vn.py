"""MMAN VN: cut + Change status in one step.

    python mman_vn.py <first B/L to keep> [folder] [-o name] [--shed-yes 0145] [--shed-no 0122]

Keeps the PSKV header line, drops every line after it up to (not including) the
given B/L, keeps the rest, then applies Change status (change_status.py, next to
this file) with the list file in <folder>/input.
Result: <folder>/output/MMAN_VN.txt. The source files are never modified.
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from change_status import change_status  # noqa: E402

RESULTS = {"mman_vn.txt", "mman_edi.txt"}


def find_one(folder: Path, patterns, what) -> Path:
    hits = sorted({h for p in patterns for h in folder.glob(p) if h.name.lower() not in RESULTS})
    if len(hits) != 1:
        sys.exit(f"ERROR: need exactly 1 {what} in {folder}, found {len(hits)}: {[h.name for h in hits]}")
    return hits[0]


def cut(raw: bytes, bl: str):
    """PSKV line + everything from the B/L line to the end. Bytes are kept as-is (CRLF safe)."""
    lines = raw.splitlines(keepends=True)
    if not lines or not lines[0].startswith(b"PSKV"):
        sys.exit("ERROR: first line is not the PSKV header")
    key = bl.strip().upper().encode("latin-1")
    start = next((i for i, l in enumerate(lines[1:], 1) if l[:35].strip() == key), None)
    if start is None:
        sys.exit(f"ERROR: B/L {bl} not found in the MMAN file")
    return b"".join([lines[0]] + lines[start:]), start - 1, len(lines)


def main():
    ap = argparse.ArgumentParser(description="Cut + Change status -> output/MMAN_VN.txt")
    ap.add_argument("bl", help="first B/L to keep, e.g. HASLS21260801066")
    ap.add_argument("folder", nargs="?", default=".", help="folder holding input/ (default: current folder)")
    ap.add_argument("-o", default="MMAN_VN.txt")
    ap.add_argument("--shed-yes", default="0145")
    ap.add_argument("--shed-no", default="0122")
    a = ap.parse_args()

    folder = Path(a.folder).resolve()
    inp = next((d for d in (folder / "input", folder / "Input") if d.is_dir()), folder)
    mman = find_one(inp, ["MMAN_*.txt"], "MMAN_*.txt")
    lst = find_one(inp, ["*.xls", "*.xlsx", "*.csv"], "list file (.xls/.xlsx/.csv)")
    out = folder / "output" / a.o
    out.parent.mkdir(exist_ok=True)

    data, removed, total = cut(mman.read_bytes(), a.bl)
    fd, tmp = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        rep = change_status(Path(tmp), lst, out, a.shed_yes, a.shed_no)
    finally:
        os.remove(tmp)

    print(f"MMAN : {mman}\nLIST : {lst}\nOUT  : {out}")
    print(f"Cut              : removed {removed} lines ({total} -> {total - removed}), first B/L kept {a.bl.upper()}")
    print(f"B/L lines edited : {rep['bl_lines']}  (shed {a.shed_yes}: {len(rep['shed_yes'])}, "
          f"shed {a.shed_no}: {len(rep['shed_no'])})")
    print("Status set       : " + (", ".join(f"{k!r} x{v}" for k, v in rep["status_lines"].items()) or "none"))
    print(f"PG -> PX         : {rep['pg_to_px'] or 'none'}")
    print(f"Size / changed   : {rep['size']} bytes, {rep['bytes_changed']} bytes changed")
    for key, label in (("not_in_list", "B/L NOT in list (untouched)"), ("no_pol", "B/L without POL"),
                       ("layout_warn", "Layout warning (check columns)")):
        if rep[key]:
            print(f"WARNING {label}: {rep[key]}")


if __name__ == "__main__":
    main()
