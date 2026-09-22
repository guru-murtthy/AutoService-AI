import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_quotation_pdf(
    quotation_number: str,
    business_name: str,
    customer_name: str,
    customer_phone: str,
    travel_details: dict,
    calculation: dict,
    valid_until: str
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    normal_bold = ParagraphStyle('BoldText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)

    elements = []

    # Business Header
    elements.append(Paragraph(business_name.upper(), title_style))
    elements.append(Paragraph(f"Official Travel Quotation • Ref: #{quotation_number}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    # Details Box (Customer & Trip Summary)
    cust_info = [
        [Paragraph("<b>Customer Name:</b>", styles['Normal']), Paragraph(customer_name, styles['Normal']),
         Paragraph("<b>Date:</b>", styles['Normal']), Paragraph(datetime.now().strftime("%d %b %Y"), styles['Normal'])],
        [Paragraph("<b>Phone:</b>", styles['Normal']), Paragraph(customer_phone or "N/A", styles['Normal']),
         Paragraph("<b>Valid Until:</b>", styles['Normal']), Paragraph(valid_until, styles['Normal'])],
        [Paragraph("<b>Route:</b>", styles['Normal']), Paragraph(f"{travel_details.get('origin', 'N/A')} → {travel_details.get('destination', 'N/A')}", styles['Normal']),
         Paragraph("<b>Vehicle:</b>", styles['Normal']), Paragraph(str(travel_details.get('vehicle_type', '7-seater')).title(), styles['Normal'])]
    ]
    info_table = Table(cust_info, colWidths=[90, 180, 80, 190])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # Pricing Items Table
    table_data = [
        [Paragraph("<b>Description</b>", normal_bold),
         Paragraph("<b>Qty</b>", normal_bold),
         Paragraph("<b>Unit Price (₹)</b>", normal_bold),
         Paragraph("<b>Total (₹)</b>", normal_bold)]
    ]

    for item in calculation.get("items", []):
        table_data.append([
            Paragraph(item["description"], styles['Normal']),
            Paragraph(str(item["quantity"]), styles['Normal']),
            Paragraph(f"₹{item['unit_price']:,.2f}", styles['Normal']),
            Paragraph(f"₹{item['total']:,.2f}", styles['Normal'])
        ])

    table_data.append(["", "", Paragraph("<b>Subtotal:</b>", normal_bold), Paragraph(f"<b>₹{calculation.get('subtotal', 0):,.2f}</b>", normal_bold)])
    if calculation.get("discount", 0) > 0:
        table_data.append(["", "", Paragraph("<b>Discount:</b>", normal_bold), Paragraph(f"<b>- ₹{calculation.get('discount', 0):,.2f}</b>", normal_bold)])
    table_data.append(["", "", Paragraph("<b>GST Tax (5%):</b>", normal_bold), Paragraph(f"<b>₹{calculation.get('tax', 0):,.2f}</b>", normal_bold)])
    table_data.append(["", "", Paragraph("<b>Grand Total:</b>", normal_bold), Paragraph(f"<b>₹{calculation.get('total', 0):,.2f}</b>", normal_bold)])

    item_table = Table(table_data, colWidths=[260, 60, 110, 110])
    item_table.setStyle(TableStyle([
        ('HEADERBACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#FEF3C7')), # Grand total highlight
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 20))

    # Terms & Conditions
    terms = [
        "1. Toll, state taxes, and parking charges are payable at actuals unless explicitly specified.",
        "2. Night driver allowance applicable if driving continues past 10:00 PM.",
        "3. Quotation valid for 7 days from the date of issuance.",
        "4. 20% advance payment required to confirm booking."
    ]
    elements.append(Paragraph("<b>Terms & Conditions:</b>", normal_bold))
    for t in terms:
        elements.append(Paragraph(t, subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
