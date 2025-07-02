from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line, Rect, Circle
from reportlab.pdfgen import canvas
import datetime
import random
import os

# Customized data with dates between March 4-7, 2025
data = {
    "seller_name": "Jason Lucas",
    "seller_location": "Ann Arbor, MI 48104",
    "seller_id": "MI-48321-654987",
    "first_buyer_name": "Bonnie Bryon",
    "first_buyer_nationality": "Canadian",
    "first_buyer_address": "9907 Road 9, Essex, ON N8M, Canada",
    "first_buyer_id": "[Buyer ID Placeholder]",
    "second_buyer_name": "George A. Hansen",
    "second_buyer_nationality": "U.S.",
    "second_buyer_address": "1234 Ocean Drive, Key Biscayne, FL 33149",
    "second_buyer_id": "FL-456789-1234",
    "property_address": "799 Cranston Blvd, Key Biscayne, FL 33149",
    "property_valuation": "$980,000.00",
    "county": "Miami-Dade County",
    # Random dates between March 4-7, 2025
    "transfer_date_1": datetime.datetime(2025, 3, random.randint(4, 7)).strftime("%B %d, %Y"),
    "transfer_date_2": datetime.datetime(2025, 3, random.randint(4, 7)).strftime("%B %d, %Y"),
    "payment_method": "Wire Transfer",
    "require_apostille": True,
    "doc_number_1": "2025-456789",
    "instrument_number_1": "MIAMI2345678",
    "book_page_1": "Book 23456, Page 789",
    "doc_number_2": "2025-567890",
    "instrument_number_2": "MIAMI3456789",
    "book_page_2": "Book 23457, Page 790",
    "parcel_id": "3050-1234-5678-0000",
    "legal_description": "Lot 5, Block 2, Cranston Condominiums, per Plat Book 305, Page 45",
    "surveyor_cert": "2456",
    "clerk_initials": "JD",
    "notary_commission": "789456",
    "notary_expires": "December 31, 2026",
    "appraisal_id": "4567890",
    "utility_account": "789012",
    "attorney_name": "Brian",
    "law_firm": "SWBW Law Firm",
    "law_firm_location": "Ohio"
}

# Define styles globally
styles = getSampleStyleSheet()
normal_style = styles['Normal']
normal_style.fontName = "Times-Roman"
normal_style.fontSize = 10
heading_style = styles['Heading1']
heading_style.fontName = "Times-Roman"
heading_style.fontSize = 12
heading_style.spaceAfter = 12

# Function to add Florida-style header and footer with color
def add_header_footer(canvas, doc):
    canvas.saveState()
    # Colored header
    canvas.setFillColor(colors.blue)
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(inch, letter[1] - 0.75 * inch, f"{data['county']} Clerk of the Court and Comptroller")
    canvas.setFillColor(colors.black)
    canvas.setFont("Times-Roman", 10)
    canvas.drawString(inch, letter[1] - 1 * inch, "Real Estate Recording Division")
    canvas.drawString(inch, letter[1] - 1.25 * inch, "73 West Flagler Street, Miami, FL 33130 | Phone: (305) 275-1155 | Email: recording@miamidadeclerk.gov")
    canvas.drawString(inch, letter[1] - 1.5 * inch, f"Instrument #: {data['instrument_number_1']} | Doc #: {data['doc_number_1']} | Recorded: {data['transfer_date_1']} 10:00 AM WAT")

    # Colored simulated seal and barcode
    canvas.setFillColor(colors.lightgrey)
    canvas.circle(inch + 6 * inch, letter[1] - 1.5 * inch, 0.5 * inch, fill=1)
    canvas.setFillColor(colors.black)
    canvas.drawString(inch + 5.5 * inch, letter[1] - 1.75 * inch, "[Official Seal - State of Florida]")
    canvas.rect(inch + 5 * inch, letter[1] - 2 * inch, 1.5 * inch, 0.25 * inch)
    canvas.setFillColor(colors.gray)
    canvas.rect(inch + 5 * inch, letter[1] - 2 * inch, 1.5 * inch, 0.25 * inch, fill=1)
    canvas.setFillColor(colors.black)
    canvas.drawString(inch + 5 * inch, letter[1] - 2.25 * inch, f"[Barcode: {data['instrument_number_1']}-{random.randint(1000, 9999)}]")

    # Colored footer with certification and watermark
    canvas.setFont("Times-Roman", 8)
    page_num = canvas.getPageNumber()
    canvas.drawString(letter[0] - 2 * inch, 0.25 * inch, f"Page {page_num} | Certified by: {data['clerk_initials']} | Copy Fee: $1.00")
    canvas.setFillColor(colors.red)
    canvas.setFillAlpha(0.1)
    canvas.setFont("Helvetica", 30)
    canvas.rotate(45)
    canvas.drawString(2 * inch, -2 * inch, "CERTIFIED COPY")
    canvas.rotate(-45)
    canvas.setFillAlpha(1.0)
    canvas.setFillColor(colors.black)

    # Simulate scan artifacts
    canvas.setStrokeColor(colors.lightgrey, alpha=0.2)
    canvas.line(0, random.uniform(0, letter[1]), letter[0], random.uniform(0, letter[1]))
    canvas.restoreState()

