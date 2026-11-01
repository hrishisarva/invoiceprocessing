# ap-mock-api: mock AP API and ERP PO screen

One small Python service (standard library only) for Labs 3 and 4. It loads `seed.json` at startup and keeps posted invoices in memory, so a restart resets the lab.

| Path | Used in | What it does |
| --- | --- | --- |
| `GET /health` | Lab 3 | Returns `{"ok":true,"service":"ap-mock-api"}` |
| `POST /api/invoice-validate` | Lab 3 | Vendor, duplicate and PO checks (see `sampleinvoicevalidate.md` in the Lab 3 zip) |
| `GET /erp/` | Lab 4 | ERP main menu |
| `GET /erp/po` | Lab 4 | PO search (`#poNumber`, `#search`, result link `#poLink`) |
| `GET /erp/po/{poNumber}` | Lab 4 | PO header, lines table `#poLines`, `#postInvoice` button |
| `POST /erp/po/{poNumber}/post` | Lab 4 | Posts an invoice (`#invoiceNumber`, `#confirmPost`); shows `#postedMessage` |

## Run locally

    python3 app.py            # listens on http://localhost:10000
    curl http://localhost:10000/health

## Build and publish the image (for Render)

    docker build --platform linux/amd64 -t <dockerhub-user>/ap-mock-api:1.0 .
    docker run --rm -p 10000:10000 <dockerhub-user>/ap-mock-api:1.0
    docker login
    docker push <dockerhub-user>/ap-mock-api:1.0

Render requires `linux/amd64` images; keep the `--platform` flag on Apple Silicon Macs.

## Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `10000` | Port to listen on; Render sets this automatically |
| `SEARCH_DELAY_SECONDS` | `0.3` | Artificial delay on PO search so robots learn to wait |
