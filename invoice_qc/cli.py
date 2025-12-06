# invoice_qc/cli.py
import json
import argparse
from invoice_qc.extractor import extract_from_folder

def cmd_extract(args):
    invoices = extract_from_folder(args.pdf_dir)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(invoices, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(invoices)} invoices")

def cmd_validate(args):
    # assume existing validator logic
    import json
    from invoice_qc.validator import Validator
    with open(args.input, "r", encoding="utf-8") as f:
        invoices = json.load(f)
    validator = Validator()
    results, summary = validator.validate_batch(invoices)
    with open(args.output, "w", encoding="utf-8") as out:
        json.dump({"results": results, "summary": summary}, out, indent=2, ensure_ascii=False)
    print("Validation completed")

def main():
    parser = argparse.ArgumentParser(prog="invoice_qc")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("extract")
    p1.add_argument("pdf_dir")
    p1.add_argument("output")

    p2 = sub.add_parser("validate")
    p2.add_argument("input")
    p2.add_argument("output")

    args = parser.parse_args()
    if args.cmd == "extract":
        cmd_extract(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
