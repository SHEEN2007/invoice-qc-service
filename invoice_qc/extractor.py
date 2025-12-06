import pdfplumber
import re
import os

# ----------------------------------------------------
# Extract raw text from a PDF
# ----------------------------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        return ""
    return text


# ----------------------------------------------------
# Regex helper – general pattern extraction
# ----------------------------------------------------
def extract_pattern(pattern, text):
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.group(1).strip() if m else None


# ----------------------------------------------------
# Helper to extract money amounts like 1000.00
# ----------------------------------------------------
def extract_amount(pattern, text):
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except:
            return None
    return None


# ----------------------------------------------------
# MAIN EXTRACTION LOGIC FOR ONE PDF
# ----------------------------------------------------
def extract_basic_invoice(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    # -----------------------
    # SIMPLE FIELD EXTRACTION
    # -----------------------
    invoice_number = extract_pattern(r"Invoice\s*No[:\s]*([A-Za-z0-9\-]+)", text)
    invoice_date = extract_pattern(r"Invoice\s*Date[:\s]*(\d{4}-\d{2}-\d{2})", text)
    due_date = extract_pattern(r"Due\s*Date[:\s]*(\d{4}-\d{2}-\d{2})", text)

    seller_name = extract_pattern(r"Seller[:\s]*([A-Za-z0-9 .,]+)", text)
    buyer_name = extract_pattern(r"Buyer[:\s]*([A-Za-z0-9 .,]+)", text)
    currency = extract_pattern(r"Currency[:\s]*([A-Z]{3})", text)

    # -----------------------
    # AMOUNTS
    # -----------------------
    net_total = extract_amount(r"Net Total[:\s]*([\d,]+\.\d+)", text)
    tax_amount = extract_amount(r"Tax[:\s]*([\d,]+\.\d+)", text)
    gross_total = extract_amount(r"Total[:\s]*([\d,]+\.\d+)", text)

    # -----------------------
    # FALLBACK CALCULATIONS
    # -----------------------

    # If gross total not found → pick largest number in text
    if gross_total is None:
        amounts = re.findall(r"(\d{3,7}\.\d{2})", text)
        if amounts:
            gross_total = float(amounts[-1])  # assume largest number is the total

    # If net_total missing but tax + gross exist → calculate
    if net_total is None and gross_total is not None and tax_amount is not None:
        net_total = gross_total - tax_amount

    # -----------------------
    # FINAL STRUCTURED OUTPUT
    # -----------------------
    return {
        "invoice_id": pdf_path,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "seller_name": seller_name,
        "buyer_name": buyer_name,
        "currency": currency,
        "net_total": net_total,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
        "line_items": []   # (Optional) We are skipping table extraction for now
    }


# ----------------------------------------------------
# EXTRACT ALL PDFs IN A FOLDER
# ----------------------------------------------------
def extract_from_folder(folder_path):
    invoices = []

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            invoice_data = extract_basic_invoice(pdf_path)
            invoices.append(invoice_data)

    return invoices