# Function to create a section
def create_section(elements, title, content):
    elements.append(Paragraph(f"<b>{title}</b>", heading_style))
    for item in content:
        if isinstance(item, str):
            elements.append(Paragraph(item, normal_style))
        else:
            elements.append(item)
    elements.append(Spacer(1, 12))

# Function to generate a single PDF
def generate_single_pdf(filename, elements):
    try:
        if os.path.exists(filename):
            os.remove(filename)  # Remove existing file to avoid permission issues
        doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=108, bottomMargin=72)
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        print(f"PDF generated successfully: {filename}")
    except PermissionError as e:
        print(f"Error: Permission denied to write {filename}. Close the file or run with sufficient permissions. Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected issue occurred while generating {filename}. Details: {e}")

# Main PDF generation with separate files
def generate_pdfs(data):
    try:
        # Signature and notarization block
        signature_block = [
            Spacer(1, 12),
            Paragraph("<b>Seller Signature:</b> _______________________________", normal_style),
            Paragraph(f"Name: {data['seller_name']} | ID: {data['seller_id']} | Date: _______________________________", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Notary Public:</b>", normal_style),
            Paragraph(f"State of Florida | County of {data['county'].replace(' County', '')}", normal_style),
            Paragraph(f"Sworn to and subscribed before me on {data['transfer_date_1']} by {data['seller_name']} who is personally known to me or has produced {data['seller_id']} as identification.", normal_style),
            Paragraph("Notary Signature: _______________________________ | Seal: [Notary Seal - State of Florida]", normal_style),
            Paragraph(f"Commission #: {data['notary_commission']} | Expires: {data['notary_expires']}", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Clerk Certification:</b>", normal_style),
            Paragraph(f"I hereby certify that the foregoing instrument was filed and recorded on {data['transfer_date_1']} at 10:00 AM WAT in {data['county']} Public Records. [Seal]", normal_style),
            Paragraph(f"Deputy Clerk: {data['clerk_initials']} | Verified by Attorney: {data['attorney_name']}, {data['law_firm']}, {data['law_firm_location']}", normal_style),
        ]

        # 1. Warranty Deed (Jason Lucas to Bonnie Bryon)
        elements_1 = []
        create_section(elements_1, "Warranty Deed", [
            f"THIS WARRANTY DEED, executed on {data['transfer_date_1']} at 10:00 AM WAT, between {data['seller_name']}, whose address is {data['seller_location']}, Grantor, and {data['first_buyer_name']}, whose address is {data['first_buyer_address']}, Grantee,",
            f"WITNESSETH, that the Grantor, for and in consideration of the sum of {data['property_valuation']} and other good and valuable consideration, the receipt whereof is hereby acknowledged, has granted, bargained, sold, and conveyed to the Grantee, and Grantee's heirs and assigns forever, the following described property in {data['county']}, Florida:",
            f"Legal Description: {data['legal_description']}, Parcel ID: {data['parcel_id']} (Surveyor Cert. # {data['surveyor_cert']}).",
            f"TO HAVE AND TO HOLD the same in fee simple forever. The Grantor hereby covenants with the Grantee that the Grantor is lawfully seized of said land in fee simple; that the land is free from all encumbrances except as recorded in {data['book_page_1']}; and that the Grantor will warrant and defend the same against the lawful claims of all persons.",
            f"Recorded in Official Records {data['book_page_1']} of {data['county']} Public Records | Document Fee: $10.00 per Florida Statute 28.24 | Intangible Tax: $1,960.00 (0.2%)."
        ] + signature_block)
        generate_single_pdf("Warranty_Deed_1.pdf", elements_1)

        # 2. Warranty Deed (Bonnie Bryon to George A. Hansen)
        elements_2 = []
        create_section(elements_2, "Warranty Deed", [
            f"THIS WARRANTY DEED, executed on {data['transfer_date_2']} at 02:00 PM WAT, between {data['first_buyer_name']}, whose address is {data['first_buyer_address']}, Grantor, and {data['second_buyer_name']}, whose address is {data['second_buyer_address']}, Grantee,",
            f"WITNESSETH, that the Grantor, for and in consideration of the sum of {data['property_valuation']} and other good and valuable consideration, the receipt whereof is hereby acknowledged, has granted, bargained, sold, and conveyed to the Grantee, and Grantee's heirs and assigns forever, the following described property in {data['county']}, Florida:",
            f"Legal Description: {data['legal_description']}, Parcel ID: {data['parcel_id']} (Surveyor Cert. # {data['surveyor_cert']}).",
            f"TO HAVE AND TO HOLD the same in fee simple forever. The Grantor hereby covenants with the Grantee that the Grantor is lawfully seized of said land in fee simple; that the land is free from all encumbrances except as recorded in {data['book_page_2']}; and that the Grantor will warrant and defend the same against the lawful claims of all persons.",
            f"Recorded in Official Records {data['book_page_2']} of {data['county']} Public Records | Document Fee: $10.00 per Florida Statute 28.24 | Intangible Tax: $1,960.00 (0.2%)."
        ] + signature_block)
        generate_single_pdf("Warranty_Deed_2.pdf", elements_2)

        # 3. Title Transfer Request (Jason to Bonnie)
        elements_3 = []
        create_section(elements_3, "Title Transfer Request", [
            f"Request to transfer title of property located at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['seller_name']} to {data['first_buyer_name']} in {data['county']}, Florida.",
            f"Instrument Number: {data['instrument_number_1']} | Book/Page: {data['book_page_1']} | Filing Fee: $10.00 | Transfer Tax: $6,860.00 (0.70%) | Recorded: {data['transfer_date_1']}."
        ] + signature_block)
        generate_single_pdf("Title_Transfer_Request_1.pdf", elements_3)

        # 4. Title Transfer Request (Bonnie to George)
        elements_4 = []
        create_section(elements_4, "Title Transfer Request", [
            f"Request to transfer title of property located at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['first_buyer_name']} to {data['second_buyer_name']} in {data['county']}, Florida.",
            f"Instrument Number: {data['instrument_number_2']} | Book/Page: {data['book_page_2']} | Filing Fee: $10.00 | Transfer Tax: $6,860.00 (0.70%) | Recorded: {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Title_Transfer_Request_2.pdf", elements_4)

        # 5. Affidavit of Ownership
        elements_5 = []
        create_section(elements_5, "Affidavit of Ownership", [
            f"STATE OF FLORIDA | COUNTY OF {data['county'].replace(' County', '')}",
            f"BEFORE ME, the undersigned authority, personally appeared {data['seller_name']}, who being duly sworn, deposes and says that they are the owner of the property located at {data['property_address']} (Parcel ID: {data['parcel_id']}), free of any liens except those recorded in {data['book_page_1']}."
        ] + signature_block)
        generate_single_pdf("Affidavit_of_Ownership.pdf", elements_5)

        # 6. Property Appraisal Report
        elements_6 = []
        create_section(elements_6, "Property Appraisal Report", [
            f"Appraised Value: {data['property_valuation']} as of {data['transfer_date_1']} by {data['county']} Property Appraiser Office, Appraisal ID: {data['appraisal_id']}, Parcel ID: {data['parcel_id']} (Cert. # {data['surveyor_cert']})."
        ])
        generate_single_pdf("Property_Appraisal_Report.pdf", elements_6)

        # 7. Statement of Consideration (Jason to Bonnie)
        elements_7 = []
        create_section(elements_7, "Statement of Consideration", [
            f"Consideration for transfer: {data['property_valuation']} via {data['payment_method']} as per Florida Statute 689.01. Documentary Stamp Tax: $6,860.00 (0.70%) | Intangible Tax: $1,960.00 (0.2%).",
            f"Certified by {data['county']} Tax Collector, Receipt #: 6789 | Transaction ID: 9876543210 | Date: {data['transfer_date_1']}."
        ] + signature_block)
        generate_single_pdf("Statement_of_Consideration_1.pdf", elements_7)

        # 8. Statement of Consideration (Bonnie to George)
        elements_8 = []
        create_section(elements_8, "Statement of Consideration", [
            f"Consideration for transfer: {data['property_valuation']} via {data['payment_method']} as per Florida Statute 689.01. Documentary Stamp Tax: $6,860.00 (0.70%) | Intangible Tax: $1,960.00 (0.2%).",
            f"Certified by {data['county']} Tax Collector, Receipt #: 6790 | Transaction ID: 9876543220 | Date: {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Statement_of_Consideration_2.pdf", elements_8)

        # 9. Documentary Stamp Tax Receipt (Jason to Bonnie)
        elements_9 = []
        create_section(elements_9, "Documentary Stamp Tax Receipt", [
            f"Receipt for Documentary Stamp Tax: $6,860.00 (0.70% of {data['property_valuation']}) per Florida Statute 201.02 for {data['property_address']} (Parcel ID: {data['parcel_id']}). "
            f"Paid on {data['transfer_date_1']} | Receipt #: 6789 | Issued by {data['county']} Tax Collector Office."
        ])
        generate_single_pdf("Documentary_Stamp_Tax_Receipt_1.pdf", elements_9)

        # 10. Documentary Stamp Tax Receipt (Bonnie to George)
        elements_10 = []
        create_section(elements_10, "Documentary Stamp Tax Receipt", [
            f"Receipt for Documentary Stamp Tax: $6,860.00 (0.70% of {data['property_valuation']}) per Florida Statute 201.02 for {data['property_address']} (Parcel ID: {data['parcel_id']}). "
            f"Paid on {data['transfer_date_2']} | Receipt #: 6790 | Issued by {data['county']} Tax Collector Office."
        ])
        generate_single_pdf("Documentary_Stamp_Tax_Receipt_2.pdf", elements_10)

        # 11. Tax Clearance Certificate
        elements_11 = []
        create_section(elements_11, "Tax Clearance Certificate", [
            f"Certificate issued by {data['county']} Tax Collector confirming all property taxes are cleared for {data['property_address']} (Parcel ID: {data['parcel_id']}) as of {data['transfer_date_2']}."
            f"Certificate #: 9012 | Valid Until: June 30, 2026 | Issued: {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Tax_Clearance_Certificate.pdf", elements_11)

        # 12. Utility Clearance Certificate
        elements_12 = []
        create_section(elements_12, "Utility Clearance Certificate", [
            f"Utilities cleared for {data['property_address']} (Account #: {data['utility_account']}) by Miami-Dade County Water and Sewer Department as of {data['transfer_date_2']}."
            f"Clearance #: 3456 | Issued by: Miami-Dade County Utilities | Date: {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Utility_Clearance_Certificate.pdf", elements_12)

        # 13. Proof of Identity
        elements_13 = []
        create_section(elements_13, "Proof of Identity", [
            f"Seller: {data['seller_name']} | ID: {data['seller_id']} | Verified by Notary on {data['transfer_date_1']}",
            f"First Buyer: {data['first_buyer_name']} | ID: {data['first_buyer_id']} | Verified by Notary on {data['transfer_date_1']}",
            f"Second Buyer: {data['second_buyer_name']} | ID: {data['second_buyer_id']} | Verified by Notary on {data['transfer_date_2']}"
        ])
        generate_single_pdf("Proof_of_Identity.pdf", elements_13)

        # 14. Notarized Transfer Authorization Letter (Jason to Bonnie)
        elements_14 = []
        create_section(elements_14, "Notarized Transfer Authorization Letter", [
            f"I, {data['seller_name']}, residing at {data['seller_location']}, authorize the transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['first_buyer_name']} under Florida Statute 689.01. Attorney: {data['attorney_name']}, {data['law_firm']}, {data['law_firm_location']}."
        ] + signature_block)
        generate_single_pdf("Notarized_Transfer_Authorization_Letter_1.pdf", elements_14)

        # 15. Notarized Transfer Authorization Letter (Bonnie to George)
        elements_15 = []
        create_section(elements_15, "Notarized Transfer Authorization Letter", [
            f"I, {data['first_buyer_name']}, residing at {data['first_buyer_address']}, authorize the transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['second_buyer_name']} under Florida Statute 689.01. Attorney: {data['attorney_name']}, {data['law_firm']}, {data['law_firm_location']}."
        ] + signature_block)
        generate_single_pdf("Notarized_Transfer_Authorization_Letter_2.pdf", elements_15)

        # 16. Power of Attorney (Optional, for Bonnie)
        elements_16 = []
        create_section(elements_16, "Power of Attorney", [
            f"Power of Attorney granted by {data['first_buyer_name']} to [Agent Name] for property transfer, per Florida Statute 709.2101."
            f"POA #: 345678 | Recorded in {data['book_page_2']} | Effective: {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Power_of_Attorney.pdf", elements_16)

        # 17. Bank Compliance Letter
        elements_17 = []
        create_section(elements_17, "Bank Compliance Letter", [
            f"United States Banking Corporation confirms compliance for account ending XXXXX2089, balance ${data['property_valuation']}, for {data['seller_name']}."
            f"Compliance Cert #: 5678 | Issued: {data['transfer_date_1']} | Branch: Ann Arbor, MI."
        ] + signature_block)
        generate_single_pdf("Bank_Compliance_Letter.pdf", elements_17)

        # 18. Wire Transfer Confirmation (Jason to Bonnie)
        elements_18 = []
        create_section(elements_18, "Wire Transfer Confirmation", [
            f"Wire transfer of ${data['property_valuation']} from {data['seller_name']} (Account XXXXX2089) to {data['first_buyer_name']} on {data['transfer_date_1']} at 10:00 AM WAT."
            f"Transaction ID: 9876543210 | Bank Ref #: 654321 | SWIFT: USBKUS33."
        ])
        generate_single_pdf("Wire_Transfer_Confirmation_1.pdf", elements_18)

        # 19. Wire Transfer Confirmation (Bonnie to George)
        elements_19 = []
        create_section(elements_19, "Wire Transfer Confirmation", [
            f"Wire transfer of ${data['property_valuation']} from {data['first_buyer_name']} (Account XXXXX2090) to {data['second_buyer_name']} on {data['transfer_date_2']} at 02:00 PM WAT."
            f"Transaction ID: 9876543220 | Bank Ref #: 654322 | SWIFT: USBKUS33."
        ])
        generate_single_pdf("Wire_Transfer_Confirmation_2.pdf", elements_19)

        # 20. FIRPTA Disclosure (Bonnie Bryon)
        if data["first_buyer_nationality"] != "U.S.":
            elements_20 = []
            create_section(elements_20, "FIRPTA Disclosure", [
                f"Foreign Investment in Real Property Tax Act (FIRPTA) disclosure for {data['first_buyer_name']}, a {data['first_buyer_nationality']} citizen, per 26 U.S.C. § 1445."
                f"Withholding Certificate #: 456789 | Withholding Amount: $98,000.00 (10%)."
            ] + signature_block)
            generate_single_pdf("FIRPTA_Disclosure.pdf", elements_20)

        # 21. Apostille Request
        if data["require_apostille"]:
            elements_21 = []
            create_section(elements_21, "Apostille Request", [
                f"Request for Apostille for transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['first_buyer_name']} in Canada, per The Hague Convention of 1961."
                f"Request #: 9012 | Submitted to Florida Secretary of State on {data['transfer_date_1']}."
            ] + signature_block)
            generate_single_pdf("Apostille_Request.pdf", elements_21)

    except ImportError as e:
        print(f"Error: Missing dependency. Please install reportlab with 'pip install reportlab'. Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected issue occurred. Details: {e}")

if __name__ == "__main__":
    generate_pdfs(data)
