import os
import io
import time
import threading
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageTemplate, Frame)
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# -----------------------------
# Configuration / Constants
# -----------------------------
API_TOKEN = 'a90f1305a149d3e0b0e86890e2680dde1e2861dc'
API_BASE_URL = 'https://api.pipedrive.com/v1/'
PERSONS_ENDPOINT = f'{API_BASE_URL}persons'
ORGANIZATION_ENDPOINT = f'{API_BASE_URL}organizations/'

# For ReportLab: assume your images are in the static folder.
LOGO_PATH = os.path.join('static', 'logo.png')
FOOTER_PATH = os.path.join('static', 'footer.png')

# -----------------------------
# Global Cache Variables
# -----------------------------
data_cache = []          # list of records (dict)
last_fetch_time = 0      # timestamp (in seconds)
CACHE_TIMEOUT = 300      # seconds

# -----------------------------
# Helper Functions
# -----------------------------
def make_api_request(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data')
    else:
        print(f'Failed to retrieve data. Status code: {response.status_code}')
        return None

def fetch_data():
    """Fetch data from Pipedrive and update the global cache."""
    global data_cache, last_fetch_time
    new_data = []
    start = 0
    limit = 400
    while True:
        params = {'api_token': API_TOKEN, 'start': start, 'limit': limit}
        persons = make_api_request(PERSONS_ENDPOINT, params)
        if not persons:
            break
        for person in persons:
            try:
                # Extract person details:
                name = person.get('name', '')
                email = ''
                if person.get('email'):
                    email = person.get('email')[0].get('value', '')
                phone = ''
                if person.get('phone'):
                    phone = person.get('phone')[0].get('value', '')
                job_title = person.get('0f81155bcd6012720f3a3686427336d6f6934b1c', '')
                
                # Defaults if no organization is found:
                organization_name = ''
                address1 = ''
                address2 = ''
                address3 = ''
                invoice_email = ''
                locality = ''
                postal_code = ''
                state = ''

                # Get organization details if available
                if person.get('org_id'):
                    org_id = person.get('org_id').get('value')
                    org_response = make_api_request(f'{ORGANIZATION_ENDPOINT}{org_id}', params={'api_token': API_TOKEN})
                    if org_response:
                        organization_name = org_response.get('name', '')
                        address1 = org_response.get('8c05dc555db68231c0adac4eb565ac22f1f5de7d', '')
                        invoice_email = org_response.get('933976fa080088301724ec9c04b5df46b76ada45', '')
                        address2 = org_response.get('7b7131bad94daec18cf63448c0ddf78254c6a14f', '')
                        address3 = org_response.get('c77bc735b6d866784c14b6498a639511c5ef6cc6', '')
                        locality = org_response.get('084158f79d6d1ae99b6a97c64762d99b87afcf06', '')
                        postal_code = org_response.get('e62b6d521dc6b370bbd3a00973f6c7aa411a3fa8', '')
                        state = org_response.get('d474c137bb5f39f51f8ce5b8732cfc129697328c', '')
                    else:
                        print(f"No organization details for {name}")
                else:
                    print(f'No Organisation found for: {name}')

                # Build a record – extra invoice fields left empty for user editing.
                record = {
                    'organization': organization_name,
                    'name': name,
                    'job_title': job_title,
                    'email': email,
                    'invoice_email': invoice_email,
                    'phone': phone,
                    'address1': address1,
                    'address2': address2,
                    'address3': address3,
                    'locality': locality,
                    'postal_code': postal_code,
                    'state': state,
                    # Extra invoice-specific fields:
                    'city': '',
                    'shipping_address': '',
                    'commercial_invoice': '',
                    'customer_po': '',
                    'customer_id': '',
                    'date': '',
                    'vendor_id': '',
                    'position': '',
                    'quantity': '',
                    'price_unit': '',
                    'sum': '',
                    'estimated_shipping_date': '',
                    'packaging': ''
                }
                new_data.append(record)
            except Exception as e:
                print(f'Error processing record for {name}: {e}')
        start += limit
    data_cache = new_data
    last_fetch_time = time.time()
    print(f"Fetched {len(data_cache)} records at {time.ctime(last_fetch_time)}")
    return data_cache

def background_update():
    """Helper to update the cache in a background thread."""
    try:
        fetch_data()
    except Exception as e:
        print("Background update failed:", e)

# -----------------------------
# Invoice PDF Generation
# -----------------------------
def generate_invoice(invoice_data):
    """
    Generate a PDF invoice using the invoice_data dictionary.
    Returns a BytesIO stream containing the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=30,
                            leftMargin=30,
                            topMargin=50,
                            bottomMargin=18)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(name="Normal", parent=styles["Normal"], fontSize=10, leading=12)
    bold_style = ParagraphStyle(name="Bold", parent=normal_style, fontName="Helvetica-Bold")
    large_bold_style = ParagraphStyle(name="LargeBold", parent=bold_style, fontSize=12, leading=14)
    
    # --- Recipient Data ---
    # The form sends "address1" but we map it to key "address" in our route.
    recipient_data = [
        invoice_data.get('organization', ''),
        invoice_data.get('address', ''),
        invoice_data.get('locality', ''),
        invoice_data.get('city', ''),
        invoice_data.get('postal_code', ''),
        invoice_data.get('state', '')
    ]
    recipient_data = [line for line in recipient_data if line]
    
    # --- Shipping Data ---
    shipping_data = [
        invoice_data.get('shipping_address', ''),
        f"{invoice_data.get('name', '')} / {invoice_data.get('job_title', '')}",
        invoice_data.get('phone', ''),
        invoice_data.get('email', '')
    ]
    shipping_data = [line for line in shipping_data if line]
    
    # --- Commercial Invoice Header ---
    commercial_invoice_data = [
        f"Commercial Invoice {invoice_data.get('commercial_invoice', '')}",
        f"Customer PO: {invoice_data.get('customer_po', '')}",
        f"Customer ID: {invoice_data.get('customer_id', '')}",
        f"Date: {invoice_data.get('date', '')}",
        f"Vendor ID: {invoice_data.get('vendor_id', '')}"
    ]
    commercial_invoice_data = [line for line in commercial_invoice_data if line]
    
    # --- Table Data for Items ---
    table_data = [["Position", "Quantity", "Price/Unit", "Sum"]]
    if invoice_data.get('position'):
        pos = invoice_data.get('position')
        pos_parts = []
        for part in pos.split(", "):
            if "H.S. Code" in part or "Origin" in part:
                pos_parts.append(f"<font size='8'>{part}</font>")
            else:
                pos_parts.append(part)
        formatted_position = ", ".join(pos_parts)
        qty = invoice_data.get('quantity', '')
        price_unit = invoice_data.get('price_unit', '')
        sum_val = invoice_data.get('sum', '')
        table_data.append([formatted_position, qty, price_unit, sum_val])
        try:
            total = float(sum_val.replace(',', '').replace('USD','').strip()) if sum_val.strip() else 0.0
        except Exception:
            total = 0.0
        table_data.append(["Total", "", "", f"{total:,.2f} USD"])
    else:
        table_data.append(["", "", "", ""])
    
    shipping_date_paragraph = f"Estimated shipping date: {invoice_data.get('estimated_shipping_date', '')}"
    
    # --- Additional Section ---
    packaging = f"Packaging: {invoice_data.get('packaging', '')}<br/>"
    additional_section_text = [
        packaging,
        "Terms of payment: within 30 days by bank transfer",
        "<i><font size='8'>All orders are accepted, delivered and invoiced based on our general terms and conditions. Download at <u>http://variowell-development.de/...</u></font></i>"
    ]
    additional_section_text = [line for line in additional_section_text if line]
    
    # --- Build PDF Content ---
    elements = []
    
    def draw_logo(canvas, doc):
        if os.path.exists(LOGO_PATH):
            try:
                logo = Image(LOGO_PATH, width=3*inch, height=1*inch)
                logo.drawOn(canvas, 40, A4[1] - 120)
            except Exception as e:
                print("Error drawing logo:", e)
        else:
            print("Logo file not found:", LOGO_PATH)
    
    def draw_footer(canvas, doc):
        if os.path.exists(FOOTER_PATH):
            try:
                footer = Image(FOOTER_PATH, width=doc.width, height=1*inch)
                footer.drawOn(canvas, doc.leftMargin, 10)
            except Exception as e:
                print("Error drawing footer:", e)
        else:
            print("Footer file not found:", FOOTER_PATH)
    
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 1*inch, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=draw_logo, onPageEnd=draw_footer)
    doc.addPageTemplates([template])
    
    # Recipient Section
    recipient_paragraphs = [Paragraph(line, bold_style if idx==0 else normal_style)
                              for idx, line in enumerate(recipient_data)]
    shipping_paragraphs = [Paragraph("Shipping address", bold_style)] + [Paragraph(line, normal_style) for line in shipping_data]
    address_table = Table([[recipient_paragraphs, shipping_paragraphs]], colWidths=[doc.width/2, doc.width/2])
    elements.append(address_table)
    elements.append(Spacer(1, 12))
    
    # Commercial Invoice Header
    if commercial_invoice_data:
        elements.append(Paragraph(commercial_invoice_data[0], large_bold_style))
    elements.append(Spacer(1, 12))
    for line in commercial_invoice_data[1:]:
        elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 20))
    
    # Items Table
    table_elements = []
    for idx, row in enumerate(table_data):
        row_elements = [Paragraph(cell, bold_style if idx==0 or row[0]=="Total" else normal_style) for cell in row]
        table_elements.append(row_elements)
    items_table = Table(table_elements, colWidths=[doc.width/2, doc.width/6, doc.width/6, doc.width/6])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (-4, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 12))
    
    # Shipping Date
    elements.append(Paragraph(shipping_date_paragraph, normal_style))
    elements.append(Spacer(1, 48))
    
    # Additional Section
    for line in additional_section_text:
        elements.append(Paragraph(line, normal_style))
        elements.append(Spacer(1, 12))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# Flask Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-data', methods=['GET'])
def get_data_route():
    global data_cache, last_fetch_time
    now = time.time()
    if data_cache and (now - last_fetch_time < CACHE_TIMEOUT):
        if now - last_fetch_time > (CACHE_TIMEOUT - 60):
            threading.Thread(target=background_update).start()
        return jsonify(data=data_cache, cached=True)
    else:
        fetch_data()
        return jsonify(data=data_cache, cached=False)

@app.route('/select-org', methods=['GET', 'POST'])
def select_org():
    if not data_cache:
        fetch_data()
    # Build a sorted, unique list of non-empty organization names.
    org_list = sorted({rec.get('organization', '').strip() for rec in data_cache if rec.get('organization', '').strip()})
    return render_template('select_org.html', organizations=org_list)

@app.route('/edit-invoice')
def edit_invoice():
    org_name = request.args.get('org_name')
    if not org_name:
        flash("No organization specified.", "danger")
        return redirect(url_for('select_org'))
    record = next((rec for rec in data_cache 
                   if rec.get('organization', '').strip().lower() == org_name.strip().lower()), None)
    if not record:
        flash(f"Organization '{org_name}' not found.", "danger")
        return redirect(url_for('select_org'))
    return render_template('edit_invoice.html', record=record)

@app.route('/create-invoice', methods=['POST'])
def create_invoice_route():
    # Map "address1" from the form to key "address" for the PDF generator.
    invoice_data = {
        'organization': request.form.get('organization', ''),
        'name': request.form.get('name', ''),
        'job_title': request.form.get('job_title', ''),
        'email': request.form.get('email', ''),
        'invoice_email': request.form.get('invoice_email', ''),
        'phone': request.form.get('phone', ''),
        'address': request.form.get('address1', ''),  # mapping here
        'address2': request.form.get('address2', ''),
        'address3': request.form.get('address3', ''),
        'locality': request.form.get('locality', ''),
        'city': request.form.get('city', ''),
        'postal_code': request.form.get('postal_code', ''),
        'state': request.form.get('state', ''),
        'shipping_address': request.form.get('shipping_address', ''),
        'commercial_invoice': request.form.get('commercial_invoice', ''),
        'customer_po': request.form.get('customer_po', ''),
        'customer_id': request.form.get('customer_id', ''),
        'date': request.form.get('date', ''),
        'vendor_id': request.form.get('vendor_id', ''),
        'position': request.form.get('position', ''),
        'quantity': request.form.get('quantity', ''),
        'price_unit': request.form.get('price_unit', ''),
        'sum': request.form.get('sum', ''),
        'estimated_shipping_date': request.form.get('estimated_shipping_date', ''),
        'packaging': request.form.get('packaging', '')
    }
    print("Invoice data received:", invoice_data)
    pdf_buffer = generate_invoice(invoice_data)
    return send_file(pdf_buffer, as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')

# -----------------------------
# Run the App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)