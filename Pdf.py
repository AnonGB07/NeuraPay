from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line, Rect, Circle
from reportlab.pdfgen import canvas
import datetime
import random
import os

# Default values for testing (Florida-specific context)
default_data = {
    "seller_name": "Jason Lucas",
    "seller_location": "123 Client Residence Blvd, Detroit, MI 48210",
    "seller_id": "MI-123-456-789",
    "buyer_name": "Bonnie Bryon",
    "buyer_nationality": "Canadian",
    "property_address": "789 Sunny Isles Blvd, Miami, FL 33160",
    "property_valuation": "$967,000.00",
    "county": "Miami-Dade County",
    "transfer_date": datetime.datetime.now().strftime("%B %d, %Y"),
    "payment_method": "Wire Transfer",
    "require_apostille": True,
    "doc_number": f"2025-{random.randint(100000, 999999)}",
    "instrument_number": f"MIAMI{random.randint(1000000, 9999999)}",
    "book_page": f"Book {random.randint(10000, 99999)}, Page {random.randint(10, 999)}",
    "parcel_id": f"{random.randint(1000000, 9999999)}-0000",
    "clerk_initials": "JD"  # Simulated clerk initials
}

# Get user input or use defaults
def get_user_input():
    print("Enter property transfer details (press Enter to accept defaults):")
    data = default_data.copy()
    data["seller_name"] = input(f"Seller Name [{default_data['seller_name']}]: ") or default_data["seller_name"]
    data["seller_location"] = input(f"Seller Location [{default_data['seller_location']}]: ") or default_data["seller_location"]
    data["seller_id"] = input(f"Seller ID/Passport [{default_data['seller_id']}]: ") or default_data["seller_id"]
    data["buyer_name"] = input(f"Buyer Name [{default_data['buyer_name']}]: ") or default_data["buyer_name"]
    data["buyer_nationality"] = input(f"Buyer Nationality [{default_data['buyer_nationality']}]: ") or default_data["buyer_nationality"]
    data["property_address"] = input(f"Property Address [{default_data['property_address']}]: ") or default_data["property_address"]
    data["property_valuation"] = input(f"Property Valuation [{default_data['property_valuation']}]: ") or default_data["property_valuation"]
    data["county"] = input(f"County [{default_data['county']}]: ") or default_data["county"]
    data["transfer_date"] = input(f"Transfer Date [{default_data['transfer_date']}]: ") or default_data["transfer_date"]
    data["payment_method"] = input(f"Payment Method [{default_data['payment_method']}]: ") or default_data["payment_method"]
    data["require_apostille"] = input(f"Require Apostille? [y/N]: ").lower() == 'y' or default_data["require_apostille"]
    data["doc_number"] = input(f"Document Number [{default_data['doc_number']}]: ") or default_data["doc_number"]
    return data

# Function to add Florida-style header and footer
def add_header_footer(canvas, doc):
    canvas.saveState()
    # Florida-style letterhead with official look
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(inch, letter[1] - 0.75 * inch, f"{data['county']} Clerk of the Court and Comptroller")
    canvas.setFont("Times-Roman", 10)
    canvas.drawString(inch, letter[1] - 1 * inch, "Real Estate Recording Division")
    canvas.drawString(inch, letter[1] - 1.25 * inch, "73 West Flagler Street, Miami, FL 33130 | Phone: (305) 275-1155")
    canvas.drawString(inch, letter[1] - 1.5 * inch, f"Instrument #: {data['instrument_number']} | Doc #: {data['doc_number']} | Recorded: {datetime.datetime.now().strftime('%B %d, %Y %I:%M %p')} WAT")

    # Simulated seal and barcode
    canvas.circle(inch + 6 * inch, letter[1] - 1.5 * inch, 0.5 * inch, fill=0)
    canvas.drawString(inch + 5.5 * inch, letter[1] - 1.75 * inch, "[Official Seal - State of Florida]")
    canvas.rect(inch + 5 * inch, letter[1] - 2 * inch, 1.5 * inch, 0.25 * inch)
    canvas.drawString(inch + 5 * inch, letter[1] - 2.25 * inch, f"[Barcode: {data['instrument_number']}]")

    # Footer with page number and certification
    canvas.setFont("Times-Roman", 8)
    page_num = canvas.getPageNumber()
    canvas.drawString(letter[0] - 2 * inch, 0.25 * inch, f"Page {page_num} of {doc.pageCount} | Certified by: {data['clerk_initials']}")

    canvas.restoreState()

# Function to create a section with Florida-style formatting
def create_section(doc, title, content):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontName = "Times-Roman"
    normal_style.fontSize = 10
    heading_style = styles['Heading1']
    heading_style.fontName = "Times-Roman"
    heading_style.fontSize = 12
    heading_style.spaceAfter = 12

    elements = [Paragraph(f"<b>{title}</b>", heading_style)]
    for item in content:
        if isinstance(item, str):
            elements.append(Paragraph(item, normal_style))
        else:
            elements.append(item)
    elements.append(Spacer(1, 12))
    doc.build(elements)

