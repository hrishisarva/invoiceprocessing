import os, subprocess
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
import importlib.util, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    spec = importlib.util.spec_from_file_location("seed","seed.py"); seed = importlib.util.module_from_spec(spec); spec.loader.exec_module(seed)
V = {v["vendorId"]:v for v in seed.VENDORS}
BILL = ["Meridian Holdings Inc.","Accounts Payable","200 Harbor Way, Suite 400","Boston, MA 02110, USA"]
BRAND = {"V-1001":"#1F4E79","V-1002":"#0F766E","V-1003":"#7C2D12","V-1004":"#4338CA","V-1005":"#9D174D","V-1006":"#334155","V-1007":"#1D4ED8","V-1008":"#374151"}
def m(x, cur): return (f"{x:,.2f}" if cur=="USD" else f"{x:,.2f}")
def sym(cur): return "$" if cur=="USD" else "EUR "
os.makedirs("out/invoices", exist_ok=True)

def table(c, x, y, w, inv, head_fill, pos_col=False):
    cur = inv["currency"]; cols = [("Description",0.0),("Qty",0.58),("Unit Price",0.70),("Amount",0.86)]
    if pos_col: cols = [("Pos.",0.0),("Description",0.07),("Qty",0.60),("Unit price",0.71),("Amount",0.86)]
    c.setFillColor(HexColor(head_fill)); c.rect(x, y-6, w, 20, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 9.5)
    for name, fx in cols:
        if name in ("Qty","Unit Price","Unit price","Amount"): c.drawRightString(x+fx*w+ (0.11*w if name!="Qty" else 0.09*w), y, name)
        else: c.drawString(x+fx*w+6, y, name)
    c.setFillColor(black); c.setFont("Helvetica", 9.5); yy = y-24
    for i,(d,q,p) in enumerate(inv["lines"],1):
        off = 0
        if pos_col: c.drawString(x+6, yy, str(i)); off = 0.07
        c.drawString(x+off*w+6, yy, d)
        qx = (0.60 if pos_col else 0.58); c.drawRightString(x+qx*w+0.09*w, yy, f"{q:g}")
        ux = (0.71 if pos_col else 0.70); c.drawRightString(x+ux*w+0.11*w, yy, m(p,cur))
        c.drawRightString(x+0.86*w+0.11*w, yy, m(q*p,cur))
        c.setStrokeColor(HexColor("#D9DDE3")); c.line(x, yy-7, x+w, yy-7); yy -= 22
    return yy

def totals(c, xr, y, inv, labels, style):
    cur = inv["currency"]; s = sym(cur)
    rows = []
    if inv.get("exclTaxTrap"):
        rows = [("Total excl. tax", inv["subtotal"], True), (inv["taxLabel"], inv["tax"], False), (labels["total"], inv["total"], True)]
    else:
        rows = [("Subtotal", inv["subtotal"], False), (inv["taxLabel"], inv["tax"], False), (labels["total"], inv["total"], True)]
    for lab, val, bold in rows:
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if (bold and lab==labels["total"]) else 10)
        c.drawRightString(xr-110, y, lab); c.drawRightString(xr, y, s + m(val,cur)); y -= 18
    return y

def tplA(c, inv):
    W,H = letter; v = V[inv["vendorId"]]; L = inv["labels"]; col = BRAND[v["vendorId"]]
    c.setFillColor(HexColor(col)); c.setFont("Helvetica-Bold", 18); c.drawString(54, H-72, v["name"])
    c.setFillColor(black); c.setFont("Helvetica", 9.5)
    for i,a in enumerate(v["addr"]): c.drawString(54, H-90-12*i, a)
    c.setFont("Helvetica-Bold", 26); c.setFillColor(HexColor("#111827")); c.drawRightString(W-54, H-74, "INVOICE")
    meta = [(L["inv"], inv["invoiceNumber"]), (L["date"], inv["dateStr"]), (L["po"], inv["po"]), (L["vid"], inv["vendorId"]), ("Terms","Net 30")]
    y = H-104
    for k,val in meta:
        c.setFont("Helvetica", 9.5); c.setFillColor(HexColor("#4B5563")); c.drawRightString(W-160, y, k)
        c.setFont("Helvetica-Bold", 9.5); c.setFillColor(black); c.drawRightString(W-54, y, val); y -= 14
    c.setFont("Helvetica-Bold", 10); c.drawString(54, H-190, "Bill To")
    c.setFont("Helvetica", 9.5)
    for i,a in enumerate(BILL): c.drawString(54, H-205-12*i, a)
    yy = table(c, 54, H-290, W-108, inv, col)
    totals(c, W-54, yy-18, inv, L, "A")
    c.setFont("Helvetica", 8.5); c.setFillColor(HexColor("#4B5563"))
    c.drawString(54, 90, f"Please reference {inv['invoiceNumber']} with your payment. Remit to account ending 4821.")
    c.drawString(54, 76, "Questions about this invoice: ar@" + v["name"].split()[0].lower() + "-example.com")

