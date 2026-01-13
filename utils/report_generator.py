from __future__ import annotations

from datetime import datetime
from pathlib import Path

from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
)


def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    """
    Generates a comprehensive formatted text report (in the required section order)
    and writes it to output/sales_report.txt by default.
    """

    # -------------------------
    # Helpers
    # -------------------------
    def money(value) -> str:
        try:
            return f"₹{float(value):,.2f}"
        except Exception:
            return "₹0.00"

    def percent(value) -> str:
        try:
            return f"{float(value):.2f}%"
        except Exception:
            return "0.00%"

    def pad(text, width, align="left"):
        text = "" if text is None else str(text)
        if len(text) > width:
            text = text[: width - 3] + "..."
        if align == "right":
            return text.rjust(width)
        if align == "center":
            return text.center(width)
        return text.ljust(width)

    def safe_write_line(f, line=""):
        f.write(line + "\n")

    out_path = Path(output_file).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records_processed = len(transactions)

    # -------------------------
    # 2. OVERALL SUMMARY (via existing functions)
    # -------------------------
    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = (total_revenue / total_transactions) if total_transactions else 0.0

    dates = [t.get("Date") for t in transactions if t.get("Date")]
    date_min = min(dates) if dates else "N/A"
    date_max = max(dates) if dates else "N/A"

    # -------------------------
    # 3. REGION-WISE PERFORMANCE
    # -------------------------
    region_stats = region_wise_sales(transactions)  # already sorted by total_sales desc

    # -------------------------
    # 4. TOP 5 PRODUCTS
    # -------------------------
    top_products = top_selling_products(transactions, n=5)

    # -------------------------
    # 5. TOP 5 CUSTOMERS
    # -------------------------
    customers = customer_analysis(transactions)  # dict sorted by total_spent desc
    top_5_customers = list(customers.items())[:5]

    # -------------------------
    # 6. DAILY SALES TREND
    # -------------------------
    daily_trend = daily_sales_trend(transactions)  # dict sorted by date

    # -------------------------
    # 7. PRODUCT PERFORMANCE ANALYSIS
    # -------------------------
    peak_date, peak_revenue, peak_txn_count = find_peak_sales_day(transactions)
    low_products = low_performing_products(transactions, threshold=10)

    # Average transaction value per region (derived from region_stats)
    avg_txn_value_by_region = []
    for region, stats in region_stats.items():
        sales = stats.get("total_sales", 0.0)
        count = stats.get("transaction_count", 0)
        avg_val = (sales / count) if count else 0.0
        avg_txn_value_by_region.append((region, avg_val))
    # Keep same order as region_stats (desc by sales)
    avg_txn_value_by_region = [(r, v) for r, v in avg_txn_value_by_region]

    # -------------------------
    # 8. API ENRICHMENT SUMMARY
    # -------------------------
    attempts = len(enriched_transactions)
    enriched_success = 0
    not_enriched_products = set()

    for t in enriched_transactions:
        if t.get("API_Match") is True:
            enriched_success += 1
        else:
            pn = t.get("ProductName")
            if pn:
                not_enriched_products.add(pn)

    success_rate = (enriched_success / attempts * 100) if attempts else 0.0
    not_enriched_products = sorted(not_enriched_products)

    # -------------------------
    # Write report (required order)
    # -------------------------
    line_eq = "=" * 44
    line_dash = "-" * 44

    with out_path.open("w", encoding="utf-8") as f:
        # 1. HEADER
        safe_write_line(f, line_eq)
        safe_write_line(f, pad("SALES ANALYTICS REPORT", 44, "center"))
        safe_write_line(f, pad(f"Generated: {generated_at}", 44, "center"))
        safe_write_line(f, pad(f"Records Processed: {total_records_processed}", 44, "center"))
        safe_write_line(f, line_eq)
        safe_write_line(f)

        # 2. OVERALL SUMMARY
        safe_write_line(f, "OVERALL SUMMARY")
        safe_write_line(f, line_dash)
        safe_write_line(f, f"{pad('Total Revenue:', 22)}{pad(money(total_revenue), 22, 'right')}")
        safe_write_line(f, f"{pad('Total Transactions:', 22)}{pad(total_transactions, 22, 'right')}")
        safe_write_line(f, f"{pad('Average Order Value:', 22)}{pad(money(avg_order_value), 22, 'right')}")
        safe_write_line(f, f"{pad('Date Range:', 22)}{pad(f'{date_min} to {date_max}', 22, 'right')}")
        safe_write_line(f)

        # 3. REGION-WISE PERFORMANCE
        safe_write_line(f, "REGION-WISE PERFORMANCE")
        safe_write_line(f, line_dash)
        safe_write_line(
            f,
            f"{pad('Region', 10)}{pad('Sales', 14, 'right')}{pad('% of Total', 12, 'right')}{pad('Transactions', 12, 'right')}",
        )
        for region, stats in region_stats.items():
            safe_write_line(
                f,
                f"{pad(region, 10)}"
                f"{pad(money(stats.get('total_sales', 0.0)), 14, 'right')}"
                f"{pad(percent(stats.get('percentage', 0.0)), 12, 'right')}"
                f"{pad(stats.get('transaction_count', 0), 12, 'right')}",
            )
        safe_write_line(f)

        # 4. TOP 5 PRODUCTS
        safe_write_line(f, "TOP 5 PRODUCTS")
        safe_write_line(f, line_dash)
        safe_write_line(
            f,
            f"{pad('Rank', 6)}{pad('Product Name', 20)}{pad('Quantity Sold', 14, 'right')}{pad('Revenue', 14, 'right')}",
        )
        for i, (name, qty, rev) in enumerate(top_products, start=1):
            safe_write_line(
                f,
                f"{pad(i, 6)}{pad(name, 20)}{pad(qty, 14, 'right')}{pad(money(rev), 14, 'right')}",
            )
        safe_write_line(f)

        # 5. TOP 5 CUSTOMERS
        safe_write_line(f, "TOP 5 CUSTOMERS")
        safe_write_line(f, line_dash)
        safe_write_line(
            f,
            f"{pad('Rank', 6)}{pad('Customer ID', 14)}{pad('Total Spent', 14, 'right')}{pad('Order Count', 12, 'right')}",
        )
        for i, (cid, stats) in enumerate(top_5_customers, start=1):
            safe_write_line(
                f,
                f"{pad(i, 6)}{pad(cid, 14)}{pad(money(stats.get('total_spent', 0.0)), 14, 'right')}{pad(stats.get('purchase_count', 0), 12, 'right')}",
            )
        safe_write_line(f)

        # 6. DAILY SALES TREND
        safe_write_line(f, "DAILY SALES TREND")
        safe_write_line(f, line_dash)
        safe_write_line(
            f,
            f"{pad('Date', 12)}{pad('Revenue', 14, 'right')}{pad('Transactions', 12, 'right')}{pad('Unique Customers', 16, 'right')}",
        )
        for date, stats in daily_trend.items():
            safe_write_line(
                f,
                f"{pad(date, 12)}"
                f"{pad(money(stats.get('revenue', 0.0)), 14, 'right')}"
                f"{pad(stats.get('transaction_count', 0), 12, 'right')}"
                f"{pad(stats.get('unique_customers', 0), 16, 'right')}",
            )
        safe_write_line(f)

        # 7. PRODUCT PERFORMANCE ANALYSIS
        safe_write_line(f, "PRODUCT PERFORMANCE ANALYSIS")
        safe_write_line(f, line_dash)
        safe_write_line(
            f,
            f"Best selling day: {peak_date} | Revenue: {money(peak_revenue)} | Transactions: {peak_txn_count}",
        )
        safe_write_line(f)

        if low_products:
            safe_write_line(f, "Low performing products (Total Quantity < 10)")
            safe_write_line(f, f"{pad('Product Name', 22)}{pad('Qty', 8, 'right')}{pad('Revenue', 14, 'right')}")
            for name, qty, rev in low_products:
                safe_write_line(f, f"{pad(name, 22)}{pad(qty, 8, 'right')}{pad(money(rev), 14, 'right')}")
        else:
            safe_write_line(f, "Low performing products: None (all products have quantity >= 10)")
        safe_write_line(f)

        safe_write_line(f, "Average transaction value per region")
        safe_write_line(f, f"{pad('Region', 10)}{pad('Avg Txn Value', 18, 'right')}")
        for region, avg_val in avg_txn_value_by_region:
            safe_write_line(f, f"{pad(region, 10)}{pad(money(avg_val), 18, 'right')}")
        safe_write_line(f)

        # 8. API ENRICHMENT SUMMARY
        safe_write_line(f, "API ENRICHMENT SUMMARY")
        safe_write_line(f, line_dash)
        safe_write_line(f, f"{pad('Total enrichment attempts:', 28)}{pad(attempts, 16, 'right')}")
        safe_write_line(f, f"{pad('Total records enriched:', 28)}{pad(enriched_success, 16, 'right')}")
        safe_write_line(f, f"{pad('Success rate:', 28)}{pad(percent(success_rate), 16, 'right')}")
        safe_write_line(f)
        safe_write_line(f, "Products that couldn't be enriched:")
        if not_enriched_products:
            for p in not_enriched_products:
                safe_write_line(f, f"- {p}")
        else:
            safe_write_line(f, "- None")

    print(f"Sales report generated: {out_path}")
    return str(out_path)
