"""Mock AP API + legacy ERP PO screen for the invoice 2-way match bootcamp.
Standard library only. Data comes from seed.json; posted invoices live in memory
(a restart resets the lab)."""
import json, os, re, time, html, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = json.load(open(os.path.join(HERE, "seed.json")))
VENDORS = {v["vendorId"]: v for v in SEED["vendors"]}
POS = {p["poNumber"]: p for p in SEED["purchaseOrders"]}
HISTORY = SEED["invoiceHistory"]
POSTED = {}          # poNumber -> list of {"invoiceNumber", "postedAt"}
LOCK = threading.Lock()
SEARCH_DELAY = float(os.environ.get("SEARCH_DELAY_SECONDS", "0.3"))

def validate(body):
    for f in ("vendorId", "invoiceNumber", "poNumber"):
        if not isinstance(body.get(f), str) or not body[f].strip():
            return 400, {"error": f"{f} is required and must be a non-empty string"}
    t = body.get("total")
    if isinstance(t, bool) or not isinstance(t, (int, float)):
        return 400, {"error": "total must be a number"}
    vid, inv, pon = body["vendorId"].strip(), body["invoiceNumber"].strip(), body["poNumber"].strip()
    reasons = []
    v = VENDORS.get(vid)
    if not v: reasons.append(f"Vendor {vid} not found")
    elif v["status"] != "ACTIVE": reasons.append(f"Vendor {vid} is inactive")
    vendor_active = bool(v) and v["status"] == "ACTIVE"
    dup = next((h for h in HISTORY if h["vendorId"] == vid and h["invoiceNumber"] == inv), None)
    if dup: reasons.append(f"Invoice {inv} from {vid} was already paid on {dup['paidOn']}")
    po = POS.get(pon)
    if not po: reasons.append(f"PO {pon} not found")
    elif po["vendorId"] != vid: reasons.append(f"PO {pon} belongs to vendor {po['vendorId']}")
    elif po["status"] != "OPEN": reasons.append(f"PO {pon} is closed")
    po_open = bool(po) and po["vendorId"] == vid and po["status"] == "OPEN"
    return 200, {"valid": vendor_active and not dup and po_open, "vendorActive": vendor_active,
                 "duplicate": bool(dup), "poOpen": po_open, "reasons": reasons}

CSS = """body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#eef1f5;color:#1f2933}
header{background:#2f4858;color:#fff;padding:10px 24px;font-size:18px}header a{color:#fff;text-decoration:none}
main{padding:24px;max-width:960px}table{border-collapse:collapse;background:#fff;width:100%;margin:12px 0}
th,td{border:1px solid #c5ccd6;padding:6px 10px;text-align:left;font-size:14px}th{background:#dde3ea}
td.num{text-align:right}.box{background:#fff;border:1px solid #c5ccd6;padding:16px;margin-bottom:16px}
label{display:inline-block;width:120px}button{padding:6px 14px;font-size:14px}
.msg{background:#e3f4e8;border:1px solid #8cc7a0;padding:8px 12px;margin-bottom:12px}
.warn{background:#fdf1e1;border:1px solid #e3b26b;padding:8px 12px;margin-bottom:12px}"""

