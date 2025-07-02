from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Circle, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import names
import random

# Register a font for better text rendering
pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))

def generate_random_folio_number():
    return f"30-4217-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_random_name():
    return names.get_full_name()

def generate_random_address(city="Key Biscayne", state="FL"):
    streets = ["Crandon Blvd", "Ocean Dr", "Harbor Dr", "Mashta Dr"]
    return f"{random.randint(100, 9999)} {random.choice(streets)}, {city}, {state} 33149"

def create_seal(x, y, label, canvas):
    d = Drawing(50, 50)
    c = Circle(25, 25, 20, fillColor=colors.lightgrey)
    s = String(25, 25, label, fontName="Helvetica", fontSize=6, textAnchor="middle")
    d.add(c)
    d.add(s)
    renderPDF.draw(d, canvas, x, y)

def create_stamp(x, y, text, canvas):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.red)
    canvas.drawString(x, y, text)

def create_signature_line(x, y, name, title, canvas):
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(x, y, "_______________________________")
    canvas.drawString(x, y - 12, f"{name}")
    canvas.drawString(x, y - 24, f"{title}")

def create_pdf_document(filename, elements, add_page_numbers=True):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    def page_numbers(canvas, doc):
        if add_page_numbers:
            page_num = canvas.getPageNumber()
            text = f"Page {page_num}"
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(doc.rightMargin + doc.width, 0.5*inch, text)
    
    def add_seals_stamps_signatures(canvas, doc):
        # Add seals, stamps, and signatures based on document type
        filename = doc.filename
        if "Deed_of_Ownership" in filename:
            create_seal(400, 600, "Notary Seal", canvas)
            create_stamp(400, 580, "Filed with Miami-Dade Clerk, March 7, 2025", canvas)
            create_signature_line(400, 550, deed_data[0 if '1' not in filename else 1]['notary']['name'], "Notary Public", canvas)
            create_signature_line(400, 500, deed_data[0 if '1' not in filename else 1]['grantor']['name'], "Grantor", canvas)
        elif "Affidavit_of_Ownership" in filename:
            create_seal(400, 600, "Notary Seal", canvas)
            create_signature_line(400, 550, owner['notary']['name'], "Notary Public", canvas)
            create_signature_line(400, 500, owner['name'], "Affiant", canvas)
        elif "Tax_Clearance_Certificate" in filename:
            create_seal(400, 600, "Official Seal", canvas)
            create_stamp(400, 580, "Approved by Miami-Dade Tax Collector", canvas)
            create_signature_line(400, 550, "Dariel Fernandez", "Tax Collector", canvas)
        elif "Utility_Clearance_Certificate" in filename:
            create_seal(400, 600, "Official Seal", canvas)
            create_stamp(400, 580, "Verified by Miami-Dade Water Dept", canvas)
            create_signature_line(400, 550, "Utility Officer", "Department Head", canvas)
        elif "Proof_of_Identity" in filename:
            create_seal(400, 600, "Notary Seal", canvas)
            create_signature_line(400, 550, parties[0]['notary']['name'], "Notary Public", canvas)
        elif "Appraisal_Report" in filename:
            create_seal(400, 600, "Appraiser Seal", canvas)
            create_signature_line(400, 550, generate_random_name(), "Licensed Appraiser", canvas)
        elif "Statement_of_Consideration" in filename:
            create_stamp(400, 580, "Recorded with Miami-Dade Clerk", canvas)
            create_signature_line(400, 550, deed_data[1]['prepared_by']['name'], "Attorney", canvas)
        elif "Transfer_Authorization_Letter" in filename:
            create_stamp(400, 580, "Approved by Ocean Tower One", canvas)
            create_signature_line(400, 550, grantor['name'], "Grantor", canvas)
        elif "Bank_Compliance_Letter" in filename:
            create_seal(400, 600, "Bank Seal", canvas)
            create_signature_line(400, 550, "[Bank Officer Name]", "Vice President", canvas)

    doc.build(elements, onFirstPage=page_numbers, onLaterPages=page_numbers, onLaterPages=add_seals_stamps_signatures)
    print(f"PDF generated successfully: {filename}")

