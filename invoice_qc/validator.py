class Validator:
    def validate_invoice(self, invoice):
        errors = []

        # -------- Completeness Rules --------
        if not invoice.get("invoice_number"):
            errors.append("missing_field: invoice_number")

        if not invoice.get("invoice_date"):
            errors.append("missing_field: invoice_date")

        if not invoice.get("seller_name"):
            errors.append("missing_field: seller_name")

        if not invoice.get("buyer_name"):
            errors.append("missing_field: buyer_name")

        # -------- Format Rules --------
        currency = invoice.get("currency")
        if currency and currency not in ["USD", "EUR", "INR"]:
            errors.append("invalid_format: currency")

        # -------- Business Rules --------
        net = invoice.get("net_total")
        tax = invoice.get("tax_amount")
        gross = invoice.get("gross_total")

        if net is not None and tax is not None and gross is not None:
            if abs((net + tax) - gross) > 0.01:
                errors.append("business_rule_failed: totals_mismatch")

        # -------- Output --------
        return {
            "invoice_id": invoice.get("invoice_id"),
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def validate_batch(self, invoices):
        results = [self.validate_invoice(inv) for inv in invoices]

        summary = {
            "total_invoices": len(results),
            "valid_invoices": sum(r["is_valid"] for r in results),
            "invalid_invoices": sum(not r["is_valid"] for r in results),
            "error_counts": {}
        }

        # Count error types
        for r in results:
            for err in r["errors"]:
                summary["error_counts"][err] = summary["error_counts"].get(err, 0) + 1

        return results, summary
