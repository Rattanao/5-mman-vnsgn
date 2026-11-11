# MMAN VN — ตัด B/L + Change Status

ตัดไฟล์ MMAN EDI (`MMAN_*.txt`) ให้เหลือเฉพาะ B/L ที่ต้องการ แล้วทำ Change status ต่อในขั้นตอนเดียว
ได้ไฟล์ชื่อตาม POD: `MMAN_LCH.txt` / `MMAN_BKK.txt` / `MMAN_UCT.txt`

ใช้ได้ 4 แบบ: หน้าเว็บ, ดับเบิลคลิก `run-mman.bat`, คำสั่ง Python, หรือ skill ของ Claude

คู่มือแบบทีละขั้น: <https://rattanao.github.io/5-mman-vnsgn/guide.html>

(รวมทุกอย่างจากเว็บเก่า Change-status-mman ไว้ที่นี่แล้ว: SHED 2 ช่อง, ทำ Change status อย่างเดียวโดยไม่ตัด, ไฟล์ .bat, คู่มือ)

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
| POD | col 41-50 | เลือก POD: `THLCH` / `THBKK` = ทำตามข้อ 2-3 (ล็อคไว้) · `THUCT` = ทุก B/L เป็น `THUCTTHUCT` (ไฟล์มาเป็น THBKK) และ SHED `0113` |
| 4 | col 51-54 | Shed ตามท่าต้นฉบับ (col 46-50): BMT `0110` · SCT `0302` · LKR `0332` · UCT `0113` · THLCH ที่เป็น DG (มี UN/CLASS) `2826` · THBKK ที่ไป LAOS `0124` · ที่เหลือตามช่อง SHED NO.: ช่องซ้าย = B/L ที่มี Status, ช่องขวา = B/L อื่น (ว่าง = ใช้ช่องซ้าย) · ค่าตาม POD: THLCH `2813` · THBKK `0145` / `0122` |
| 5 | col 844-845 | อักษร 2 ตัวแรกของ POL เช่น `VN` (แทน `TH`) |
| 6 | บรรทัดตู้ col 18-21 | Status จากไฟล์รายการ เช่น `8  N` → `9  N` (ว่าง = คงเดิม) |
| – | หน่วยหีบห่อ | `PG` → `PX` ทุก B/L |
| 7 | col 881, 974, 1765 | ชื่อ consignee และชื่อ notify = ตามชื่อ notify ที่ col 1672 (TH+ชื่อ) เสมอ เว้นวรรค 1 เคาะเท่านั้น ทุก B/L · ที่อยู่ต่อท้ายชื่อคงไว้ · ยกเว้น B/L TRANSIT/TRANSHIPMENT ห้ามแก้ คงเดิม |
| 8 | col 1670-1671 | B/L TRANSIT/TRANSHIPMENT (รวม "INTRANSIT"): `TH` หน้าชื่อ notify = ประเทศปลายทาง `LA` LAO · `MM` MYANMAR · `KH` CAMBODIA · `CN` CHINA · `PG` PAPUA NEW GUINEA · `MY` MALAYSIA (ดูจากที่อยู่ consignee ก่อน แล้วจึงดูจาก description) |
| 9 | col 3804 (ตัวอักษรหน้า description) | B/L ที่ Status `9  N` = `5` · B/L อื่น `O` คงเดิม · TRANSIT = `7` · TRANSIT ไป LAOS = ตาม `CARGO MOVEMENT = L` หรือ `7` ใน MMAN (ไม่มี = `7`) · TRANSHIPMENT = `3` |
| 10 | col 1742-1754, 1416-1669, 2207-2460 | ทุก B/L ยกเว้น TRANSIT/TRANSHIPMENT: ลบเลขภาษี notify, ที่อยู่ consignee และที่อยู่ notify (เลขภาษี consignee และรหัสสาขาคงไว้) |

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
4. เลือก **POD** (THLCH / THBKK ทำแบบเดิม · THUCT สำหรับงานเข้า UCT) แล้วตรวจ **SHED NO.** 2 ช่อง: ซ้าย = B/L ที่มี Status, ขวา = B/L อื่น (ว่าง = ใช้ช่องซ้าย)
   เลือก POD แล้วใส่ค่าให้เอง: THLCH `2813` · THBKK `0145` / `0122` (แก้ได้) ท่าที่ล็อคไว้ในตารางข้อ 4 ใส่อัตโนมัติ
5. กด **ตัด + Change status** ตรวจผลในตาราง แล้วกด **ดาวน์โหลด** (ชื่อไฟล์ตาม POD เช่น `MMAN_UCT.txt`)

ประมวลผลในเบราว์เซอร์ทั้งหมด ไม่มีการอัปโหลดไฟล์ไปที่ใด

## วิธีใช้ 2: ดับเบิลคลิก `run-mman.bat` (Windows)

