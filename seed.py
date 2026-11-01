import json
VENDORS = [
 {"vendorId":"V-1001","name":"Northwind Office Supply Co.","status":"ACTIVE","currency":"USD","addr":["1450 Commerce Park Dr","Columbus, OH 43219"],"industry":"General / Financial services"},
 {"vendorId":"V-1002","name":"Bluepeak Medical Supplies Inc.","status":"ACTIVE","currency":"USD","addr":["88 Lakeview Blvd","Minneapolis, MN 55401"],"industry":"Healthcare"},
 {"vendorId":"V-1003","name":"Ironclad Components LLC","status":"ACTIVE","currency":"USD","addr":["3100 Foundry Rd","Toledo, OH 43605"],"industry":"Manufacturing"},
 {"vendorId":"V-1004","name":"Relay Field Services Ltd.","status":"ACTIVE","currency":"USD","addr":["725 Tower Ridge Ln","Plano, TX 75024"],"industry":"Telecom"},
 {"vendorId":"V-1005","name":"Civic Print & Signage","status":"ACTIVE","currency":"USD","addr":["19 Capitol Square","Albany, NY 12207"],"industry":"Public sector"},
 {"vendorId":"V-1006","name":"Halden Logistics GmbH","status":"INACTIVE","currency":"USD","addr":["Hafenstrasse 12","20457 Hamburg, Germany"],"industry":"Logistics"},
 {"vendorId":"V-1007","name":"Lumen IT Services","status":"ACTIVE","currency":"USD","addr":["600 Market St, Floor 9","San Francisco, CA 94104"],"industry":"IT services"},
 {"vendorId":"V-1008","name":"Adler Precision Tools GmbH","status":"ACTIVE","currency":"EUR","addr":["Industriestrasse 40","70565 Stuttgart, Germany"],"industry":"Manufacturing"},
]
POS = [
 {"poNumber":"PO-4500101","vendorId":"V-1001","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Copy paper, letter, 20 lb, case of 10 reams","orderedQty":40,"unitPrice":38.50},{"line":2,"description":"Toner cartridge, black, high yield","orderedQty":12,"unitPrice":142.00}]},
 {"poNumber":"PO-4500102","vendorId":"V-1002","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Nitrile exam gloves, medium, box of 100","orderedQty":100,"unitPrice":12.00},{"line":2,"description":"Sterile gauze pads 4x4, pack of 50","orderedQty":50,"unitPrice":18.75}]},
 {"poNumber":"PO-4500103","vendorId":"V-1003","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Machined aluminum bracket AB-220","orderedQty":10,"unitPrice":480.00}]},
 {"poNumber":"PO-4500104","vendorId":"V-1004","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Fiber splicing service, per site","orderedQty":20,"unitPrice":350.00}]},
 {"poNumber":"PO-4500105","vendorId":"V-1005","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Vinyl banner 3 x 6 ft, full color","orderedQty":30,"unitPrice":64.00}]},
 {"poNumber":"PO-4500106","vendorId":"V-1006","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"LTL freight, per pallet","orderedQty":8,"unitPrice":210.00}]},
 {"poNumber":"PO-4500107","vendorId":"V-1007","status":"CLOSED","currency":"USD","lines":[{"line":1,"description":"Managed backup service, monthly","orderedQty":1,"unitPrice":2400.00}]},
 {"poNumber":"PO-4500108","vendorId":"V-1007","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Laptop imaging and setup, per device","orderedQty":25,"unitPrice":80.00}]},
 {"poNumber":"PO-4500109","vendorId":"V-1008","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Precision torque wrench TW-50","orderedQty":4,"unitPrice":1153.50}]},
 {"poNumber":"PO-4500110","vendorId":"V-1003","status":"OPEN","currency":"USD","lines":[{"line":1,"description":"Hex bolt M8 x 40, box of 200","orderedQty":15,"unitPrice":27.40},{"line":2,"description":"Lock washer M8, box of 500","orderedQty":10,"unitPrice":19.90}]},
]
HISTORY = [
 {"vendorId":"V-1005","invoiceNumber":"CPS-2026-0918","poNumber":"PO-4500105","total":2073.60,"status":"PAID","paidOn":"2026-09-30"},
 {"vendorId":"V-1001","invoiceNumber":"INV-NW-20311","poNumber":"PO-4500087","total":1288.40,"status":"PAID","paidOn":"2026-09-12"},
]
INVOICES = [
 dict(n=1, file="invoice_01_northwind.pdf", tpl="A", vendorId="V-1001", invoiceNumber="INV-NW-20417", dateStr="October 6, 2026", dateIso="2026-10-06", po="PO-4500101", currency="USD",
      lines=[("Copy paper, letter, 20 lb, case of 10 reams",40,38.50),("Toner cartridge, black, high yield",12,142.00)], taxRate=0.0825, taxLabel="Sales tax (8.25%)",
      labels=dict(inv="Invoice #",date="Invoice Date",po="PO Number",vid="Vendor ID",total="Total Due"), scenario="Clean match", lab3=True, lab4="Yes - posted", agent="AUTO_POSTED"),
 dict(n=2, file="invoice_02_bluepeak.pdf", tpl="B", vendorId="V-1002", invoiceNumber="BMS-77821", dateStr="10/08/2026", dateIso="2026-10-08", po="PO-4500102", currency="USD",
      lines=[("Nitrile exam gloves, medium, box of 100",100,12.20),("Sterile gauze pads 4x4, pack of 50",50,18.75)], taxRate=0.0, taxLabel="Tax (exempt, medical supplies)",
      labels=dict(inv="Invoice No.",date="Date",po="Purchase Order",vid="Supplier No.",total="Amount Due"), scenario="Price variance inside tolerance (gloves +$0.20/box, $20 on the line)", lab3=True, lab4="Yes - posted", agent="AUTO_POSTED"),
 dict(n=3, file="invoice_03_ironclad.pdf", tpl="B2", vendorId="V-1003", invoiceNumber="IC-3391", dateStr="2026-10-09", dateIso="2026-10-09", po="PO-4500103", currency="USD",
      lines=[("Machined aluminum bracket AB-220",10,540.00)], taxRate=0.07, taxLabel="Sales tax 7%",
      labels=dict(inv="Invoice No.",date="Invoice Date",po="Order No.",vid="Your vendor no.",total="Amount due"), scenario="Price variance over tolerance (+$60/unit, 12.5%, $600 on the line)", lab3=True, lab4="No", agent="PRICE_VARIANCE / DISPUTE"),
 dict(n=4, file="invoice_04_relay.pdf", tpl="B", vendorId="V-1004", invoiceNumber="RFS-10882", dateStr="12-Oct-2026", dateIso="2026-10-12", po="PO-4500104", currency="USD",
      lines=[("Fiber splicing service, per site",25,350.00)], taxRate=0.06, taxLabel="Tax (6%)",
      labels=dict(inv="Invoice No.",date="Date",po="Purchase Order",vid="Supplier No.",total="Amount Due"), scenario="Quantity billed above PO (25 sites vs 20 ordered)", lab3=True, lab4="No", agent="QUANTITY_VARIANCE / DISPUTE + vendor query"),
 dict(n=5, file="invoice_05_civicprint.pdf", tpl="A", vendorId="V-1005", invoiceNumber="CPS-2026-0918", dateStr="10/13/2026", dateIso="2026-10-13", po="PO-4500105", currency="USD",
      lines=[("Vinyl banner 3 x 6 ft, full color",30,64.00)], taxRate=0.08, taxLabel="Sales tax (8%)",
      labels=dict(inv="Invoice #",date="Invoice Date",po="PO Number",vid="Vendor ID",total="Total Due"), scenario="Duplicate invoice number (already paid 2026-09-30)", lab3=False, lab4="-", agent="STOP_RETURNED"),
 dict(n=6, file="invoice_06_halden.pdf", tpl="C", vendorId="V-1006", invoiceNumber="HL-55102", dateStr="14 Oct 2026", dateIso="2026-10-14", po="PO-4500106", currency="USD",
      lines=[("LTL freight, per pallet",8,210.00)], taxRate=0.0, taxLabel="VAT 0% (export service)",
      labels=dict(inv="Invoice number",date="Invoice date",po="Your order",vid="Supplier no.",total="Total amount"), scenario="Inactive vendor (scanned-style image PDF)", lab3=False, lab4="-", agent="STOP_RETURNED", scanned=True),
 dict(n=7, file="invoice_07_lumen.pdf", tpl="A", vendorId="V-1007", invoiceNumber="LIT-9034", dateStr="2026-10-15", dateIso="2026-10-15", po="PO-4500107", currency="USD",
      lines=[("Managed backup service, monthly",1,2400.00)], taxRate=0.0, taxLabel="Tax (services, not taxable)",
      labels=dict(inv="Invoice #",date="Date",po="PO #",vid="Vendor ID",total="Balance Due"), scenario="Closed PO", lab3=False, lab4="-", agent="STOP_RETURNED"),
 dict(n=8, file="invoice_08_lumen.pdf", tpl="A", vendorId="V-1007", invoiceNumber="LIT-9041", dateStr="2026-10-16", dateIso="2026-10-16", po="PO-4500108", currency="USD",
      lines=[("Laptop imaging and setup, per device",25,80.00)], taxRate=0.08, taxLabel="Sales tax (8%)", totalOverride=2210.00,
      labels=dict(inv="Invoice #",date="Date",po="PO #",vid="Vendor ID",total="Balance Due"), scenario="Total miscalculated (2,000 + 160 printed as 2,210)", lab3=True, lab4="No (totals check)", agent="TAX_ERROR / DISPUTE"),
 dict(n=9, file="invoice_09_adler.pdf", tpl="C", vendorId="V-1008", invoiceNumber="AP-2026-0412", dateStr="03.08.2026", dateIso="2026-08-03", po="PO-4500109", currency="EUR",
      lines=[("Precision torque wrench TW-50",4,1000.00)], taxRate=0.0, taxLabel="VAT 0% (export delivery)",
      labels=dict(inv="Invoice number",date="Invoice date",po="Your order",vid="Supplier no.",total="Total amount"), scenario="EUR invoice against a USD PO (ECB rate 3 Aug 2026: 1.1535)", lab3=True, lab4="Yes with FX stretch / No without", agent="AUTO_POSTED with stretch; PRICE_VARIANCE without"),
 dict(n=10, file="invoice_10_ironclad.pdf", tpl="B2", vendorId="V-1003", invoiceNumber="IC-3402", dateStr="Oct 19, 2026", dateIso="2026-10-19", po="PO-4500110", currency="USD",
      lines=[("Hex bolt M8 x 40, box of 200",15,27.40),("Lock washer M8, box of 500",10,19.90)], taxRate=0.07, taxLabel="Sales tax 7%", exclTaxTrap=True,
      labels=dict(inv="Invoice No.",date="Invoice Date",po="Order No.",vid="Your vendor no.",total="Amount due"), scenario="IXP traps: Order No. beside Invoice No.; 'Total excl. tax' shown above amount due", lab3=True, lab4="Yes - posted", agent="AUTO_POSTED"),
]
def r2(x): return round(x + 1e-9, 2)
for inv in INVOICES:
    sub = r2(sum(q*p for _,q,p in inv["lines"]))
    tax = r2(sub*inv["taxRate"])
    inv["subtotal"]=sub; inv["tax"]=tax
    inv["total"]= inv.get("totalOverride", r2(sub+tax))
json.dump({"vendors":VENDORS,"purchaseOrders":POS,"invoiceHistory":HISTORY,"invoices":[{k:v for k,v in i.items() if k not in("tpl","labels")} for i in INVOICES],
           "tolerance":{"pct":2,"amount":50},"fx":{"date":"2026-08-03","EURUSD":1.1535,"source":"ECB euro reference rate"}}, open("seed.json","w"), indent=2)
for i in INVOICES: print(i["n"], i["invoiceNumber"], i["subtotal"], i["tax"], i["total"])
