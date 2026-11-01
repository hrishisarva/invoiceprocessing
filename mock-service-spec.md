# Mock service specification

One small web service, deployed to Render's free tier from a Docker Hub image, serves both the API (Lab 3) and the ERP screen (Lab 4). Load all data from `seed.json` at startup and keep posted invoices in memory; a restart resets the lab.

## API

| Method | Path | Behaviour |
| --- | --- | --- |
| GET | `/health` | `{"ok":true,"service":"ap-mock-api"}` |
| POST | `/api/invoice-validate` | Body `{vendorId, invoiceNumber, poNumber, total}`. `vendorActive`: vendor exists and status is ACTIVE. `duplicate`: invoiceHistory has the same vendorId and invoiceNumber. `poOpen`: PO exists, belongs to the vendor, status OPEN. `valid` = all three. `reasons`: one string per failed check. 400 on missing or mistyped fields |

PO lines are not exposed by the API, on purpose: they appear only on the ERP screen.

## ERP screen (plain server-rendered HTML, stable ids for selectors)

| Path | Content |
| --- | --- |
| `/erp/` | Menu with a **Purchase Orders** link |
| `/erp/po` | **PO Number** input (`id="poNumber"`), **Search** button (`id="search"`), one result row linking to the PO |
| `/erp/po/{poNumber}` | Header: PO number, vendor name, currency, status. Lines table (`id="poLines"`) with Line, Description, Ordered Quantity, Unit Price, Line Amount. **Post Invoice** button (`id="postInvoice"`) |
| Post dialog | **Invoice Number** input (`id="invoiceNumber"`) and **Confirm** (`id="confirmPost"`); shows `Invoice <number> posted` and lists posted invoices under the PO |

Disable Post Invoice on CLOSED POs. Add a short artificial delay (300 ms) on search to make the robot wait correctly.
