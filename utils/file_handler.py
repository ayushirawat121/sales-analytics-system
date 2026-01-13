def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns:
        list of raw transaction lines (strings)

    Expected Output Format:
        ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements handled:
    - Uses 'with' statement
    - Tries multiple encodings ('utf-8', 'latin-1', 'cp1252')
    - Handles FileNotFoundError
    - Skips header row
    - Removes empty lines
    """

    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                lines = file.readlines()

            # Remove header and empty lines
            data_lines = [
                line.strip()
                for line in lines[1:]  # skip header
                if line.strip()
            ]

            return data_lines

        except UnicodeDecodeError:
            # Try next encoding
            continue

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    # If none of the encodings worked
    print("Error: Unable to read file due to encoding issues.")
    return []

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    transactions = []
    expected_fields = 8

    for line in raw_lines:
        if not line or not line.strip():
            continue  # skip empty lines

        parts = line.strip().split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != expected_fields:
            continue

        transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = parts

        # Clean ProductName (remove commas)
        product_name = product_name.replace(",", "").strip()

        # Clean numeric fields (remove commas)
        quantity = quantity.replace(",", "").strip()
        unit_price = unit_price.replace(",", "").strip()

        # Convert types safely (skip line if conversion fails)
        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
        except ValueError:
            continue

        transactions.append({
            "TransactionID": transaction_id.strip(),
            "Date": date.strip(),
            "ProductID": product_id.strip(),
            "ProductName": product_name,
            "Quantity": quantity,         # int
            "UnitPrice": unit_price,      # float
            "CustomerID": customer_id.strip(),
            "Region": region.strip(),
        })

    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters

    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """

    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    # -------------------------
    # 1) Validate transactions
    # -------------------------
    valid = []
    invalid_count = 0

    for t in transactions:
        # Required fields present
        if not all(field in t for field in required_fields):
            invalid_count += 1
            continue

        # Basic value/type validations
        try:
            qty = t["Quantity"]
            price = t["UnitPrice"]
        except Exception:
            invalid_count += 1
            continue

        if qty is None or price is None or qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        # ID format rules
        if not str(t["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue
        if not str(t["ProductID"]).startswith("P"):
            invalid_count += 1
            continue
        if not str(t["CustomerID"]).startswith("C"):
            invalid_count += 1
            continue

        valid.append(t)

    total_input = len(transactions)

    # ------------------------------------
    # 2) Display available filter options
    # ------------------------------------
    available_regions = sorted({t["Region"] for t in valid if t.get("Region")})
    print(f"Available regions: {available_regions}")

    # Compute transaction amounts for range display
    amounts = [t["Quantity"] * t["UnitPrice"] for t in valid]
    if amounts:
        min_amt_available = min(amounts)
        max_amt_available = max(amounts)
        print(f"Transaction amount range: min={min_amt_available}, max={max_amt_available}")
    else:
        print("Transaction amount range: min=0, max=0")

    # ------------------------------------
    # 3) Apply filters (with step counts)
    # ------------------------------------
    filtered_by_region = 0
    filtered_by_amount = 0

    current = valid

    # Region filter
    if region is not None:
        before = len(current)
        current = [t for t in current if t.get("Region") == region]
        after = len(current)
        filtered_by_region = before - after
        print(f"After region filter ({region}): {after} records")

    # Amount filters (Quantity * UnitPrice)
    if min_amount is not None or max_amount is not None:
        before = len(current)

        def in_amount_range(t):
            amount = t["Quantity"] * t["UnitPrice"]
            if min_amount is not None and amount < min_amount:
                return False
            if max_amount is not None and amount > max_amount:
                return False
            return True

        current = [t for t in current if in_amount_range(t)]
        after = len(current)
        filtered_by_amount = before - after
        print(f"After amount filter (min={min_amount}, max={max_amount}): {after} records")

    # -------------------------
    # 4) Build filter summary
    # -------------------------
    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(current),
    }

    return current, invalid_count, filter_summary