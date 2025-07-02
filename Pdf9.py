from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_usbc_letter(output_path="USBC_Letter_Jason_Lucas_Generated.pdf"):
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    margin = 1 * inch
    line_height = 14
    y = height - margin

    # Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Law Offices of A. H. Bennett, Esq. – Compliance Counsel, USBC")
    y -= line_height
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Phone: (313) 555-9912 | Email: ahbennett@usbc.com")
    y -= line_height * 2

    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "USBC – United States Banking Corporation")
    y -= line_height
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Detroit Branch – 500 Woodward Ave, Detroit, MI 48226")
    y -= line_height
    c.drawString(margin, y, "Phone: (313) 555-4490 | Email: noreply@usbc.com")
    y -= line_height * 2

    # Date and Ref ID
    c.drawString(margin, y, "Date: June 17, 2025     Ref ID: USBC-DET-REF9823-L")
    y -= line_height * 2

    # Recipient
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "To: Mr. Jason Lucas")
    y -= line_height * 2

    # Subject
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Subject: Final Notice – Dormant Account and State Escheatment")
    y -= line_height * 2

    # Body
    c.setFont("Helvetica", 11)
    body = [
        "Dear Mr. Jason Lucas,",
        "",
        "This is an official notice concerning your account ending in XXXX2089,",
        "which currently holds a balance of $967,000.00. This account has been inactive and",
        "has not registered any activity or contact within the required period.",
        "",
        "In accordance with the Michigan Unclaimed Property Act (Public Act 29 of 1995),",
        "USBC is obligated to report and transfer dormant funds to the Michigan Department of Treasury",
        "if no preventive action is taken by June 20, 2025.",
        "",
        "Since you are not enrolled in internet banking, please visit our Detroit branch",
        "with a valid government-issued photo ID to either initiate a transaction or complete",
        "a Declaration of Intent to Retain Ownership form.",
        "",
        "Failure to take action before the stated deadline will result in the initiation of state",
        "escheatment procedures. Reclaiming escheated funds involves delays and formal filing with the state.",
        "",
        "We highly advise immediate action.",
        "",
        "Yours faithfully,",
        "",
        "A. H. Bennett, Esq.",
        "Senior Legal Advisor – Dormancy Compliance Unit",
        "USBC – United States Banking Corporation",
        "",
        "Issued under the supervision of legal counsel in compliance with Michigan state law.",
        "",
        "Mr. Jason Lucas",
        "123 Client Residence Blvd",
        "Detroit, MI 48210"
    ]

    for line in body:
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_height

    c.save()
    print(f"PDF generated successfully: {output_path}")

# Run the script
generate_usbc_letter()