def tplB(c, inv, ironclad=False):
    W,H = letter; v = V[inv["vendorId"]]; L = inv["labels"]; col = BRAND[v["vendorId"]]
    c.setFillColor(HexColor(col)); c.rect(0, H-96, W, 96, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 20); c.drawString(54, H-52, v["name"])
    c.setFont("Helvetica", 9.5); c.drawString(54, H-70, " | ".join(v["addr"]))
    c.setFont("Helvetica-Bold", 14); c.drawRightString(W-54, H-52, "Tax Invoice" if not ironclad else "INVOICE")
    c.setFillColor(black)
    if ironclad:
        y = H-130
        c.setFont("Helvetica", 9.5); c.setFillColor(HexColor("#4B5563")); c.drawString(54, y, L["inv"]); c.drawString(170, y, L["po"]); c.drawString(300, y, L["date"]); c.drawString(420, y, L["vid"])
        c.setFont("Helvetica-Bold", 11); c.setFillColor(black); c.drawString(54, y-15, inv["invoiceNumber"]); c.drawString(170, y-15, inv["po"]); c.drawString(300, y-15, inv["dateStr"]); c.drawString(420, y-15, inv["vendorId"])
        c.setFont("Helvetica", 9); c.setFillColor(HexColor("#4B5563")); c.drawString(54, y-32, "Customer ref. MH-" + inv["po"][-5:] + "   Ship via: Ground   Terms: Net 45")
    else:
        y = H-128; c.setFont("Helvetica", 9.5)
        left = [(L["inv"], inv["invoiceNumber"]), (L["date"], inv["dateStr"])]; right = [(L["po"], inv["po"]), (L["vid"], inv["vendorId"])]
        for i,(k,val) in enumerate(left):
            c.setFillColor(HexColor("#4B5563")); c.setFont("Helvetica",9.5); c.drawString(54, y-16*i, k+":"); c.setFillColor(black); c.setFont("Helvetica-Bold",9.5); c.drawString(140, y-16*i, val)
        for i,(k,val) in enumerate(right):
            c.setFillColor(HexColor("#4B5563")); c.setFont("Helvetica",9.5); c.drawString(330, y-16*i, k+":"); c.setFillColor(black); c.setFont("Helvetica-Bold",9.5); c.drawString(430, y-16*i, val)
    c.setFont("Helvetica-Bold", 10); c.setFillColor(black); c.drawString(54, H-200, "Bill to")
    c.setFont("Helvetica", 9.5)
    for i,a in enumerate(BILL): c.drawString(54, H-214-12*i, a)
    yy = table(c, 54, H-290, W-108, inv, col)
    totals(c, W-54, yy-18, inv, L, "B")
    c.setFont("Helvetica", 8.5); c.setFillColor(HexColor("#4B5563")); c.drawString(54, 80, "Thank you for your business. Late payments may incur a 1.5% monthly fee.")

def tplC(c, inv):
    W,H = A4; v = V[inv["vendorId"]]; L = inv["labels"]
    c.setFont("Helvetica-Bold", 15); c.drawRightString(W-50, H-60, v["name"])
    c.setFont("Helvetica", 9)
    for i,a in enumerate(v["addr"]): c.drawRightString(W-50, H-76-11*i, a)
    c.drawRightString(W-50, H-110, "VAT ID: DE000000000 (sample)")
    c.setFont("Helvetica", 7.5); c.drawString(50, H-140, v["name"] + " - " + ", ".join(v["addr"]))
    c.setFont("Helvetica", 10)
    for i,a in enumerate(BILL): c.drawString(50, H-156-13*i, a)
    c.setFont("Helvetica-Bold", 18); c.drawString(50, H-240, "INVOICE")
    meta = [(L["inv"], inv["invoiceNumber"]), (L["date"], inv["dateStr"]), (L["po"], inv["po"]), (L["vid"], inv["vendorId"]), ("Currency", inv["currency"])]
    y = H-262
    for k,val in meta:
        c.setFont("Helvetica", 9.5); c.drawString(50, y, k); c.setFont("Helvetica-Bold", 9.5); c.drawString(160, y, val); y -= 14
    yy = table(c, 50, H-350, W-100, inv, "#374151", pos_col=True)
    L2 = dict(L); 
    cur = inv["currency"]; s = sym(cur); y = yy-18
    for lab,val,b in [("Net amount", inv["subtotal"], False),(inv["taxLabel"], inv["tax"], False),(L["total"], inv["total"], True)]:
        c.setFont("Helvetica-Bold" if b else "Helvetica", 10.5 if b else 10); c.drawRightString(W-160, y, lab); c.drawRightString(W-50, y, s+m(val,cur)); y -= 17
    c.setFont("Helvetica", 8); c.setFillColor(HexColor("#4B5563"))
    c.drawString(50, 70, "Payment within 30 days net. IBAN DE00 1234 5678 9012 3456 78 (sample)  BIC SAMPDEFFXXX")
    c.drawString(50, 58, "Managing director: sample data for training use only")

for inv in seed.INVOICES:
    path = f"out/invoices/{inv['file']}"
    size = A4 if inv["tpl"]=="C" else letter
    c = canvas.Canvas(path, pagesize=size); c.setTitle(f"Invoice {inv['invoiceNumber']}"); c.setAuthor(V[inv['vendorId']]['name'])
    {"A":lambda: tplA(c,inv), "B":lambda: tplB(c,inv), "B2":lambda: tplB(c,inv,True), "C":lambda: tplC(c,inv)}[inv["tpl"]]()
    c.setFont("Helvetica-Oblique", 7); c.setFillColor(HexColor("#9CA3AF")); c.drawCentredString(size[0]/2, 28, "Synthetic invoice for UiPath bootcamp training. Not a real document.")
    c.showPage(); c.save()
    if inv.get("scanned"):
        subprocess.run(["pdftoppm","-r","150","-png","-singlefile",path,"/tmp/scan"],check=True)
        from PIL import Image, ImageFilter
        import random
        im = Image.open("/tmp/scan.png").convert("L").rotate(0.8, expand=False, fillcolor=255, resample=Image.BICUBIC)
        px = im.load(); random.seed(6)
        for _ in range(9000):
            x=random.randrange(im.width); y=random.randrange(im.height); px[x,y]=random.choice([150,190,215])
        im = im.filter(ImageFilter.GaussianBlur(0.45))
        im.save(path, "PDF", resolution=150.0)
print(sorted(os.listdir("out/invoices")))
