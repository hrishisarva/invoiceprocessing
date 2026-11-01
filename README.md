# Facilitator kit — Invoice Processing with 2-Way Match

> All vendors, people, amounts and IDs in this pack are synthetic and exist only for training.

| File | Purpose |
| --- | --- |
| `seed.json` | Vendors, purchase orders, paid-invoice history, the 10 invoices, tolerance and FX rate. One source for the mock API and the ERP screen |
| `mock/` | The ready-to-deploy service: `app.py`, `Dockerfile`, `seed.json` and a README with build and push commands |
| `mock-service-spec.md` | What the mock AP API and ERP screen must do |
| `generator/seed.py`, `generator/render.py` | Regenerate the invoice PDFs (Python 3, reportlab, Pillow, poppler) |

## Expected results across the labs

| # | Invoice | Vendor | Total | Scenario | Lab 3 Invoice Valid | Lab 4 Within Tolerance | Lab 5 result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | INV-NW-20417 | Northwind Office Supply Co. | $3,511.63 | Clean match | Yes | Yes - posted | AUTO_POSTED |
| 2 | BMS-77821 | Bluepeak Medical Supplies Inc. | $2,157.50 | Price variance inside tolerance (gloves +$0.20/box, $20 on the line) | Yes | Yes - posted | AUTO_POSTED |
| 3 | IC-3391 | Ironclad Components LLC | $5,778.00 | Price variance over tolerance (+$60/unit, 12.5%, $600 on the line) | Yes | No | PRICE_VARIANCE / DISPUTE |
| 4 | RFS-10882 | Relay Field Services Ltd. | $9,275.00 | Quantity billed above PO (25 sites vs 20 ordered) | Yes | No | QUANTITY_VARIANCE / DISPUTE + vendor query |
| 5 | CPS-2026-0918 | Civic Print & Signage | $2,073.60 | Duplicate invoice number (already paid 2026-09-30) | No | - | STOP_RETURNED |
| 6 | HL-55102 | Halden Logistics GmbH | $1,680.00 | Inactive vendor (scanned-style image PDF) | No | - | STOP_RETURNED |
| 7 | LIT-9034 | Lumen IT Services | $2,400.00 | Closed PO | No | - | STOP_RETURNED |
| 8 | LIT-9041 | Lumen IT Services | $2,210.00 | Total miscalculated (2,000 + 160 printed as 2,210) | Yes | No (totals check) | TAX_ERROR / DISPUTE |
| 9 | AP-2026-0412 | Adler Precision Tools GmbH | EUR 4,000.00 | EUR invoice against a USD PO (ECB rate 3 Aug 2026: 1.1535) | Yes | Yes with FX stretch / No without | AUTO_POSTED with stretch; PRICE_VARIANCE without |
| 10 | IC-3402 | Ironclad Components LLC | $652.70 | IXP traps: Order No. beside Invoice No.; 'Total excl. tax' shown above amount due | Yes | Yes - posted | AUTO_POSTED |
# invoiceprocessing
