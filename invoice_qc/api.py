from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Any
from pydantic import BaseModel
import os
import tempfile
import shutil

from invoice_qc.extractor import extract_basic_invoice, extract_from_folder
from invoice_qc.validator import Validator

app = FastAPI(title="Invoice QC Service")

# -------------------------------------------
# ENABLE CORS FOR FRONTEND
# -------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow Vue/React/local HTML
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validator = Validator()


# -------------------------------------------
# MODELS
# -------------------------------------------
class InvoiceModel(BaseModel):
    invoice_number: Any = None
    invoice_date: Any = None
    seller_name: Any = None
    buyer_name: Any = None
    currency: Any = None
    net_total: Any = None
    tax_amount: Any = None
    gross_total: Any = None


# -------------------------------------------
# HEALTH CHECK
# -------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------------------------
# VALIDATE JSON ENDPOINT
# -------------------------------------------
@app.post("/validate-json")
async def validate_json(invoices: List[InvoiceModel]):
    invoices_list = [inv.dict() for inv in invoices]
    results, summary = validator.validate_batch(invoices_list)
    return {"results": results, "summary": summary}


# -------------------------------------------
# UPLOAD PDF → EXTRACT → VALIDATE
# -------------------------------------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    # Extract invoice
    extracted = extract_basic_invoice(temp_path)

    # Validate
    results, summary = validator.validate_batch([extracted])

    # remove temp
    os.remove(temp_path)

    return {
        "extracted_invoice": extracted,
        "validation": {
            "results": results,
            "summary": summary
        }
    }


# -------------------------------------------
# OPTIONAL: EXTRACT ALL PDFs IN FOLDER
# -------------------------------------------
@app.get("/extract-folder")
def extract_folder():
    invoices = extract_from_folder("sample_pdfs")
    return {"count": len(invoices), "invoices": invoices}
