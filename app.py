import streamlit as st
import pandas as pd
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

    # 3) Check for GST/HST number
    gst_hst_pattern = re.compile(r'\d{9}\s?[A-Z]{2}\s?\d{4}', re.IGNORECASE)
    gst_hst_number = gst_hst_pattern.search(text)
    gst_hst_found = gst_hst_number is not None
    if gst_hst_found:
        gst_hst_number = gst_hst_number.group().strip()
    else:
        gst_hst_number = None

    # 4) Check for Invoice number in various formats
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
        'Emile Corporation Found': emile_corp_found,
        'Address Found': address_found,
        'GST/HST Number': gst_hst_number,
        'Invoice Number': invoice_number,
    }

# Streamlit UI
st.title("Batch Invoice Information Extractor")

# Allow the user to upload multiple PDFs
uploaded_files = st.file_uploader("Upload PDF Invoices", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Initialize a list to store results
    results = []

    # Process each uploaded PDF
    for uploaded_file in uploaded_files:
        # Convert the uploaded file to a file-like object
        pdf_file = io.BytesIO(uploaded_file.read())

        # Extract information from the uploaded PDF
        invoice_info = extract_invoice_info(pdf_file)

        # Add the file name and extracted info to the results
        invoice_info['File Name'] = uploaded_file.name
        results.append(invoice_info)

    # Display the results
    st.subheader("Extracted Invoice Information")
    for result in results:
        st.write(f"**File Name:** {result['File Name']}")
        st.write(f"**Emile Corporation Found:** {result['Emile Corporation Found']}")
        st.write(f"**Address Found:** {result['Address Found']}")
        st.write(f"**GST/HST Number:** {result['GST/HST Number']}")
        st.write(f"**Invoice Number:** {result['Invoice Number']}")
        st.write("---")

    # Optional: Display a download button for consolidated results
    st.download_button(
        label="Download Results as CSV",
        data=pd.DataFrame(results).to_csv(index=False),
        file_name="invoice_extraction_results.csv",
        mime="text/csv",
    )
