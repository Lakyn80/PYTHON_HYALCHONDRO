# app/utils/export_orders.py

import os
import pandas as pd
from datetime import datetime
from flask import current_app
from app.models import Order, Product, Customer, db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_orders():
    # Načti data z databáze
    orders = Order.query.order_by(Order.created_at.desc()).all()

    data = []
    for o in orders:
        customer = Customer.query.get(o.customer_id)
        product = Product.query.get(o.product_id)
        data.append({
            "ID": o.id,
            "Číslo objednávky": f"ORD{o.id:03d}",
            "Zákazník": customer.name if customer else "-",
            "Email": customer.email if customer else o.email,
            "Adresa": o.address,
            "Produkt": product.name if product else "-",
            "Množství": o.quantity,
            "Datum": o.created_at.strftime("%Y-%m-%d") if o.created_at else "",
            "Číslo faktury": f"F{o.id:03d}",
            "Stav": getattr(o, 'status', "Nová"),
        })

    df = pd.DataFrame(data)

    # Ulož CSV
    df.to_csv(os.path.join(EXPORT_DIR, "orders_export.csv"), index=False)

    # Ulož Excel
    df.to_excel(os.path.join(EXPORT_DIR, "orders_export.xlsx"), index=False)

    # PDF
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    with PdfPages(os.path.join(EXPORT_DIR, "orders_export.pdf")) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    print("✅ Objednávky exportovány.")
