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

# Customized data with dates between March 4-7, 2025 (unless overridden)
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
    "law_firm_location": "Ohio",
    # Additional data from USBC letter
    "bank_name": "USBC - United States Banking Corporation",
    "bank_branch": "Detroit Branch",
    "bank_address": "500 Woodward Ave, Detroit, MI 48226",
    "bank_phone": "(313) 555-4490",
    "bank_email": "noreply@usbc.com",
    "compliance_counsel": "Law Offices of A. H. Bennett, Esq. - Compliance Counsel",
    "counsel_email": "ahbennett@usbc.com",
    "letter_date": "June 17, 2025",  # Specific date from the provided document
    "account_number": "XXXXX2089",
    "account_balance": "$967,000.00",
    "recipient_name": "Mr. Jason Lucas",
    "recipient_address": "123 Client Residence Blvd, Detroit, MI 48210",
    "subject": "Final Notice - Dormant Account and State Escheatment",
    "deadline_date": "June 20, 2025",
    "issuer_name": "A. H. Bennett, Esq.",
    "issuer_title": "Senior Legal Advisor - Dormancy Compliance Unit"
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

# Function to add header and footer with color (no watermark)
def add_header_footer(canvas, doc):
    canvas.saveState()
    # Colored header (blue background with white text)
    canvas.setFillColor(colors.blue)
    canvas.rect(0, letter[1] - 1.5 * inch, letter[0], 1.5 * inch, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(inch, letter[1] - 0.75 * inch, f"{data['bank_name']}")
    canvas.setFont("Times-Roman", 10)
    canvas.drawString(inch, letter[1] - 1 * inch, f"{data['bank_branch']} - {data['bank_address']}")
    canvas.drawString(inch, letter[1] - 1.25 * inch, f"Phone: {data['bank_phone']} | Email: {data['bank_email']}")
    canvas.drawString(inch, letter[1] - 1.5 * inch, f"Compliance Counsel: {data['compliance_counsel']} | Email: {data['counsel_email']}")

    # Colored seal (gray with black text)
    canvas.setFillColor(colors.lightgrey)
    canvas.circle(inch + 6 * inch, letter[1] - 1.5 * inch, 0.5 * inch, fill=1)
    canvas.setFillColor(colors.black)
    canvas.drawString(inch + 5.5 * inch, letter[1] - 1.75 * inch, "[Official Seal]")

    # Footer with page number
    canvas.setFillColor(colors.black)
    canvas.setFont("Times-Roman", 8)
    page_num = canvas.getPageNumber()
    canvas.drawString(letter[0] - 2 * inch, 0.25 * inch, f"Page {page_num}")

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
        # Signature block (adapted from the letter format)
        signature_block = [
            Spacer(1, 12),
            Paragraph(f"{data['issuer_name']}", normal_style),
            Paragraph(f"{data['issuer_title']}", normal_style),
            Paragraph(f"{data['bank_name']}", normal_style),
            Paragraph(f"Issued under the supervision of legal counsel in compliance with Michigan state law.", normal_style)
        ]

        # 1. Warranty Deed (Jason Lucas to Bonnie Bryon)
        elements_1 = []
        create_section(elements_1, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Property Transfer - {data['property_address']}"
        ])
        create_section(elements_1, "", [
            f"Dear {data['first_buyer_name']},",
            f"This is to confirm the transfer of the property located at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['seller_name']} to you, executed on {data['transfer_date_1']} at 10:00 AM WAT, for a consideration of {data['property_valuation']} via {data['payment_method']}."
        ] + signature_block)
        generate_single_pdf("Warranty_Deed_1.pdf", elements_1)

        # 2. Warranty Deed (Bonnie Bryon to George A. Hansen)
        elements_2 = []
        create_section(elements_2, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Property Transfer - {data['property_address']}"
        ])
        create_section(elements_2, "", [
            f"Dear {data['second_buyer_name']},",
            f"This is to confirm the transfer of the property located at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['first_buyer_name']} to you, executed on {data['transfer_date_2']} at 02:00 PM WAT, for a consideration of {data['property_valuation']} via {data['payment_method']}."
        ] + signature_block)
        generate_single_pdf("Warranty_Deed_2.pdf", elements_2)

        # 3. Title Transfer Request (Jason to Bonnie)
        elements_3 = []
        create_section(elements_3, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Title Transfer Request - {data['property_address']}"
        ])
        create_section(elements_3, "", [
            f"Dear {data['first_buyer_name']},",
            f"This is a request to transfer the title of the property at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['seller_name']} to you. Details: Instrument Number {data['instrument_number_1']}, Book/Page {data['book_page_1']}, Recorded {data['transfer_date_1']}."
        ] + signature_block)
        generate_single_pdf("Title_Transfer_Request_1.pdf", elements_3)

        # 4. Title Transfer Request (Bonnie to George)
        elements_4 = []
        create_section(elements_4, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Title Transfer Request - {data['property_address']}"
        ])
        create_section(elements_4, "", [
            f"Dear {data['second_buyer_name']},",
            f"This is a request to transfer the title of the property at {data['property_address']} (Parcel ID: {data['parcel_id']}) from {data['first_buyer_name']} to you. Details: Instrument Number {data['instrument_number_2']}, Book/Page {data['book_page_2']}, Recorded {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Title_Transfer_Request_2.pdf", elements_4)

        # 5. Affidavit of Ownership
        elements_5 = []
        create_section(elements_5, f"Date: {data['transfer_date_1']}", [
            f"To: {data['county']} Clerk of the Court",
            f"Subject: Affidavit of Ownership - {data['property_address']}"
        ])
        create_section(elements_5, "", [
            f"Dear Sir/Madam,",
            f"I, {data['seller_name']}, affirm that I am the owner of the property at {data['property_address']} (Parcel ID: {data['parcel_id']}), free of liens except those recorded in {data['book_page_1']}."
        ] + signature_block)
        generate_single_pdf("Affidavit_of_Ownership.pdf", elements_5)

        # 6. Property Appraisal Report
        elements_6 = []
        create_section(elements_6, f"Date: {data['transfer_date_1']}", [
            f"To: {data['county']} Property Appraiser Office",
            f"Subject: Appraisal Report - {data['property_address']}"
        ])
        create_section(elements_6, "", [
            f"Dear Sir/Madam,",
            f"The appraised value of the property at {data['property_address']} (Parcel ID: {data['parcel_id']}) is {data['property_valuation']} as of {data['transfer_date_1']}, Appraisal ID: {data['appraisal_id']}."
        ] + signature_block)
        generate_single_pdf("Property_Appraisal_Report.pdf", elements_6)

        # 7. Statement of Consideration (Jason to Bonnie)
        elements_7 = []
        create_section(elements_7, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Statement of Consideration - {data['property_address']}"
        ])
        create_section(elements_7, "", [
            f"Dear {data['first_buyer_name']},",
            f"Consideration for the transfer of {data['property_address']} is {data['property_valuation']} via {data['payment_method']}, with Documentary Stamp Tax: $6,860.00 and Intangible Tax: $1,960.00, certified on {data['transfer_date_1']}."
        ] + signature_block)
        generate_single_pdf("Statement_of_Consideration_1.pdf", elements_7)

        # 8. Statement of Consideration (Bonnie to George)
        elements_8 = []
        create_section(elements_8, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Statement of Consideration - {data['property_address']}"
        ])
        create_section(elements_8, "", [
            f"Dear {data['second_buyer_name']},",
            f"Consideration for the transfer of {data['property_address']} is {data['property_valuation']} via {data['payment_method']}, with Documentary Stamp Tax: $6,860.00 and Intangible Tax: $1,960.00, certified on {data['transfer_date_2']}."
        ] + signature_block)
        generate_single_pdf("Statement_of_Consideration_2.pdf", elements_8)

        # 9. Documentary Stamp Tax Receipt (Jason to Bonnie)
        elements_9 = []
        create_section(elements_9, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Documentary Stamp Tax Receipt - {data['property_address']}"
        ])
        create_section(elements_9, "", [
            f"Dear {data['first_buyer_name']},",
            f"Receipt for Documentary Stamp Tax: $6,860.00 (0.70% of {data['property_valuation']}) for {data['property_address']} (Parcel ID: {data['parcel_id']}), paid on {data['transfer_date_1']}, Receipt #: 6789."
        ] + signature_block)
        generate_single_pdf("Documentary_Stamp_Tax_Receipt_1.pdf", elements_9)

        # 10. Documentary Stamp Tax Receipt (Bonnie to George)
        elements_10 = []
        create_section(elements_10, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Documentary Stamp Tax Receipt - {data['property_address']}"
        ])
        create_section(elements_10, "", [
            f"Dear {data['second_buyer_name']},",
            f"Receipt for Documentary Stamp Tax: $6,860.00 (0.70% of {data['property_valuation']}) for {data['property_address']} (Parcel ID: {data['parcel_id']}), paid on {data['transfer_date_2']}, Receipt #: 6790."
        ] + signature_block)
        generate_single_pdf("Documentary_Stamp_Tax_Receipt_2.pdf", elements_10)

        # 11. Tax Clearance Certificate
        elements_11 = []
        create_section(elements_11, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Tax Clearance Certificate - {data['property_address']}"
        ])
        create_section(elements_11, "", [
            f"Dear {data['second_buyer_name']},",
            f"Certificate confirming all property taxes are cleared for {data['property_address']} (Parcel ID: {data['parcel_id']}) as of {data['transfer_date_2']}, Certificate #: 9012, Valid Until: June 30, 2026."
        ] + signature_block)
        generate_single_pdf("Tax_Clearance_Certificate.pdf", elements_11)

        # 12. Utility Clearance Certificate
        elements_12 = []
        create_section(elements_12, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Utility Clearance Certificate - {data['property_address']}"
        ])
        create_section(elements_12, "", [
            f"Dear {data['second_buyer_name']},",
            f"Utilities cleared for {data['property_address']} (Account #: {data['utility_account']}) as of {data['transfer_date_2']}, Clearance #: 3456."
        ] + signature_block)
        generate_single_pdf("Utility_Clearance_Certificate.pdf", elements_12)

        # 13. Proof of Identity
        elements_13 = []
        create_section(elements_13, f"Date: {data['transfer_date_1']}", [
            f"To: {data['county']} Clerk of the Court",
            f"Subject: Proof of Identity - {data['property_address']}"
        ])
        create_section(elements_13, "", [
            f"Dear Sir/Madam,",
            f"Proof of Identity: {data['seller_name']} (ID: {data['seller_id']}), {data['first_buyer_name']} (ID: {data['first_buyer_id']}), {data['second_buyer_name']} (ID: {data['second_buyer_id']}), verified on {data['transfer_date_1']}."
        ] + signature_block)
        generate_single_pdf("Proof_of_Identity.pdf", elements_13)

        # 14. Notarized Transfer Authorization Letter (Jason to Bonnie)
        elements_14 = []
        create_section(elements_14, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Transfer Authorization - {data['property_address']}"
        ])
        create_section(elements_14, "", [
            f"Dear {data['first_buyer_name']},",
            f"I, {data['seller_name']}, authorize the transfer of {data['property_address']} to you under Florida Statute 689.01, Attorney: {data['attorney_name']}, {data['law_firm']}, {data['law_firm_location']}."
        ] + signature_block)
        generate_single_pdf("Notarized_Transfer_Authorization_Letter_1.pdf", elements_14)

        # 15. Notarized Transfer Authorization Letter (Bonnie to George)
        elements_15 = []
        create_section(elements_15, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Transfer Authorization - {data['property_address']}"
        ])
        create_section(elements_15, "", [
            f"Dear {data['second_buyer_name']},",
            f"I, {data['first_buyer_name']}, authorize the transfer of {data['property_address']} to you under Florida Statute 689.01, Attorney: {data['attorney_name']}, {data['law_firm']}, {data['law_firm_location']}."
        ] + signature_block)
        generate_single_pdf("Notarized_Transfer_Authorization_Letter_2.pdf", elements_15)

        # 16. Power of Attorney (Optional, for Bonnie)
        elements_16 = []
        create_section(elements_16, f"Date: {data['transfer_date_2']}", [
            f"To: {data['county']} Clerk of the Court",
            f"Subject: Power of Attorney - {data['property_address']}"
        ])
        create_section(elements_16, "", [
            f"Dear Sir/Madam,",
            f"Power of Attorney granted by {data['first_buyer_name']} to [Agent Name] for property transfer, per Florida Statute 709.2101, POA #: 345678, Recorded in {data['book_page_2']}."
        ] + signature_block)
        generate_single_pdf("Power_of_Attorney.pdf", elements_16)

        # 17. Bank Compliance Letter (Inspired by USBC letter)
        elements_17 = []
        create_section(elements_17, f"Date: {data['letter_date']}", [
            f"To: {data['recipient_name']}",
            f"{data['recipient_address']}",
            f"Subject: {data['subject']}"
        ])
        create_section(elements_17, "", [
            f"Dear {data['recipient_name']},",
            f"This is an official notice concerning your account ending in {data['account_number']}, which currently holds a balance of {data['account_balance']}. This account has been inactive. In accordance with the Michigan Unclaimed Property Act, USBC is obligated to report and transfer dormant funds to the Michigan Department of Treasury if no action is taken by {data['deadline_date']}."
        ] + signature_block)
        generate_single_pdf("Bank_Compliance_Letter.pdf", elements_17)

        # 18. Wire Transfer Confirmation (Jason to Bonnie)
        elements_18 = []
        create_section(elements_18, f"Date: {data['transfer_date_1']}", [
            f"To: {data['first_buyer_name']}",
            f"{data['first_buyer_address']}",
            f"Subject: Wire Transfer Confirmation - {data['property_address']}"
        ])
        create_section(elements_18, "", [
            f"Dear {data['first_buyer_name']},",
            f"Wire transfer of {data['property_valuation']} from {data['seller_name']} (Account {data['account_number']}) to you on {data['transfer_date_1']} at 10:00 AM WAT, Transaction ID: 9876543210."
        ] + signature_block)
        generate_single_pdf("Wire_Transfer_Confirmation_1.pdf", elements_18)

        # 19. Wire Transfer Confirmation (Bonnie to George)
        elements_19 = []
        create_section(elements_19, f"Date: {data['transfer_date_2']}", [
            f"To: {data['second_buyer_name']}",
            f"{data['second_buyer_address']}",
            f"Subject: Wire Transfer Confirmation - {data['property_address']}"
        ])
        create_section(elements_19, "", [
            f"Dear {data['second_buyer_name']},",
            f"Wire transfer of {data['property_valuation']} from {data['first_buyer_name']} (Account XXXXX2090) to you on {data['transfer_date_2']} at 02:00 PM WAT, Transaction ID: 9876543220."
        ] + signature_block)
        generate_single_pdf("Wire_Transfer_Confirmation_2.pdf", elements_19)

        # 20. FIRPTA Disclosure (Bonnie Bryon)
        if data["first_buyer_nationality"] != "U.S.":
            elements_20 = []
            create_section(elements_20, f"Date: {data['transfer_date_1']}", [
                f"To: {data['first_buyer_name']}",
                f"{data['first_buyer_address']}",
                f"Subject: FIRPTA Disclosure - {data['property_address']}"
            ])
            create_section(elements_20, "", [
                f"Dear {data['first_buyer_name']},",
                f"Foreign Investment in Real Property Tax Act (FIRPTA) disclosure for you, a {data['first_buyer_nationality']} citizen, per 26 U.S.C. § 1445, Withholding Certificate #: 456789, Withholding Amount: $98,000.00 (10%)."
            ] + signature_block)
            generate_single_pdf("FIRPTA_Disclosure.pdf", elements_20)

        # 21. Apostille Request
        if data["require_apostille"]:
            elements_21 = []
            create_section(elements_21, f"Date: {data['transfer_date_1']}", [
                f"To: Florida Secretary of State",
                f"Subject: Apostille Request - {data['property_address']}"
            ])
            create_section(elements_21, "", [
                f"Dear Sir/Madam,",
                f"Request for Apostille for transfer of {data['property_address']} (Parcel ID: {data['parcel_id']}) to {data['first_buyer_name']} in Canada, per The Hague Convention of 1961, Request #: 9012, Submitted on {data['transfer_date_1']}."
            ] + signature_block)
            generate_single_pdf("Apostille_Request.pdf", elements_21)

    except ImportError as e:
        print(f"Error: Missing dependency. Please install reportlab with 'pip install reportlab'. Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected issue occurred. Details: {e}")

if __name__ == "__main__":
    generate_pdfs(data)
