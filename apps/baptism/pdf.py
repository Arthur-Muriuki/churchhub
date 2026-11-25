import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generate_baptism_certificate_pdf(record, church_profile):
    """
    Renders an A4 PDF certificate for a verified BaptismRecord and returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    width, height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    primary_hex = getattr(church_profile, "primary_color", "#0A2540") or "#0A2540"
    try:
        primary_color = colors.HexColor(primary_hex)
    except Exception:
        primary_color = colors.HexColor("#0A2540")

    gold_accent = colors.HexColor("#B45309")
    muted_gray = colors.HexColor("#4B5563")
    light_bg = colors.HexColor("#F8FAFC")

    # Subtle background tint & decorative double border
    c.setFillColor(light_bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setStrokeColor(primary_color)
    c.setLineWidth(3)
    c.rect(14 * mm, 14 * mm, width - 28 * mm, height - 28 * mm, fill=0, stroke=1)

    c.setStrokeColor(gold_accent)
    c.setLineWidth(1)
    c.rect(17 * mm, 17 * mm, width - 34 * mm, height - 34 * mm, fill=0, stroke=1)

    y = height - 36 * mm

    # Optional church logo
    if church_profile and church_profile.logo:
        try:
            c.drawImage(
                church_profile.logo.path,
                width / 2 - 11 * mm,
                y - 14 * mm,
                width=22 * mm,
                height=22 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
            y -= 20 * mm
        except Exception:
            pass

    # Church Name & Denomination
    church_name = (church_profile.name if church_profile and church_profile.name else "ChurchHub Assembly").upper()
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(width / 2, y, church_name)
    y -= 6 * mm

    if church_profile and church_profile.denomination:
        c.setFillColor(muted_gray)
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, church_profile.denomination)
        y -= 6 * mm

    if church_profile and church_profile.physical_address:
        c.setFillColor(muted_gray)
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, y, church_profile.physical_address)
        y -= 10 * mm

    # Certificate Title
    c.setFillColor(gold_accent)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, y, "CERTIFICATE OF WATER BAPTISM")
    y -= 12 * mm

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(width / 2, y, "This is to certify that")
    y -= 11 * mm

    # Recipient Name
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y, record.member.full_name)
    y -= 5 * mm

    c.setStrokeColor(gold_accent)
    c.setLineWidth(1)
    c.line(width / 2 - 65 * mm, y, width / 2 + 65 * mm, y)
    y -= 11 * mm

    # Baptism Statement
    baptism_date_str = record.baptism_date.strftime("%B %d, %Y")
    venue_str = record.location_or_venue or (church_profile.name if church_profile else "the local assembly")
    minister_str = record.officiating_minister or "Authorized Minister"

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(
        width / 2,
        y,
        f"received Christian water baptism on {baptism_date_str}",
    )
    y -= 7 * mm
    c.drawCentredString(
        width / 2,
        y,
        f"at {venue_str}, administered by {minister_str}.",
    )
    y -= 14 * mm

    # Verification & Reference Details
    c.setFillColor(muted_gray)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, y, f"Certificate Reference No.: {record.certificate_number}")
    y -= 6 * mm
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(width / 2, y, f"Member ID: {record.member.member_number}")
    if record.witness_name:
        y -= 6 * mm
        c.drawCentredString(width / 2, y, f"Witness: {record.witness_name}")

    # Signatories block near bottom
    sig_y = 46 * mm
    left_x = 45 * mm
    right_x = width - 45 * mm

    if church_profile and church_profile.official_stamp_or_signature:
        try:
            c.drawImage(
                church_profile.official_stamp_or_signature.path,
                width / 2 - 14 * mm,
                sig_y - 2 * mm,
                width=28 * mm,
                height=18 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    c.setStrokeColor(muted_gray)
    c.setLineWidth(0.8)
    c.line(left_x - 28 * mm, sig_y, left_x + 28 * mm, sig_y)
    c.line(right_x - 28 * mm, sig_y, right_x + 28 * mm, sig_y)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    pastor_label = (church_profile.senior_pastor_name if church_profile and church_profile.senior_pastor_name else "Senior Pastor")
    secretary_label = (church_profile.church_secretary_name if church_profile and church_profile.church_secretary_name else "Church Secretary")
    c.drawCentredString(left_x, sig_y - 5 * mm, pastor_label)
    c.drawCentredString(right_x, sig_y - 5 * mm, secretary_label)

    c.setFillColor(muted_gray)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(left_x, sig_y - 9.5 * mm, "Senior Pastor / Clergy")
    c.drawCentredString(right_x, sig_y - 9.5 * mm, "Church Secretary / Registrar")

    # Footer note
    footer_note = (
        church_profile.certificate_footer_note
        if church_profile and church_profile.certificate_footer_note
        else "Official digital record verified by Church Administration."
    )
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(width / 2, 23 * mm, footer_note)

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes