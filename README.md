This project is my implementation of the Invoice Extraction & Quality Control assignment.
1. I built a small system that can:

2. Extract information from invoice PDFs

3. Validate the extracted data using rules I designed

4. Run through a CLI

5. Expose the logic through a FastAPI backend

6. A simple front-end page for uploading PDFs or pasting JSON and viewing the validations

The goal was to make something realistic but still manageable within the timeframe.

1️. What the project does (quick overview)
-> PDF Extraction

Reads text from a PDF and tries to extract useful invoice fields using regex + small heuristics.

-> Validation

Checks completeness, format, basic business rules, and some anomalies.

-> CLI

Can extract, validate, or perform a full-run from PDFs → results.

-> FastAPI backend

Endpoints for JSON validation and PDF upload/extraction.

-> Bonus UI

A minimal HTML/JS page acting like an internal QC console.

2️. Schema Design (Fields I selected)

I tried to choose fields that appear in almost all B2B invoices and are actually useful:

Field                                  	Why I chose it
invoice_number                         	A core identifier
invoice_date	                          Needed for timeline/finance
due_date	                              To compare with invoice_date
seller_name	                            Supplier identification
buyer_name	                            Customer identification
currency	                              Avoid mismatched currencies
net_total	                              subtotal before tax
tax_amount	                            VAT/GST component
gross_total	                            final payable amount


3.  Validation 

I created a mix of completeness, format, and business rules.

-> Completeness

invoice_number must not be empty

invoice_date must not be empty

seller_name and buyer_name shouldn’t be empty

Reason: an invoice without these is practically unusable.

->Format rules

  a. currency must be a valid ISO code (INR, USD, EUR…)

  b.dates must be parseable

  c.totals should be numeric

Reason: prevents messy downstream processing.

-> Business rules

  a.net_total + tax_amount ≈ gross_total

  b.due_date >= invoice_date

Reason: these appear in almost all invoicing systems.

-> Anomaly rule

  a.No negative totals


Reason: protects against faulty extraction or bad data.

4️. How the extraction works (PDF → JSON)

PDF extraction uses:

  a.pdfplumber for text extraction

  b.regex for matching things like invoice number, totals, dates

  c.fallback logic (e.g., picking the largest number if totals aren’t found)

If some fields aren’t found in the PDF, I keep them as null.
This lets the validation layer handle missing data properly.

Sample extraction output:

{
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-01-10",
  "seller_name": null,
  "buyer_name": null,
  "net_total": 820,
  "tax_amount": 180,
  "gross_total": 1000,
  "line_items": []
}

5️. Validation Results Format

Each invoice returns:

{
  "invoice_id": "...",
  "is_valid": false,
  "errors": [
    "missing_field: seller_name",
    "missing_field: buyer_name"
  ]
}


And there's also a summary:

{
  "total_invoices": 1,
  "valid_invoices": 0,
  "invalid_invoices": 1
}

6️. CLI Usage
Extract PDFs
      python -m invoice_qc.cli extract sample_pdfs extracted.json

Validate JSON file
      python -m invoice_qc.cli validate extracted.json validated_output.json

Full pipeline
      python -m invoice_qc.cli full-run sample_pdfs validated_output.json

7️. API Endpoints (FastAPI)

Run the API:

     uvicorn invoice_qc.api:app --reload

Health check

     GET /health

{ "status": "ok" }

Validate JSON

   POST /validate-json

Sends a list of invoices in the body.

Upload PDF and auto-extract

POST /upload-pdf

This returns both the extracted invoice + validation results.

8️. Bonus: Small QC Web Console

->Inside frontend/index.html, I made a small UI that:

  a.lets you upload a PDF

  b. paste JSON directly

  c.displays the JSON response nicely formatted

  d.calls backend APIs from the browser

This simulates how an internal QC dashboard might work.

9️. How this can integrate with bigger systems

This could easily slot into:

  a. A document ingestion pipeline

  b.An accounting dashboard

  c.An RPA process

  d.A vendor onboarding portal

Possible future improvements:

  a.Job queues for large batches

  b.database storage of results


10. Installation Instructions

Create a venv:

  python -m venv venv


Activate:

  venv\Scripts\activate   (Windows)
  source venv/bin/activate (Mac/Linux)


Install dependencies:

  pip install -r requirements.txt


Run API:

  uvicorn invoice_qc.api:app --reload


Open UI:
Just open frontend/index.html in a browser.

11. AI Usage Notes (as required)

I used ChatGPT mainly for:

->brainstorming regex patterns

->helping shape FastAPI route structure

->some UI JavaScript fetch code

->proofreading and organizing my thoughts

An example where AI was wrong:
It suggested a regex for seller/buyer fields that didn’t match my actual PDFs at all.
I had to create my own fallback logic and accept null values so the validator could catch missing fields.

I kept the architectural decisions and rule design purely based on my own judgement.

1️2.  Limitations / Known Issues

  a.PDF formats differ a lot → extraction is not perfect

  b.Seller/buyer names may fail if not clearly labeled

  c.No ML-based parsing, only rule-based extraction

  d.Line-item extraction minimal

Some assumptions were made to keep the project scoped properly