def create_deed_of_ownership(deed_data):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    notary_style = ParagraphStyle('NotaryStyle', parent=styles['BodyText'], fontSize=9, leading=12, spaceAfter=0.1*inch)
    
    doc_stamp_tax = (deed_data['sale_price'] / 100) * 0.60 + (deed_data['sale_price'] / 100) * 0.45
    doc_stamp_text = f"Documentary Stamp Tax: ${doc_stamp_tax:.2f} paid to the Clerk of the Circuit Court, Miami-Dade County."
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph(f"{deed_data['deed_type'].upper()} DEED", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"Prepared by: {deed_data['prepared_by']['name']}<br/>{deed_data['prepared_by']['address']}<br/>SWBW Law Firm, Columbus, OH", body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"""
        THIS {deed_data['deed_type'].upper()} DEED, executed this {deed_data['transfer_date']}, by {deed_data['grantor']['name']}, whose address is {deed_data['grantor']['address']}, hereinafter called the Grantor, to {deed_data['grantee']['name']}, whose address is {deed_data['grantee']['address']}, hereinafter called the Grantee.<br/><br/>
        WITNESSETH, that the Grantor, for and in consideration of the sum of ${deed_data['sale_price']:,.2f} and other valuable consideration, the receipt whereof is hereby acknowledged, hereby grants, bargains, sells, aliens, remises, releases, conveys, and confirms unto the Grantee, all that certain land situated in Miami-Dade County, Florida, described as follows:<br/><br/>
        <b>Property Address:</b> {deed_data['property_address']}<br/>
        <b>Legal Description:</b> {deed_data['legal_description']}<br/>
        <b>Folio Number:</b> {deed_data['folio_number']}<br/><br/>
        TOGETHER with all the tenements, hereditaments, and appurtenances thereto belonging or in anywise appertaining.<br/><br/>
        TO HAVE AND TO HOLD the same in fee simple forever.<br/><br/>
        {doc_stamp_text}<br/><br/>
        <b>Verification:</b> Property details verified with Miami-Dade County Property Appraiser records (www.miamidadepa.gov) as of {deed_data['transfer_date']}. Title search conducted by Key Title Services, Inc., confirming clear title. Ocean Tower One Condominium Association approval granted on {deed_data['transfer_date']}. Property Fraud Alert registered with Miami-Dade Clerk of Courts (www.miamidadeclerk.gov) per HB 1419.<br/><br/>
        <b>Note:</b> Seals, stamps, and signatures are simulated placeholders. Replace with official versions from authorized entities.
        """, body_style),
        Spacer(1, 0.25*inch),
        Paragraph("IN WITNESS WHEREOF, the Grantor has hereunto set their hand and seal on the day and year first above written.", body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Signed, sealed, and delivered in the presence of:", body_style),
        Spacer(1, 0.1*inch),
        Paragraph(f"Witness 1: _______________________________<br/>Name: {deed_data['witnesses'][0]['name']}<br/>Address: {deed_data['witnesses'][0]['address']}", body_style),
        Paragraph(f"Witness 2: _______________________________<br/>Name: {deed_data['witnesses'][1]['name']}<br/>Address: {deed_data['witnesses'][1]['address']}", body_style),
        Paragraph(f"Grantor: _______________________________<br/>Name: {deed_data['grantor']['name']}", body_style),
        Paragraph(f"""
        State of Florida<br/>
        County of Miami-Dade<br/><br/>
        The foregoing instrument was acknowledged before me by means of [ ] physical presence or [ ] online notarization, this {deed_data['transfer_date']}, by {deed_data['grantor']['name']}, who is personally known to me or who has produced ____________________ as identification.
        """, notary_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"Return to:<br/>{deed_data['prepared_by']['name']}<br/>{deed_data['prepared_by']['address']}", body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: This deed has been reviewed and approved by SWBW Law Firm, ensuring compliance with Florida Statutes § 695.26. Contact: Brian, SWBW Law Firm, 123 Main St, Columbus, OH 43215.", body_style)
    ]
    
    create_pdf_document(deed_data['filename'], elements)

def create_affidavit_of_ownership(filename, owner, property_address, legal_description, folio_number, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    notary_style = ParagraphStyle('NotaryStyle', parent=styles['BodyText'], fontSize=9, leading=12, spaceAfter=0.1*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("AFFIDAVIT OF OWNERSHIP", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        STATE OF FLORIDA<br/>
        COUNTY OF MIAMI-DADE<br/><br/>
        Before me, the undersigned authority, personally appeared {owner['name']}, who, being duly sworn, deposes and says:<br/><br/>
        1. That the affiant is the owner of the property located at {property_address}.<br/>
        2. That the legal description of the property is as follows: {legal_description}.<br/>
        3. That the folio number of the property is {folio_number}.<br/>
        4. That the affiant has full legal right and authority to convey the property.<br/>
        5. That there are no liens, encumbrances, or claims against the property except as noted in the deed.<br/>
        6. That the property details have been verified with the Miami-Dade County Property Appraiser (www.miamidadepa.gov) as of {date}.<br/>
        7. That the Ocean Tower One Condominium Association has confirmed compliance with all association rules for this transfer.<br/><br/>
        <b>Note:</b> Seals and signatures are simulated placeholders. Replace with official versions from a notary public.<br/><br/>
        Affiant: _______________________________<br/>
        Name: {owner['name']}<br/>
        Address: {owner['address']}
        """, body_style),
        Paragraph(f"""
        Sworn to and subscribed before me this {date}, by {owner['name']}, who is personally known to me or who has produced ____________________ as identification.
        """, notary_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: This affidavit has been reviewed by SWBW Law Firm, ensuring compliance with Florida Statutes. Contact: Brian, SWBW Law Firm, 123 Main St, Columbus, OH 43215.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_tax_clearance_certificate(filename, owner, property_address, folio_number, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("TAX CLEARANCE CERTIFICATE", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        MIAMI-DADE COUNTY TAX COLLECTOR<br/>
        111 NW 1st Street, Miami, FL 33128<br/><br/>
        This is to certify that all property taxes for the property located at:<br/><br/>
        <b>Property Address:</b> {property_address}<br/>
        <b>Folio Number:</b> {folio_number}<br/>
        <b>Owner:</b> {owner['name']}<br/><br/>
        have been paid in full as of {date}, per records verified with the Miami-Dade County Property Appraiser (www.miamidadepa.gov). No outstanding property taxes, assessments, or liens are recorded against this property.<br/><br/>
        <b>Note:</b> Seal and signature are simulated placeholders. Replace with official versions from the Miami-Dade Tax Collector.<br/><br/>
        Certificate Number: TCC-{random.randint(100000, 999999)}
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: Verified by SWBW Law Firm for compliance with Florida Statutes § 193.122.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_utility_clearance_certificate(filename, owner, property_address, utility_accounts, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("UTILITY CLEARANCE CERTIFICATE", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        MIAMI-DADE COUNTY WATER AND SEWER DEPARTMENT<br/>
        3071 SW 38th Ave, Miami, FL 33146<br/><br/>
        This is to certify that all utility bills for the property located at:<br/><br/>
        <b>Property Address:</b> {property_address}<br/>
        <b>Owner:</b> {owner['name']}<br/><br/>
        have been paid in full as of {date}. The following utility accounts are clear:<br/>
        - Water Account: {utility_accounts['water']}<br/>
        - Electric Account: {utility_accounts['electric']}<br/>
        - Gas Account: {utility_accounts['gas']}<br/><br/>
        <b>Note:</b> Seal and stamp are simulated placeholders. Replace with official versions from the Miami-Dade Water Department.<br/><br/>
        Certificate Number: UCC-{random.randint(100000, 999999)}
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: Verified by SWBW Law Firm for accuracy.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_proof_of_identity(filename, parties, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("PROOF OF IDENTITY", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        STATE OF FLORIDA<br/>
        COUNTY OF MIAMI-DADE<br/><br/>
        The undersigned notary public certifies that the following individuals appeared before me on {date} and provided satisfactory proof of identity, verified through the Miami-Dade County Tax Collector’s identification system:<br/><br/>
        """, body_style)
    ]
    
    for party in parties:
        elements.append(Paragraph(f"""
        Name: {party['name']}<br/>
        Address: {party['address']}<br/>
        Identification: {party['id_type']} #{party['id_number']}<br/><br/>
        """, body_style))
    
    elements.append(Paragraph(f"""
        Sworn to and subscribed before me this {date}, by the above individuals, who are personally known to me or who have produced the above identification.<br/><br/>
        <b>Note:</b> Seal and signature are simulated placeholders. Replace with official versions from a notary public.<br/><br/>
        """, body_style))
    elements.append(Paragraph(f"Attorney Review: Verified by SWBW Law Firm for compliance with Florida Statutes § 695.03.", body_style))
    
    create_pdf_document(filename, elements)

def create_appraisal_report(filename, property_address, folio_number, appraised_value, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    appraiser_name = generate_random_name()
    elements = [
        Spacer(1, 3*inch),
        Paragraph("APPRAISAL REPORT", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        Prepared by: {appraiser_name}<br/>
        Licensed Appraiser, Key Appraisal Services, Inc.<br/>
        1234 Appraisal Lane, Miami, FL 33133<br/><br/>
        <b>Property Address:</b> {property_address}<br/>
        <b>Folio Number:</b> {folio_number}<br/>
        <b>Appraised Value:</b> ${appraised_value:,.2f}<br/>
        <b>Date of Appraisal:</b> {date}<br/><br/>
        This appraisal report certifies that the property located at the above address was appraised in accordance with the Uniform Standards of Professional Appraisal Practice (USPAP). The appraised value reflects the fair market value as of the date of appraisal, verified with Miami-Dade County Property Appraiser records (www.miamidadepa.gov).<br/><br/>
        <b>Note:</b> Seal and signature are simulated placeholders. Replace with official versions from a licensed appraiser.<br/><br/>
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: This report has been reviewed by SWBW Law Firm for accuracy.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_statement_of_consideration(filename, property_address, folio_number, sale_price, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    doc_stamp_tax = (sale_price / 100) * 0.60 + (sale_price / 100) * 0.45
    elements = [
        Spacer(1, 3*inch),
        Paragraph("STATEMENT OF CONSIDERATION", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        Property Address: {property_address}<br/>
        Folio Number: {folio_number}<br/>
        Sale Price: ${sale_price:,.2f}<br/>
        Date of Transfer: {date}<br/><br/>
        This statement certifies that the consideration for the transfer of the above property is ${sale_price:,.2f}, and the documentary stamp tax of ${doc_stamp_tax:.2f} has been paid to the Miami-Dade County Clerk of the Circuit Court, per Florida Statutes § 201.02. Property details verified with Miami-Dade County Property Appraiser (www.miamidadepa.gov).<br/><br/>
        <b>Note:</b> Stamp and signature are simulated placeholders. Replace with official versions from the Miami-Dade Clerk.<br/><br/>
        Prepared by: {deed_data['prepared_by']['name']}<br/>
        Address: {deed_data['prepared_by']['address']}<br/>
        Date: {date}
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: Verified by SWBW Law Firm for compliance.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_transfer_authorization_letter(filename, grantor, grantee, property_address, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("TRANSFER AUTHORIZATION LETTER", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        SWBW Law Firm<br/>
        123 Main St, Columbus, OH 43215<br/>
        Date: {date}<br/><br/>
        To Whom It May Concern:<br/><br/>
        I, {grantor['name']}, residing at {grantor['address']}, hereby authorize the transfer of the property located at {property_address} to {grantee['name']}, residing at {grantee['address']}, effective {date}. This transfer has been approved by the Ocean Tower One Condominium Association and verified with Miami-Dade County Property Appraiser records (www.miamidadepa.gov).<br/><br/>
        This authorization includes all necessary actions to complete the transfer, including the execution of the deed and payment of applicable taxes.<br/><br/>
        <b>Note:</b> Stamp and signature are simulated placeholders. Replace with official versions from the grantor and condo association.<br/><br/>
        Sincerely,
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: This letter has been reviewed by SWBW Law Firm, ensuring compliance with Florida Statutes.", body_style)
    ]
    
    create_pdf_document(filename, elements)

def create_bank_compliance_letter(filename, grantor, property_address, folio_number, date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, alignment=1, textColor=colors.darkblue, spaceAfter=0.25*inch)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=0.15*inch)
    
    elements = [
        Spacer(1, 3*inch),
        Paragraph("BANK COMPLIANCE LETTER", title_style),
        Spacer(1, 0.25*inch),
        Paragraph(f"""
        Key Bank of Miami<br/>
        1000 Bank St, Miami, FL 33131<br/>
        Date: {date}<br/><br/>
        To Whom It May Concern:<br/><br/>
        Key Bank of Miami hereby certifies that {grantor['name']} has complied with all financial obligations related to the property located at {property_address}, Folio Number: {folio_number}, as of {date}. A title search by Key Title Services, Inc. confirms no outstanding mortgages or liens held by this institution. Property details verified with Miami-Dade County Property Appraiser (www.miamidadepa.gov).<br/><br/>
        <b>Note:</b> Seal and signature are simulated placeholders. Replace with official versions from Key Bank of Miami.<br/><br/>
        """, body_style),
        Spacer(1, 0.15*inch),
        Paragraph(f"Attorney Review: Verified by SWBW Law Firm for accuracy.", body_style)
    ]
    
    create_pdf_document(filename, elements)

# Common data
property_address = "799 Crandon Blvd, Unit 13, Key Biscayne, FL 33149"
legal_description = "Condominium Unit 13, OCEAN TOWER ONE, as recorded in Official Records Book 12345, Page 678, Miami-Dade County, Florida"
folio_number = generate_random_folio_number()
sale_price = 967000.00
prepared_by = {
    'name': "Brian, SWBW Law Firm",
    'address': "123 Main St, Columbus, OH 43215"
}
witnesses = [
    {'name': generate_random_name(), 'address': generate_random_address()},
    {'name': generate_random_name(), 'address': generate_random_address()}
]
notary = {
    'name': generate_random_name(),
    'commission': f"FL{random.randint(1000000, 9999999)}",
    'expiry': "12/31/2027"
}
utility_accounts = {
    'water': f"W{random.randint(1000000, 9999999)}",
    'electric': f"E{random.randint(1000000, 9999999)}",
    'gas': f"G{random.randint(1000000, 9999999)}"
}
parties = [
    {
        'name': "Jason Lucas",
        'address': "799 Crandon Blvd, Unit 13, Key Biscayne, FL 33149",
        'id_type': "Florida Driver's License",
        'id_number': f"FL{random.randint(100000000, 999999999)}",
        'notary': notary
    },
    {
        'name': "Bonnie Bryon",
        'address': "9907 Road 9, Essex, ON N8M, Canada",
        'id_type': "Canadian Passport",
        'id_number': f"CA{random.randint(10000000, 99999999)}",
        'notary': notary
    },
    {
        'name': "George A. Hansen",
        'address': generate_random_address(),
        'id_type': "Florida Driver's License",
        'id_number': f"FL{random.randint(100000000, 999999999)}",
        'notary': notary
    }
]

# Deed data
deed_data = [
    {
        'filename': "Deed_of_Ownership.pdf",
        'deed_type': "Warranty",
        'grantor': parties[0],
        'grantee': parties[1],
        'property_address': property_address,
        'legal_description': legal_description,
        'folio_number': folio_number,
        'sale_price': sale_price,
        'witnesses': witnesses,
        'prepared_by': prepared_by,
        'transfer_date': "March 4, 2025",
        'notary': notary
    },
    {
        'filename': "Deed_of_Ownership_2.pdf",
        'deed_type': "Warranty",
        'grantor': {'name': "Bonnie Bryon and Jason Lucas", 'address': "9907 Road 9, Essex, ON N8M, Canada and 799 Crandon Blvd, Unit 13, Key Biscayne, FL 33149"},
        'grantee': parties[2],
        'property_address': property_address,
        'legal_description': legal_description,
        'folio_number': folio_number,
        'sale_price': sale_price,
        'witnesses': witnesses,
        'prepared_by': prepared_by,
        'transfer_date': "March 6, 2025",
        'notary': notary
    }
]

# Generate documents
for deed in deed_data:
    create_deed_of_ownership(deed)
create_affidavit_of_ownership("Affidavit_of_Ownership.pdf", parties[0], property_address, legal_description, folio_number, "March 4, 2025")
create_affidavit_of_ownership("Affidavit_of_Ownership_2.pdf", parties[1], property_address, legal_description, folio_number, "March 6, 2025")
create_tax_clearance_certificate("Tax_Clearance_Certificate.pdf", parties[2], property_address, folio_number, "March 7, 2025")
create_utility_clearance_certificate("Utility_Clearance_Certificate.pdf", parties[2], property_address, utility_accounts, "March 7, 2025")
create_proof_of_identity("Proof_of_Identity.pdf", parties, "March 7, 2025")
create_appraisal_report("Appraisal_Report.pdf", property_address, folio_number, sale_price, "March 6, 2025")
create_statement_of_consideration("Statement_of_Consideration.pdf", property_address, folio_number, sale_price, "March 6, 2025")
create_transfer_authorization_letter("Transfer_Authorization_Letter.pdf", parties[1], parties[2], property_address, "March 6, 2025")
create_bank_compliance_letter("Bank_Compliance_Letter.pdf", parties[1], property_address, folio_number, "March 7, 2025")
