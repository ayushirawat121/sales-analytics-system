from __future__ import annotations

from pathlib import Path

from utils.file_handler import read_sales_data
from utils.file_handler import parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
)
from utils.api_handler import fetch_all_products, create_product_mapping  # create_product_mapping saves enriched file
from utils.report_generator import generate_sales_report


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "data" / "sales_data.txt"
ENRICHED_FILE = PROJECT_ROOT / "data" / "enriched_sales_data.txt"
REPORT_FILE = PROJECT_ROOT / "output" / "sales_report.txt"


def _safe_input(prompt: str) -> str:
    """Prevents crashes if running in non-interactive environments."""
    try:
        return input(prompt)
    except EOFError:
        return ""


def _money_range(transactions):
    amounts = []
    for t in transactions:
        try:
            amounts.append(t["Quantity"] * t["UnitPrice"])
        except Exception:
            continue
    if not amounts:
        return 0.0, 0.0
    return min(amounts), max(amounts)


def main():
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()

        # [1/10] Reading sales data...
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data(str(DATA_FILE))
        if not raw_lines:
            print("✗ No data read. Please check the file path and encoding.")
            return
        print(f"✓ Successfully read {len(raw_lines)} transactions")
        print()

        # [2/10] Parsing and cleaning data...
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records")
        print()

        # [3/10] Filter options
        print("[3/10] Filter Options Available:")
        available_regions = sorted({t.get("Region") for t in transactions if t.get("Region")})
        min_amt, max_amt = _money_range(transactions)
        print(f"Regions: {', '.join(available_regions) if available_regions else 'N/A'}")
        print(f"Amount Range: ₹{min_amt:,.0f} - ₹{max_amt:,.0f}")
        print()

        want_filter = _safe_input("Do you want to filter data? (y/n): ").strip().lower()
        region = None
        min_amount = None
        max_amount = None

        if want_filter == "y":
            region_in = _safe_input("Enter region (or press Enter to skip): ").strip()
            region = region_in if region_in else None

            min_in = _safe_input("Enter minimum amount (or press Enter to skip): ").strip()
            max_in = _safe_input("Enter maximum amount (or press Enter to skip): ").strip()

            try:
                min_amount = float(min_in) if min_in else None
            except ValueError:
                min_amount = None

            try:
                max_amount = float(max_in) if max_in else None
            except ValueError:
                max_amount = None

        print()

        # [4/10] Validating + filtering
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, filter_summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        print(f"✓ Valid: {len(valid_transactions)} | Invalid: {invalid_count}")
        print()

        # [5/10] Analyze sales data (Part 2)
        print("[5/10] Analyzing sales data...")
        total_revenue = calculate_total_revenue(valid_transactions)
        regions = region_wise_sales(valid_transactions)
        top_products = top_selling_products(valid_transactions, n=5)
        customers = customer_analysis(valid_transactions)
        daily = daily_sales_trend(valid_transactions)
        peak_day = find_peak_sales_day(valid_transactions)
        low_products = low_performing_products(valid_transactions, threshold=10)
        print("✓ Analysis complete")
        print()

        # [6/10] Fetching product data from API...
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        if api_products:
            print(f"✓ Fetched {len(api_products)} products")
        else:
            print("✗ Failed to fetch products (API). Continuing without enrichment.")
        print()

        # [7/10] Enriching sales data...
        print("[7/10] Enriching sales data...")
        enriched_transactions = []
        if api_products:
            # NOTE: this version expects create_product_mapping(api_products, transactions, output_file)
            # and it saves enriched data using save_enriched_data internally.
            product_mapping, enriched_transactions = create_product_mapping(
                api_products,
                valid_transactions,
                output_file=str(ENRICHED_FILE),
            )
            attempts = len(enriched_transactions)
            successes = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
            success_rate = (successes / attempts * 100) if attempts else 0.0
            print(f"✓ Enriched {successes}/{attempts} transactions ({success_rate:.1f}%)")
        else:
            # If API failed, pass-through valid transactions as "enriched" with API_Match False
            for t in valid_transactions:
                e = t.copy()
                e["API_Category"] = None
                e["API_Brand"] = None
                e["API_Rating"] = None
                e["API_Match"] = False
                enriched_transactions.append(e)
            print("✓ Enrichment skipped (API unavailable)")
        print()

        # [8/10] Saving enriched data...
        # If API succeeded, create_product_mapping already saved it.
        # If API failed, we did not save — so we save here to keep workflow consistent.
        print("[8/10] Saving enriched data...")
        if not ENRICHED_FILE.exists():
            # create_product_mapping should have saved; if not, save via api_handler helper if you keep it separate.
            # If you kept save_enriched_data() in utils/api_handler.py, you can import & call it here.
            try:
                from utils.api_handler import save_enriched_data
                save_enriched_data(enriched_transactions, filename=str(ENRICHED_FILE))
            except Exception:
                pass

        if ENRICHED_FILE.exists():
            print(f"✓ Saved to: {ENRICHED_FILE}")
        else:
            print("✗ Could not save enriched data (check paths and permissions).")
        print()

        # [9/10] Generating report...
        print("[9/10] Generating report...")
        generate_sales_report(
            transactions=valid_transactions,
            enriched_transactions=enriched_transactions,
            output_file=str(REPORT_FILE),
        )
        if REPORT_FILE.exists():
            print(f"✓ Report saved to: {REPORT_FILE}")
        else:
            print("✗ Report generation failed (file not created).")
        print()

        # [10/10] Complete
        print("[10/10] Process Complete!")
        print("=" * 40)
        print("Files generated:")
        print(f"- Enriched data: {ENRICHED_FILE}")
        print(f"- Report:        {REPORT_FILE}")
        print("=" * 40)

    except Exception as e:
        # Global safety net: do not crash, show user-friendly message
        print("\n✗ Something went wrong, but the program did not crash.")
        print(f"Error: {e}")
        print("Tip: Check that you are running from the project root and that data/sales_data.txt exists.")


if __name__ == "__main__":
    main()