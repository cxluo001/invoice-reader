import streamlit as st
import pdfplumber
import re
import io

def extract_invoice_info(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()

    # 1) Check for 'emile corporation' with flexible spacing
    emile_pattern = re.compile(r'e\s*m\s*i\s*l\s*e\s*corporation', re.IGNORECASE)
    emile_corp_found = emile_pattern.search(text) is not None

    # 2) Check for address, ignoring commas
    address_pattern = re.compile(
        r'134\s*Bethridge\s*Rd\s*,?\s*Etobicoke\s*,?\s*ON\s*,?\s*M9W\s*1N3',
        re.IGNORECASE
    )
    address_found = address_pattern.search(text) is not None

    # 3) Check for GST number
    gst_pattern = re.compile(r'\d{9}\s?[A-Z]{2}\s?\d{4}', re.IGNORECASE)
    gst_found = gst_pattern.search(text) is not None

    # 4) Check for HST number (must include 'HST')
    hst_pattern = re.compile(r'HST\s*[:#]?\s*\d{9}\s?[A-Z]{2}\s?\d{4}', re.IGNORECASE)
    hst_found = hst_pattern.search(text) is not None

    # 5) Check for Invoice number in various formats
    invoice_pattern = re.compile(
        r'(invoice\s*(number|no\.|#)\s*[:#]?\s*([0-9\-/._\[\]()]+))',
        re.IGNORECASE
    )
    invoice_match = invoice_pattern.search(text)

    if invoice_match:
        invoice_number = invoice_match.group(3).strip()
        if not invoice_number:  # Check for empty field
            invoice_number = 'Blank'
    else:
        invoice_number = None

    # Return the results
    return {
        'emile_corp_found': emile_corp_found,
        'address_found': address_found,
        'gst_found': gst_found,
        'hst_found': hst_found,
        'invoice_number': invoice_number,
    }

# Streamlit UI
st.title("Invoice Information Extractor")

# Allow the user to upload a PDF
uploaded_file = st.file_uploader("Upload a PDF Invoice", type="pdf")

if uploaded_file is not None:
    # Display the uploaded file name
    st.write(f"File Name: {uploaded_file.name}")

    # Convert the uploaded file to a file-like object
    pdf_file = io.BytesIO(uploaded_file.read())

    # Extract information from the uploaded PDF
    invoice_info = extract_invoice_info(pdf_file)
    
    # Display the results
    st.subheader("Extracted Invoice Information")
    st.write(invoice_info)