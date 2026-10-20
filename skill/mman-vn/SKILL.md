---
name: mman-vn
description: "MMAN VN" for a Thailand import MMAN EDI manifest (fixed-width MMAN_*.txt). In one step it (1) keeps the PSKV header line, keeps only the B/L range the user names, "เริ่มต้นเก็บ B/L … ถึง B/L …" (e.g. HASLS21260801066 to HASLS21260801762, with the last B/L's sub-B/Ls; no end B/L = to the last line), cutting everything before and after, then (2) applies Change status from a B/L list (.xls/.xlsx/.csv with B/L No., Status, POL): POL + port of discharge (the port most B/Ls have; THLKR and other original ports stay), consignee/notify names taken from the notify name+address field (col 1764) except TRANSIT/TRANSHIPMENT B/Ls, shed by original port (BMT 0110, SCT 0302, LKR 0332, UCT 0113, THLCH DG 2826, the rest the given shed, default 2813), consignee names with single spaces only, POL country code in place of TH, new container status (e.g. 8  N -> 9  N), PG -> PX. Writes output/MMAN_LCH.txt. Use whenever the user says "mman vn", "ตัดและ change status", "ตัด MMAN ตั้งแต่ BL ...", "ทำ mman_vn", or points to a folder with input/ holding an MMAN_*.txt plus a status list and names a starting B/L.
---

# MMAN LCH (ตัด + Change status → output/MMAN_LCH.txt)

Rattana's confirmed format. Run the bundled script; don't edit the file by hand. The file is
fixed-width, latin-1 and CRLF. Never change line lengths or line endings (sed in Git Bash once
broke CRLF).

## Input

- A folder with `input/` (or `Input/`) containing **1** `MMAN_*.txt` + **1** list file (`.xls`, `.xlsx`, `.csv`)
- The **first B/L to keep** ("เริ่มต้นเก็บ B/L", e.g. `HASLS21260801066`) and optionally the
  **last B/L to keep** ("ถึง B/L", e.g. `HASLS21260801762`). If the user gave no B/L, ask. Don't
  guess. No end B/L = keep through the last line.
- List file: only columns A-C are used, found **by header name** (B/L No., Status, POL in any
  order, e.g. `SUR.xls` = POL, Status, B/L No.). Status blank = keep the original status.
- If the list is a **PDF**, extract columns A-C into a CSV with the header `B/L No.,Status,POL`
  (keep the spacing in Status, e.g. `9  N`) and put that CSV in `input/` instead.

## What the script does

1. **Cut**: keep line 1 (`PSKV…`) plus the lines from the first B/L through the last B/L,
   including the last B/L's sub-B/Ls (`…762A`, `…762B`) and their container lines. Everything
   before and after is removed. Bytes are copied as-is.
2. **Change status** on the remaining B/Ls (0-based columns on each `HASL…` line):

| # | Position | Value |
|---|---|---|
| 1 | col 35-39 | POL (from the list) |
| 2 | col 40-44 | port of discharge = the port most B/Ls have in col 45-49 (e.g. THBKK, THLCH) |
| 3 | col 45-49 | port from the original (THLCH, THLKR, …), never changed |
| 4 | col 50-53 | shed by the original port in col 45-49: THBMT `0110`, THSCT `0302`, THLKR `0332`, THUCT `0113`; THLCH DG `2826` (DG = the list's DG column is filled, or the B/L line has UN xxxx / IMO / IMDG / CLASS n); everything else `--shed` (default `2813`) |
| 5 | col 843-844 | first 2 letters of POL (e.g. `VN`), replacing `TH` |
| 6 | container line col 17 | Status from the list (`8  N` → `9  N`) |
| – | package unit | `PG` → `PX` on every B/L |
| 7 | col 880 (93), 973 (696), 1671 (93) | consignee name, consignee name+address, notify name = the name at the start of col 1764 (notify name+address), taken as the words that match the consignee name, written with single spaces only. Kept when the B/L line says TRANSIT/TRANSHIPMENT, or when the consignee name is not the notify name (WARNING) |
| 8 | col 1669-1670 | TRANSIT/TRANSHIPMENT B/L (also "INTRANSIT"): the notify country `TH` becomes the destination country: LA (LAO/LAOS/VIENTIANE), MM (MYANMAR/YANGON), KH (CAMBODIA/PHNOM PENH), CN (CHINA), PG (PAPUA NEW GUINEA), MY (MALAYSIA); last mention in the consignee name+address (col 973), else first mention in the description. None found = TH kept + WARNING |
| 9 | col 3803 | the code before the description: TRANSHIPMENT `3`; TRANSIT `7`; TRANSIT to LAOS = the `CARGO MOVEMENT = L` / `7` written in the B/L (none = `7`) |

**Leave the letter `O` before the description (col 3803) unchanged on every other B/L.**

## Steps

1. Run:
   ```bash
   PYTHONIOENCODING=utf-8 python "<skill dir>/scripts/mman_vn.py" <first B/L> "<folder containing input>" [--to <last B/L>]
   ```
   (If `python` is only the Microsoft Store alias, use `py` instead.)
   The result is always `output/MMAN_LCH.txt` in that folder (`-o name` to rename). The input
   files are never modified. Requires `pandas`, `xlrd` (.xls) and `openpyxl` (.xlsx).
2. Report to the user in Thai: lines removed and the B/L range kept, how many B/Ls remain,
   the shed codes used (and DG B/Ls), how many status lines changed and to what, which B/Ls went PG→PX, file size.
3. If the script prints `ERROR` (B/L not found, more than one MMAN/list file) or `WARNING`
   (B/L not in the list, B/L without POL, unexpected layout), tell the user and ask. Don't guess.
