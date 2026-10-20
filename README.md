# MMAN VN — ตัด B/L + Change Status

ตัดไฟล์ MMAN EDI (`MMAN_*.txt`) ให้เหลือเฉพาะ B/L ที่ต้องการ แล้วทำ Change status ต่อในขั้นตอนเดียว
ได้ไฟล์ `MMAN_LCH.txt` (แบบฟอร์มสำหรับงาน THLCH)

ใช้ได้ 3 แบบ: หน้าเว็บ, คำสั่ง Python, หรือ skill ของ Claude

## สิ่งที่โปรแกรมทำ

**ขั้นที่ 1 ตัด**

- เก็บบรรทัดแรก (`PSKV…`) ไว้เสมอ
- เก็บเฉพาะตั้งแต่ **เริ่มต้นเก็บ B/L** (เช่น `HASLS21260801066`) **ถึง B/L** (เช่น `HASLS21260801762`)
  โดยรวม sub-B/L (`…762A`, `…762B`) และบรรทัดตู้ของ B/L สุดท้ายด้วย
- บรรทัดก่อนและหลังช่วงนี้ตัดออกทั้งหมด
- เว้นว่าง "เริ่มต้นเก็บ B/L" = ตั้งแต่ B/L แรก · เว้นว่าง "ถึง B/L" = ถึงบรรทัดสุดท้าย

**ขั้นที่ 2 Change status** (กับ B/L ที่เหลือ)

| # | ตำแหน่ง (นับจาก 1) | ค่าที่ใส่ |
|---|---|---|
| 1 | col 36-40 | POL จากไฟล์รายการ เช่น `VNSGN` |
| 2 | col 41-45 | ท่าเรือของ B/L ส่วนใหญ่ในไฟล์ เช่น `THBKK`, `THLCH` |
| 3 | col 46-50 | ท่าเรือตามต้นฉบับ (`THLCH`, `THLKR`, …) คงเดิม ห้ามแก้ |
| 4 | col 51-54 | Shed ตามท่าต้นฉบับ (col 46-50): BMT `0110` · SCT `0302` · LKR `0332` · UCT `0113` · THLCH ที่เป็น DG (มี UN/CLASS) `2826` · ที่เหลือตามช่อง SHED NO. (ค่าเริ่มต้น `2813`) |
| 5 | col 844-845 | อักษร 2 ตัวแรกของ POL เช่น `VN` (แทน `TH`) |
| 6 | บรรทัดตู้ col 18-21 | Status จากไฟล์รายการ เช่น `8  N` → `9  N` (ว่าง = คงเดิม) |
| – | หน่วยหีบห่อ | `PG` → `PX` ทุก B/L |
| 7 | col 881, 974, 1672 | ชื่อ consignee และชื่อ notify = ชื่อที่ col 1765 เว้นวรรค 1 เคาะเท่านั้น (ยกเว้น B/L TRANSIT/TRANSHIPMENT หรือชื่อ consignee ไม่ตรงกับ notify → คงเดิม) |
| 8 | col 1670-1671 | B/L TRANSIT/TRANSHIPMENT (รวม "INTRANSIT"): `TH` หน้าชื่อ notify = ประเทศปลายทาง `LA` LAO · `MM` MYANMAR · `KH` CAMBODIA · `CN` CHINA · `PG` PAPUA NEW GUINEA · `MY` MALAYSIA (ดูจากที่อยู่ consignee ก่อน แล้วจึงดูจาก description) |
| 9 | col 3804 (ตัวอักษรหน้า description) | B/L อื่น `O` คงเดิม · TRANSIT = `7` · TRANSIT ไป LAOS = ตาม `CARGO MOVEMENT = L` หรือ `7` ใน MMAN (ไม่มี = `7`) · TRANSHIPMENT = `3` |

ความยาวบรรทัดและการขึ้นบรรทัด (CRLF) คงเดิมทุกไบต์ ไฟล์ต้นฉบับไม่ถูกแก้ไข

## ไฟล์ที่ต้องเตรียม

1. **MMAN** — `MMAN_*.txt` 1 ไฟล์
2. **รายการ Status** — `.xls` / `.xlsx` / `.csv` 1 ไฟล์ ใช้เฉพาะคอลัมน์ A-C ซึ่งต้องมีหัวคอลัมน์
   `B/L No.`, `Status`, `POL` (เรียงลำดับใดก็ได้ เช่น `SUR.xls` = POL, Status, B/L No.)
   - B/L No. ใส่เลขหลัก เช่น `HASLS21260801066` จะครอบคลุม sub-B/L (`…066A`, `…066B`) ด้วย
   - Status เช่น `9  N`, `7  N` · เว้นว่าง = คง Status เดิม