1. ติดตั้ง Python 3 ครั้งแรก (ติ๊ก **Add python.exe to PATH**) แล้วดาวน์โหลด ZIP ของ repo นี้มาแตกไฟล์
2. วางไฟล์ MMAN 1 ไฟล์ + รายการ STATUS 1 ไฟล์ใน `input\`
3. ดับเบิลคลิก `run-mman.bat` แล้วตอบคำถาม (กด Enter ข้ามได้ทุกข้อ): เริ่มต้นเก็บ B/L, ถึง B/L, POD, SHED NO. B/L ที่มี Status, SHED NO. B/L อื่น (`=` = ใช้ค่าเดียวกับข้างบน)
4. ได้ผลที่ `output\MMAN_<POD>.txt` · ครั้งแรกโปรแกรมติดตั้ง pandas, xlrd, openpyxl ให้เอง (ต้องต่ออินเทอร์เน็ต)

## วิธีใช้ 3: คำสั่ง Python

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
└─ output/          ← ได้ MMAN_<POD>.txt ที่นี่ (เช่น MMAN_LCH.txt)
```

รันในโฟลเดอร์ `5-mman-vnsgn` โดยเปลี่ยนเลข B/L เป็นตัวที่ต้องการ

ไม่ตัด ทำ Change status อย่างเดียว (แทนเว็บเก่า Change-status-mman):

```bash
python mman_vn.py --pod THBKK
```

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
| `-o ชื่อไฟล์.txt` | เปลี่ยนชื่อไฟล์ผลลัพธ์ (ค่าเริ่มต้นตาม POD: `MMAN_LCH.txt`, `MMAN_BKK.txt`, `MMAN_UCT.txt`; ไม่ใส่ `--pod` = `MMAN_LCH.txt`) |
| `--pod THUCT` | งานเข้า THUCT: ทุก B/L เป็น `THUCTTHUCT` และ SHED `0113` (ไม่ใส่ = THLCH/THBKK แบบเดิม) |
| `--shed-yes 0145` | SHED NO. ของ B/L ที่มี Status (ค่าเริ่มต้นตาม POD: THBKK `0145`, อื่นๆ `2813`) |
| `--shed-no 0122` | SHED NO. ของ B/L อื่น (ค่าเริ่มต้นตาม POD: THBKK `0122`, อื่นๆ `2813`; `=` = เท่ากับ `--shed-yes`) |
| `--shed 2813` | SHED NO. เดียวกันทุก B/L |
| `--ask` | ถามช่วง B/L, POD และ SHED บนหน้าจอ (ที่ `run-mman.bat` ใช้) |

โปรแกรมจะหยุดพร้อม `ERROR` ถ้าไม่พบ B/L ที่ระบุ, ไม่มี B/L ใดในไฟล์ MMAN ตรงกับรายการ (รายการคนละลำเรือ) หรือใน `input/` มีไฟล์ MMAN / ไฟล์รายการมากกว่า 1 ไฟล์
และแสดง `WARNING` ถ้ามี B/L ที่ไม่อยู่ในรายการ, ไม่มี POL หรือตำแหน่งคอลัมน์ผิดปกติ

## วิธีใช้ 4: Skill ของ Claude

คัดลอกโฟลเดอร์ `skill/mman-vn` ไปไว้ที่ `~/.claude/skills/mman-vn`
แล้วคัดลอก `mman_vn.py` กับ `change_status.py` ไปไว้ใน `~/.claude/skills/mman-vn/scripts/`

จากนั้นวางไฟล์ใน `input/` แล้วสั่ง Claude เช่น

> ทำ mman vn เริ่มต้นเก็บ BL HASLS21260801066 ถึง BL HASLS21260801762

หรือ "Change status POD THBKK" (ไม่ตัด) · skill นี้ใช้แทน skill `change-status` เดิมได้

## ไฟล์ใน repo

| ไฟล์ | หน้าที่ |
|---|---|
| `index.html` | หน้าเว็บ (GitHub Pages) |
| `guide.html` | คู่มือการใช้งาน (ภาษาไทย) |
| `run-mman.bat` | ดับเบิลคลิกเพื่อรันบน Windows |
| `requirements.txt` | ไลบรารีที่ต้องใช้ (pandas, xlrd, openpyxl) |
| `mman_vn.py` | คำสั่งตัด + Change status |
| `change_status.py` | กฎ Change status (ถูกเรียกโดย `mman_vn.py`; รันเดี่ยวได้ `python change_status.py <โฟลเดอร์>` → `output/MMAN_EDI.txt`) |
| `skill/mman-vn/SKILL.md` | Skill ของ Claude |

โฟลเดอร์ `input/` และ `output/` เป็นข้อมูลจริง ถูกกันไว้ใน `.gitignore` ไม่ขึ้น GitHub
