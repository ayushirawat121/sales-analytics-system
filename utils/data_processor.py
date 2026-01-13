#method to calculate total revenue
def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns:
        float: total revenue (sum of Quantity * UnitPrice)

    Example:
        1545000.50
    """
    total_revenue = 0.0

    for t in transactions:
        try:
            total_revenue += t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            # Skip malformed transaction records
            continue

    return total_revenue

#method to calculate region wise sales
def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns:
        dict with region statistics sorted by total_sales (descending)

    Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        ...
    }
    """
    region_stats = {}
    grand_total = 0.0

    # -------------------------
    # 1) Aggregate totals
    # -------------------------
    for t in transactions:
        try:
            region = t["Region"]
            amount = t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            continue

        grand_total += amount

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # -------------------------
    # 2) Calculate percentages
    # -------------------------
    for region in region_stats:
        total_sales = region_stats[region]["total_sales"]
        percentage = (total_sales / grand_total * 100) if grand_total > 0 else 0.0
        region_stats[region]["percentage"] = round(percentage, 2)

    # -------------------------
    # 3) Sort by total_sales DESC
    # -------------------------
    sorted_regions = dict(
        sorted(
            region_stats.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_regions


#method to get top selling products
def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns:
        list of tuples:
        (ProductName, TotalQuantity, TotalRevenue)
    """
    product_stats = {}

    # -------------------------
    # 1) Aggregate by ProductName
    # -------------------------
    for t in transactions:
        try:
            name = t["ProductName"]
            qty = t["Quantity"]
            revenue = t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            continue

        if name not in product_stats:
            product_stats[name] = {
                "quantity": 0,
                "revenue": 0.0
            }

        product_stats[name]["quantity"] += qty
        product_stats[name]["revenue"] += revenue

    # -------------------------
    # 2) Sort by TotalQuantity DESC
    # -------------------------
    sorted_products = sorted(
        product_stats.items(),
        key=lambda item: item[1]["quantity"],
        reverse=True
    )

    # -------------------------
    # 3) Return top n products
    # -------------------------
    result = []
    for product, stats in sorted_products[:n]:
        result.append(
            (product, stats["quantity"], stats["revenue"])
        )

    return result


#customer data analysis as per the transacations 
def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns:
        dict of customer statistics sorted by total_spent (descending)
    """
    customer_stats = {}

    # -------------------------
    # 1) Aggregate per customer
    # -------------------------
    for t in transactions:
        try:
            customer = t["CustomerID"]
            product = t["ProductName"]
            amount = t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            continue

        if customer not in customer_stats:
            customer_stats[customer] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_stats[customer]["total_spent"] += amount
        customer_stats[customer]["purchase_count"] += 1
        customer_stats[customer]["products_bought"].add(product)

    # -------------------------
    # 2) Final calculations
    # -------------------------
    for customer in customer_stats:
        total = customer_stats[customer]["total_spent"]
        count = customer_stats[customer]["purchase_count"]

        customer_stats[customer]["avg_order_value"] = round(
            total / count, 2
        ) if count > 0 else 0.0

        # Convert generated set to sorted list
        customer_stats[customer]["products_bought"] = sorted(
            customer_stats[customer]["products_bought"]
        )

    # -------------------------
    # 3) Sort by total_spent DESC
    # -------------------------
    sorted_customers = dict(
        sorted(
            customer_stats.items(),
            key=lambda item: item[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customers

#daily sales trend on the basis of transactions
def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date

    Output Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        ...
    }
    """
    daily = {}

    # -------------------------
    # 1) Group & aggregate by date
    # -------------------------
    for t in transactions:
        try:
            date = t["Date"]
            amount = t["Quantity"] * t["UnitPrice"]
            customer = t["CustomerID"]
        except (KeyError, TypeError):
            continue

        if date not in daily:
            daily[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily[date]["revenue"] += amount
        daily[date]["transaction_count"] += 1
        daily[date]["unique_customers"].add(customer)

    # -------------------------
    # 2) Convert sets to counts
    # -------------------------
    for date in daily:
        daily[date]["unique_customers"] = len(daily[date]["unique_customers"])

    # -------------------------
    # 3) Sort chronologically by date key
    # -------------------------
    sorted_daily = dict(sorted(daily.items(), key=lambda item: item[0]))

    return sorted_daily

#method to find peak sales by day
def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns:
        tuple (date, revenue, transaction_count)

    Example:
        ('2024-12-15', 185000.0, 12)
    """
    daily_stats = {}

    # -------------------------
    # 1) Aggregate revenue per day
    # -------------------------
    for t in transactions:
        try:
            date = t["Date"]
            amount = t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            continue

        if date not in daily_stats:
            daily_stats[date] = {
                "revenue": 0.0,
                "transaction_count": 0
            }

        daily_stats[date]["revenue"] += amount
        daily_stats[date]["transaction_count"] += 1

    if not daily_stats:
        return None, 0.0, 0

    # -------------------------
    # 2) Find peak revenue day
    # -------------------------
    peak_date, peak_data = max(
        daily_stats.items(),
        key=lambda item: item[1]["revenue"]
    )

    return (
        peak_date,
        peak_data["revenue"],
        peak_data["transaction_count"]
    )

#method to find low performing products
def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns:
        list of tuples:
        (ProductName, TotalQuantity, TotalRevenue)
    """
    product_stats = {}

    # -------------------------
    # 1) Aggregate by ProductName
    # -------------------------
    for t in transactions:
        try:
            product = t["ProductName"]
            qty = t["Quantity"]
            revenue = t["Quantity"] * t["UnitPrice"]
        except (KeyError, TypeError):
            continue

        if product not in product_stats:
            product_stats[product] = {
                "quantity": 0,
                "revenue": 0.0
            }

        product_stats[product]["quantity"] += qty
        product_stats[product]["revenue"] += revenue

    # -------------------------
    # 2) Filter low performing products
    # -------------------------
    low_products = []

    for product, stats in product_stats.items():
        if stats["quantity"] < threshold:
            low_products.append(
                (product, stats["quantity"], stats["revenue"])
            )

    # -------------------------
    # 3) Sort by TotalQuantity ASC
    # -------------------------
    low_products.sort(key=lambda x: x[1])

    return low_products