# Main PDF generation
def generate_pdf(data):
    pdf_file = "Complete_Property_Transfer_Documents.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=108)  # 3-inch top margin for recording
    elements = []

    # Signature and notarization block (Florida-style with enhanced details)
    signature_block = [
        Spacer(1, 12),
        Paragraph("<b>Seller Signature:</b> _______________________________", normal_style),
        Paragraph(f"Name: {data['seller_name']} | ID: {data['seller_id']} | Date: _______________________________", normal_style),
        Spacer(1, 12),
        Paragraph("<b>Notary Public:</b>", normal_style),
        Paragraph(f"State of Florida | County of {data['county'].replace(' County', '')}", normal_style),
        Paragraph(f"Sworn to and subscribed before me on {data['transfer_date']} by {data['seller_name']} who is personally known to me or has produced {data['seller_id']} as identification.", normal_style),
        Paragraph("Notary Signature: _______________________________ | Seal: [Notary Seal - State of Florida]", normal_style),
        Paragraph(f"Commission #: {random.randint(100000, 999999)} | Expires: {datetime.datetime(2026, 12, 31).strftime('%B %d, %Y')}", normal_style),
        Spacer(1, 12),
        Paragraph("<b>Clerk Certification:</b>", normal_style),
        Paragraph(f"I hereby certify that the foregoing instrument was filed and recorded on {datetime.datetime.now().strftime('%B %d, %Y')} at {datetime.datetime.now().strftime('%I:%M %p')} WAT in {data['county']} Public Records. [Seal]", normal_style),
        Paragraph(f"Deputy Clerk: {data['clerk_initials']}", normal_style),
    ]

    # 1. Warranty Deed (Florida Statute 689.02)
    create_section(doc, "Warranty Deed", [
        f"THIS WARRANTY DEED, made this {data['transfer_date']} at {datetime.datetime.now().strftime('%I:%M %p')} WAT, between {data['seller_name']}, whose address is {data['seller_location']}, Grantor, and {data['buyer_name']}, whose address is [Buyer Address], Grantee,",
        f"WITNESSETH, that the Grantor, for and in consideration of the sum of {data['property_valuation']} and other good and valuable consideration, the receipt whereof is hereby acknowledged, has granted, bargained, sold, and conveyed to the Grantee, and Grantee's heirs and assigns forever, the following described property in {data['county']}, Florida:",
        f"Legal Description: Lot 12, Block 3, Sunny Isles Subdivision, {data['property_address']}, per Plat Book {random.randint(100, 999)}, Page {random.randint(10, 99)}, Parcel ID: {data['parcel_id']} (Surveyor Cert. # {random.randint(1000, 9999)}).",
        f"TO HAVE AND TO HOLD the same in fee simple forever. The Grantor hereby covenants with the Grantee that the Grantor is lawfully seized of said land in fee simple; that the land is free from all encumbrances except as recorded in {data['book_page']}; and that the Grantor will warrant and defend the same against the lawful claims of all persons.",
        f"Recorded in Official Records {data['book_page']} of {data['county']} Public Records | Document Fee: $10.00 per Florida Statute 28.24 | Intangible Tax: $1,934.00 (0.2%)."
    ] + signature_block)

    # 2. Title Transfer Request
    create_section(doc, "Title Transfer Request", [
        f"Request to transfer title of property located at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['seller_name']} to {data['buyer_name']} in {data['county']}, Florida.",
        f"Instrument Number: {data['instrument_number']} | Book/Page: {data['book_page']} | Filing Fee: $10.00 | Transfer Tax: $5,820.00 (0.70%)."
    ] + signature_block)

    # 3. Affidavit of Ownership
    create_section(doc, "Affidavit of Ownership", [
        f"STATE OF FLORIDA | COUNTY OF {data['county'].replace(' County', '')}",
        f"BEFORE ME, the undersigned authority, personally appeared {data['seller_name']}, who being duly sworn, deposes and says that they are the owner of the property located at {data['property_address']} (Parcel ID: {data['parcel_id']}), free of any liens except those recorded in {data['book_page']}."
    ] + signature_block)

    # 4. Warranty Deed (Duplicate for Record)
    create_section(doc, "Warranty Deed (Duplicate for Record)", [
        "See primary Warranty Deed above. This duplicate is filed for record purposes with {data['county']} Clerk.",
        f"Filed on {data['transfer_date']} under Instrument #{data['instrument_number']} | Certified Copy Fee: $1.00 per page."
    ] + signature_block)

    # 5. Property Appraisal Report
    create_section(doc, "Property Appraisal Report", [
        f"Appraised Value: {data['property_valuation']} as of {data['transfer_date']} by {data['county']} Property Appraiser Office, Appraisal ID: {random.randint(1000000, 9999999)}, Parcel ID: {data['parcel_id']} (Cert. # {random.randint(1000, 9999)})."
    ])

    # 6. Statement of Consideration
    create_section(doc, "Statement of Consideration", [
        f"Consideration for transfer: {data['property_valuation']} via {data['payment_method']} as per Florida Statute 689.01. Documentary Stamp Tax: $5,820.00 (0.70%) | Intangible Tax: $1,934.00 (0.2%).",
        f"Certified by {data['county']} Tax Collector, Receipt #: {random.randint(1000, 9999)} | Transaction ID: {random.randint(1000000000, 9999999999)}."
    ] + signature_block)

    # 7. Documentary Stamp Tax Receipt
    create_section(doc, "Documentary Stamp Tax Receipt", [
        f"Receipt for Documentary Stamp Tax: $5,820.00 (0.70% of {data['property_valuation']} per Florida Statute 201.02) for {data['property_address']} (Parcel ID: {data['parcel_id']}).
        Paid on {data['transfer_date']} | Receipt #: {random.randint(1000, 9999)} | Issued by {data['county']} Tax Collector Office."
    ])

    # 8. Tax Clearance Certificate
    create_section(doc, "Tax Clearance Certificate", [
        f"Certificate issued by {data['county']} Tax Collector confirming all property taxes are cleared for {data['property_address']} (Parcel ID: {data['parcel_id']}) as of {data['transfer_date']}."
        f"Certificate #: {random.randint(1000, 9999)} | Valid Until: {datetime.datetime(2026, 6, 30).strftime('%B %d, %Y')}."
    ] + signature_block)

    # 9. Utility Clearance Certificate
    create_section(doc, "Utility Clearance Certificate", [
        f"Utilities cleared for {data['property_address']} (Account #: {random.randint(100000, 999999)}) by Miami-Dade County Water and Sewer Department as of {data['transfer_date']}."
        f"Clearance #: {random.randint(1000, 9999)} | Issued by: Miami-Dade County Utilities."
    ] + signature_block)

    # 10. Proof of Identity
    create_section(doc, "Proof of Identity", [
        f"Seller: {data['seller_name']} | ID: {data['seller_id']} | Verified by Notary on {data['transfer_date']}",
        f"Buyer: {data['buyer_name']} | Nationality: {data['buyer_nationality']} | ID: [Buyer ID Placeholder] | Verified by: [Notary/Agent]"
    ])

    # 11. Notarized Transfer Authorization Letter
    create_section(doc, "Notarized Transfer Authorization Letter", [
        f"I, {data['seller_name']}, residing at {data['seller_location']}, authorize the transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['buyer_name']} under Florida Statute 689.01."
    ] + signature_block)

    # 12. Power of Attorney
    create_section(doc, "Power of Attorney", [
        f"Power of Attorney granted by {data['seller_name']} to [Agent Name] for property transfer, per Florida Statute 709.2101."
        f"POA #: {random.randint(100000, 999999)} | Recorded in {data['book_page']} | Effective: {data['transfer_date']}."
    ] + signature_block)

    # 13. Bank Compliance Letter
    create_section(doc, "Bank Compliance Letter", [
        f"United States Banking Corporation confirms compliance for account ending XXXXX2089, balance ${data['property_valuation']}, for {data['seller_name']}."
        f"Compliance Cert #: {random.randint(1000, 9999)} | Issued: {data['transfer_date']} | Branch: Detroit, MI."
    ] + signature_block)

    # 14. Wire Transfer Confirmation
    create_section(doc, "Wire Transfer Confirmation", [
        f"Wire transfer of ${data['property_valuation']} from {data['seller_name']} (Account XXXXX2089) to {data['buyer_name']} on {data['transfer_date']} at {datetime.datetime.now().strftime('%I:%M %p')} WAT."
        f"Transaction ID: {random.randint(1000000000, 9999999999)} | Bank Ref #: {random.randint(100000, 999999)} | SWIFT: USBKUS33."
    ])

    # 15. FIRPTA Disclosure
    if data["buyer_nationality"] != "U.S.":
        create_section(doc, "FIRPTA Disclosure", [
            f"Foreign Investment in Real Property Tax Act (FIRPTA) disclosure for {data['buyer_name']}, a {data['buyer_nationality']} citizen, per 26 U.S.C. § 1445."
            f"Withholding Certificate #: {random.randint(100000, 999999)} | Withholding Amount: $96,700.00 (10%)."
        ] + signature_block)

    # 16. Apostille Request
    if data["require_apostille"]:
        create_section(doc, "Apostille Request", [
            f"Request for Apostille for transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['buyer_name']} in Canada, per The Hague Convention of 1961."
            f"Request #: {random.randint(1000, 9999)} | Submitted to Florida Secretary of State on {data['transfer_date']}."
        ] + signature_block)

    # Build the PDF with header/footer
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    print(f"PDF generated successfully: {pdf_file}")

if __name__ == "__main__":
    global data
    data = get_user_input()
    generate_pdf(data)