3. **เริ่มต้นเก็บ B/L / ถึง B/L** — เลข B/L แรกและ B/L สุดท้ายที่ต้องการให้เหลือในไฟล์

## วิธีใช้ 1: หน้าเว็บ

เปิด <https://rattanao.github.io/5-mman-vnsgn/>

1. เลือกไฟล์ MMAN (.txt)
2. เลือกไฟล์ STATUS (.xls / .xlsx / .csv)
3. พิมพ์ **เริ่มต้นเก็บ B/L** และ **ถึง B/L** (เว้นว่างทั้งสองช่อง = ไม่ตัด ทำ Change status อย่างเดียว)
4. ใส่ SHED NO. (ค่าเริ่มต้น 2813) ใช้กับ THLCH ที่ไม่ใช่ DG ท่าอื่นใส่ตามตารางข้อ 4 อัตโนมัติ
5. กด **ตัด + Change status** ตรวจผลในตาราง แล้วกด **ดาวน์โหลด MMAN_LCH.txt**

ประมวลผลในเบราว์เซอร์ทั้งหมด ไม่มีการอัปโหลดไฟล์ไปที่ใด

## วิธีใช้ 2: คำสั่ง Python

ติดตั้งครั้งแรก:

```bash
pip install pandas xlrd openpyxl
```

วางไฟล์ตามนี้:

```
5-mman-vnsgn/
├─ mman_vn.py
├─ change_status.py
├─ input/
│  ├─ MMAN__00PSKV....txt
│  └─ SUR.xls
└─ output/          ← ได้ MMAN_LCH.txt ที่นี่
```

รันในโฟลเดอร์ `5-mman-vnsgn` โดยเปลี่ยนเลข B/L เป็นตัวที่ต้องการ

เก็บตั้งแต่ B/L นี้ถึงบรรทัดสุดท้าย:

```bash
python mman_vn.py HASLS21260801066
```

เก็บตั้งแต่ B/L นี้ ถึง B/L นี้:

```bash
python mman_vn.py HASLS21260801066 --to HASLS21260801762
```

ตัวเลือกเพิ่มเติม:

| ตัวเลือก | ความหมาย |
|---|---|
| `python mman_vn.py <B/L> <โฟลเดอร์>` | ระบุโฟลเดอร์งานอื่นที่มี `input/` |
| `-o ชื่อไฟล์.txt` | เปลี่ยนชื่อไฟล์ผลลัพธ์ (ค่าเริ่มต้น `MMAN_LCH.txt`) |
| `--shed 2813` | Shed ของ THLCH ที่ไม่ใช่ DG (ค่าเริ่มต้น 2813) |

โปรแกรมจะหยุดพร้อม `ERROR` ถ้าไม่พบ B/L ที่ระบุ หรือใน `input/` มีไฟล์ MMAN / ไฟล์รายการมากกว่า 1 ไฟล์
และแสดง `WARNING` ถ้ามี B/L ที่ไม่อยู่ในรายการ, ไม่มี POL หรือตำแหน่งคอลัมน์ผิดปกติ

## วิธีใช้ 3: Skill ของ Claude

คัดลอกโฟลเดอร์ `skill/mman-vn` ไปไว้ที่ `~/.claude/skills/mman-vn`
แล้วคัดลอก `mman_vn.py` กับ `change_status.py` ไปไว้ใน `~/.claude/skills/mman-vn/scripts/`

จากนั้นวางไฟล์ใน `input/` แล้วสั่ง Claude เช่น

> ทำ mman vn เริ่มต้นเก็บ BL HASLS21260801066 ถึง BL HASLS21260801762

## ไฟล์ใน repo

| ไฟล์ | หน้าที่ |
|---|---|
| `index.html` | หน้าเว็บ (GitHub Pages) |
| `mman_vn.py` | คำสั่งตัด + Change status |
| `change_status.py` | กฎ Change status (ถูกเรียกโดย `mman_vn.py`) |
| `skill/mman-vn/SKILL.md` | Skill ของ Claude |

โฟลเดอร์ `input/` และ `output/` เป็นข้อมูลจริง ถูกกันไว้ใน `.gitignore` ไม่ขึ้น GitHub
