from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

 # 📌 Cesta k fontu
    font_path = os.path.join("app", "static", "fonts", "DejaVuSans.ttf")
    # Záhlaví faktury
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 50, "FAKTURA")

    # Info o firmě
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 90, "Firma: ArteModerno s.r.o.")
    p.drawString(40, height - 105, "Adresa: Praha 1, Česká republika")
    p.drawString(40, height - 120, "IČO: 12345678, DIČ: CZ12345678")

    # Datum a číslo
    p.drawString(400, height - 90, f"Datum: {order.created_at.strftime('%d.%m.%Y')}")
    p.drawString(400, height - 105, f"Faktura č.: F{order.id:03}")

    # Údaje zákazníka
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 160, "Zákazník:")
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 175, f"{order.name}")
    p.drawString(40, height - 190, f"{order.address}")
    p.drawString(40, height - 205, f"{order.email}")

    # Produkt
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 240, "Objednávka:")
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 255, f"Produkt: {order.product.name}")
    p.drawString(40, height - 270, f"Množství: {order.quantity}")
    p.drawString(40, height - 285, f"Cena: {order.product.price:.2f} Kč")

    # Celkem
    total = order.quantity * order.product.price
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 320, f"Celkem k úhradě: {total:.2f} Kč")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