def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)} - Meridian ERP</title>
<style>{CSS}</style></head><body><header><a href="/erp/">Meridian ERP 7.2</a> &nbsp;|&nbsp; Accounts Payable</header>
<main><h2 id="pageTitle">{html.escape(title)}</h2>{body}</main></body></html>"""

def money(x): return f"{x:,.2f}"

def erp_home():
    return page("Main menu", '<div class="box"><ul><li><a id="menuPurchaseOrders" href="/erp/po">Purchase Orders</a></li>'
                '<li><span style="color:#8a94a3">Vendors (read only)</span></li><li><span style="color:#8a94a3">Reports</span></li></ul></div>')

def erp_search(q):
    form = ('<div class="box"><form method="get" action="/erp/po"><label for="poNumber">PO Number</label>'
            f'<input id="poNumber" name="poNumber" value="{html.escape(q or "")}"> <button id="search" type="submit">Search</button></form></div>')
    if q is None: return page("Purchase Orders", form)
    time.sleep(SEARCH_DELAY)
    po = POS.get(q.strip().upper())
    if not po:
        return page("Purchase Orders", form + f'<div class="warn" id="noResults">No purchase order found for {html.escape(q)}</div>')
    v = VENDORS[po["vendorId"]]
    rows = (f'<table id="searchResults"><tr><th>PO Number</th><th>Vendor</th><th>Currency</th><th>Status</th></tr>'
            f'<tr><td><a id="poLink" href="/erp/po/{po["poNumber"]}">{po["poNumber"]}</a></td><td>{html.escape(v["name"])}</td>'
            f'<td>{po["currency"]}</td><td>{po["status"]}</td></tr></table>')
    return page("Purchase Orders", form + rows)

def erp_detail(pon, posted_msg):
    po = POS.get(pon)
    if not po: return None
    v = VENDORS[po["vendorId"]]
    msg = f'<div class="msg" id="postedMessage">Invoice {html.escape(posted_msg)} posted</div>' if posted_msg else ""
    head = (f'<div class="box" id="poHeader"><div><label>PO Number</label><span id="poNumberValue">{po["poNumber"]}</span></div>'
            f'<div><label>Vendor</label><span id="vendorName">{html.escape(v["name"])}</span> (<span id="vendorId">{v["vendorId"]}</span>)</div>'
            f'<div><label>Currency</label><span id="poCurrency">{po["currency"]}</span></div>'
            f'<div><label>Status</label><span id="poStatus">{po["status"]}</span></div></div>')
    lines = "".join(f'<tr><td>{l["line"]}</td><td>{html.escape(l["description"])}</td><td class="num">{l["orderedQty"]}</td>'
                    f'<td class="num">{money(l["unitPrice"])}</td><td class="num">{money(l["orderedQty"]*l["unitPrice"])}</td></tr>' for l in po["lines"])
    table = ('<table id="poLines"><tr><th>Line</th><th>Description</th><th>Ordered Quantity</th><th>Unit Price</th><th>Line Amount</th></tr>'
             f'{lines}</table>')
    disabled = "" if po["status"] == "OPEN" else " disabled"
    post = (f'<button id="postInvoice" type="button"{disabled}>Post Invoice</button>'
            f'<dialog id="postDialog"><form method="post" action="/erp/po/{po["poNumber"]}/post">'
            '<p><label for="invoiceNumber">Invoice Number</label><input id="invoiceNumber" name="invoiceNumber" required></p>'
            '<button id="confirmPost" type="submit">Confirm</button> <button id="cancelPost" type="button">Cancel</button></form></dialog>'
            '<script>const d=document.getElementById("postDialog");document.getElementById("postInvoice").onclick=()=>d.showModal();'
            'document.getElementById("cancelPost").onclick=()=>d.close();</script>')
    with LOCK: plist = list(POSTED.get(po["poNumber"], []))
    hist = ""
    if plist:
        hist = '<h3>Posted invoices</h3><table id="postedInvoices"><tr><th>Invoice Number</th><th>Posted at (UTC)</th></tr>' + "".join(
            f'<tr><td>{html.escape(p["invoiceNumber"])}</td><td>{p["postedAt"]}</td></tr>' for p in plist[-20:]) + "</table>"
    return page(f'Purchase Order {po["poNumber"]}', msg + head + table + post + hist)

class H(BaseHTTPRequestHandler):
    server_version = "MeridianERP/7.2"
    def send(self, code, body, ctype="application/json", extra=None):
        data = (json.dumps(body, separators=(",", ":")) if ctype == "application/json" else body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        u = urlparse(self.path); p = u.path.rstrip("/") or "/"
        q = parse_qs(u.query)
        if p == "/health": return self.send(200, {"ok": True, "service": "ap-mock-api"})
        if p == "/": return self.send(302, "", "text/plain", {"Location": "/erp/"})
        if p == "/erp": return self.send(200, erp_home(), "text/html")
        if p == "/erp/po": return self.send(200, erp_search(q.get("poNumber", [None])[0]), "text/html")
        m = re.fullmatch(r"/erp/po/([A-Za-z0-9-]+)", p)
        if m:
            body = erp_detail(m.group(1).upper(), q.get("posted", [None])[0])
            return self.send(200, body, "text/html") if body else self.send(404, page("Not found", "<p>No such purchase order.</p>"), "text/html")
        return self.send(404, {"error": "not found"})
    def do_POST(self):
        u = urlparse(self.path); p = u.path.rstrip("/")
        n = int(self.headers.get("Content-Length") or 0); raw = self.rfile.read(n) if n else b""
        if p == "/api/invoice-validate":
            try: body = json.loads(raw or b"{}")
            except ValueError: return self.send(400, {"error": "body must be valid JSON"})
            if not isinstance(body, dict): return self.send(400, {"error": "body must be a JSON object"})
            code, out = validate(body); return self.send(code, out)
        m = re.fullmatch(r"/erp/po/([A-Za-z0-9-]+)/post", p)
        if m:
            pon = m.group(1).upper(); po = POS.get(pon)
            inv = (parse_qs(raw.decode()).get("invoiceNumber", [""])[0]).strip()
            if not po or po["status"] != "OPEN" or not inv:
                return self.send(400, page("Cannot post", "<div class='warn' id='postError'>PO is closed or the invoice number is empty.</div>"), "text/html")
            with LOCK:
                lst = POSTED.setdefault(pon, [])
                if not any(x["invoiceNumber"] == inv for x in lst):
                    lst.append({"invoiceNumber": inv, "postedAt": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())})
            from urllib.parse import quote
            return self.send(303, "", "text/plain", {"Location": f"/erp/po/{pon}?posted={quote(inv)}"})
        return self.send(404, {"error": "not found"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    print(f"ap-mock-api listening on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
