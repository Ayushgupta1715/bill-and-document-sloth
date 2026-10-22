"""Generate realistic sample bills, invoices, receipts, and warranties for demonstration."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documents", "samples")


def create_sample_electricity_bill(output_path: str):
    """BESCOM Electricity Bill."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E3A8A'))
    story.append(Paragraph("BESCOM — Bangalore Electricity Supply Company", title_style))
    story.append(Paragraph("<b>ELECTRICITY CONSUMPTION BILL</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    info_data = [
        ["Consumer No:", "9182374610", "Bill Date:", "2026-10-18"],
        ["Consumer Name:", "Arjun Sharma", "Due Date:", "2026-10-28"],
        ["Tariff Category:", "LT-2(a) Domestic", "Billing Period:", "01 Oct 2026 - 18 Oct 2026"],
        ["Meter Number:", "BLR-MTR-40291", "Units Consumed:", "142 kWh"]
    ]
    t1 = Table(info_data, colWidths=[120, 150, 100, 150])
    t1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1F2937')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3F4F6')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    charges_data = [
        ["Description", "Units / Base", "Rate", "Amount (₹)"],
        ["Fixed Energy Charges", "1 Connection", "₹120.00", "120.00"],
        ["Energy Charges (142 kWh)", "142 kWh", "₹7.50 / kWh", "1,065.00"],
        ["Fuel Adjustment Charges (FAC)", "142 kWh", "₹1.80 / kWh", "255.60"],
        ["Electricity Tax (9%)", "-", "9%", "129.65"],
        ["Previous Arrears / Adjustments", "-", "-", "279.75"],
        ["TOTAL AMOUNT DUE", "", "", "₹1,850.00"]
    ]
    t2 = Table(charges_data, colWidths=[200, 110, 100, 110])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF3C7')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#92400E')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Payment Instructions:</b> Pay on or before <b>Due Date: 2026-10-28</b> to avoid late fee surcharge.", styles['Italic']))
    doc.build(story)


def create_sample_airtel_invoice(output_path: str):
    """Airtel Broadband Invoice."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#DC2626'))
    story.append(Paragraph("Airtel Broadband & Telecommunications", title_style))
    story.append(Paragraph("<b>TAX INVOICE — HIGH SPEED FIBER</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    info_data = [
        ["Invoice No:", "INV-2026-AIR-9481", "Invoice Date:", "2026-10-15"],
        ["Account No:", "AIR-FIB-7729104", "Due Date:", "2026-10-24"],
        ["Service:", "Airtel Xstream Fiber 200Mbps", "Billing Period:", "15 Oct 2026 - 14 Nov 2026"],
        ["GSTIN:", "29AAACA1234F1Z5", "Payment Status:", "Unpaid"]
    ]
    t1 = Table(info_data, colWidths=[120, 150, 100, 150])
    t1.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    items_data = [
        ["Plan / Item Description", "Speed", "Quantity", "Amount (₹)"],
        ["Xstream Entertainment Broadband", "200 Mbps Unlimited", "1 Month", "846.61"],
        ["CGST (9%)", "-", "-", "76.19"],
        ["SGST (9%)", "-", "-", "76.20"],
        ["TOTAL PAYABLE AMOUNT", "", "", "₹999.00"]
    ]
    t2 = Table(items_data, colWidths=[200, 130, 80, 110])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEE2E2')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#991B1B')),
    ]))
    story.append(t2)
    doc.build(story)


def create_sample_apple_warranty(output_path: str):
    """AppleCare+ Warranty Certificate."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'))
    story.append(Paragraph("AppleCare+ Proof of Coverage", title_style))
    story.append(Paragraph("<b>OFFICIAL WARRANTY CERTIFICATE</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    info_data = [
        ["Provider:", "Apple Inc.", "Agreement Number:", "APP-WARR-90218"],
        ["Product Description:", "MacBook Pro 14-inch (M3 Pro)", "Serial Number:", "C02G91XPQ6L4"],
        ["Coverage Start Date:", "2024-11-15", "Valid Until:", "2027-11-15"],
        ["Coverage Status:", "Active & Protected", "Warranty Type:", "AppleCare+ Extended Warranty"]
    ]
    t1 = Table(info_data, colWidths=[130, 140, 110, 140])
    t1.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Coverage Summary:</b> Unlimited incidents of accidental damage protection, 24/7 priority technical support, and battery service coverage valid until <b>2027-11-15</b>.", styles['Normal']))
    doc.build(story)


def create_sample_insurance_policy(output_path: str):
    """Star Health Insurance Policy."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#047857'))
    story.append(Paragraph("Star Health and Allied Insurance Co. Ltd.", title_style))
    story.append(Paragraph("<b>HEALTH INSURANCE POLICY SCHEDULE</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    info_data = [
        ["Policy Number:", "POL-SH-8829103", "Date of Issue:", "2025-12-30"],
        ["Insured Name:", "Neha Sharma & Family", "Renewal Date:", "2026-12-30"],
        ["Policy Type:", "Family Health Optima", "Sum Assured:", "₹10,00,000"],
        ["Total Premium Paid:", "₹12,400.00", "Payment Status:", "Active / Paid"]
    ]
    t1 = Table(info_data, colWidths=[120, 150, 110, 140])
    t1.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#A7F3D0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    doc.build(story)


def create_sample_cafe_receipt(output_path: str):
    """Blue Tokai Coffee Roasters Receipt."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#78350F'))
    story.append(Paragraph("Blue Tokai Coffee Roasters", title_style))
    story.append(Paragraph("<b>RETAIL STORE PURCHASE RECEIPT</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    info_data = [
        ["Store:", "Indiranagar Roastery", "Order ID:", "#BT-8491"],
        ["Date:", "2026-10-19", "Payment Method:", "Credit Card ending 4091"]
    ]
    t1 = Table(info_data, colWidths=[120, 150, 100, 150])
    t1.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FDE68A')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    items = [
        ["Item", "Qty", "Price", "Total (₹)"],
        ["Flat White Coffee (Oat Milk)", "1", "₹220.00", "220.00"],
        ["Butter Almond Croissant", "1", "₹145.00", "145.00"],
        ["CGST & SGST (5%)", "-", "-", "20.00"],
        ["TOTAL AMOUNT", "", "", "₹385.00"]
    ]
    t2 = Table(items, colWidths=[200, 60, 100, 120])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#92400E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF3C7')),
    ]))
    story.append(t2)
    doc.build(story)


def generate_all_sample_documents() -> list[str]:
    """Generate all demo sample documents on disk and return their file paths."""
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    samples = [
        (os.path.join(SAMPLE_DIR, "Sample_BESCOM_Electricity_Bill.pdf"), create_sample_electricity_bill),
        (os.path.join(SAMPLE_DIR, "Sample_Airtel_Fiber_Invoice.pdf"), create_sample_airtel_invoice),
        (os.path.join(SAMPLE_DIR, "Sample_AppleCare_Warranty.pdf"), create_sample_apple_warranty),
        (os.path.join(SAMPLE_DIR, "Sample_StarHealth_Insurance_Policy.pdf"), create_sample_insurance_policy),
        (os.path.join(SAMPLE_DIR, "Sample_Cafe_Coffee_Receipt.pdf"), create_sample_cafe_receipt),
    ]

    generated_paths = []
    for path, func in samples:
        func(path)
        generated_paths.append(path)
    return generated_paths
