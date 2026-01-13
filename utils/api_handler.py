import requests

BASE_URL = "https://dummyjson.com/products"

#method to get all the products
def get_all_products():
    """
    Fetches the default list of products (first 30 by default).

    Returns:
        list of product dictionaries (data['products'])
    """
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except requests.exceptions.RequestException as e:
        print(f"API Error (get_all_products): {e}")
        return []
    

#method to get top 30 products
def get_products_with_limit(limit=30):
    """
    Fetches a specific number of products using the `limit` query param.

    Example:
        https://dummyjson.com/products?limit=100

    Returns:
        list of product dictionaries
    """
    try:
        response = requests.get(f"{BASE_URL}?limit={limit}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except requests.exceptions.RequestException as e:
        print(f"API Error (get_products_with_limit): {e}")
        return []
    
#method to get product details on the basis of product id
def get_product_by_id(product_id):
    """
    Fetches a single product by its ID.

    Example:
        https://dummyjson.com/products/1

    Returns:
        dict (single product object) OR {} if error
    """
    try:
        response = requests.get(f"{BASE_URL}/{product_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error (get_product_by_id): {e}")
        return {}

#method to search for products
def search_products(query):
    """
    Searches products using a query string.

    Example:
        https://dummyjson.com/products/search?q=phone

    Returns:
        list of matching product dictionaries
    """
    try:
        response = requests.get(f"{BASE_URL}/search", params={"q": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except requests.exceptions.RequestException as e:
        print(f"API Error (search_products): {e}")
        return []
    

import requests

BASE_URL = "https://dummyjson.com/products"


#api to fetch all products data
def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns:
        list of product dictionaries with keys:
        ['id', 'title', 'category', 'brand', 'price', 'rating']
    """
    try:
        response = requests.get(f"{BASE_URL}?limit=100", timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get("products", [])

        result = []
        for p in products:
            result.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating"),
            })

        print("Successfully fetched product data from API.")
        return result

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch products from API: {e}")
        return []
    

#helper method to save the enriched data
def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file
    """
    header = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    def safe_str(value):
        return "" if value is None else str(value)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(header) + "\n")

        for t in enriched_transactions:
            row = [
                safe_str(t.get("TransactionID")),
                safe_str(t.get("Date")),
                safe_str(t.get("ProductID")),
                safe_str(t.get("ProductName")),
                safe_str(t.get("Quantity")),
                safe_str(t.get("UnitPrice")),
                safe_str(t.get("CustomerID")),
                safe_str(t.get("Region")),
                safe_str(t.get("API_Category")),
                safe_str(t.get("API_Brand")),
                safe_str(t.get("API_Rating")),
                safe_str(t.get("API_Match")),
            ]
            f.write("|".join(row) + "\n")


#method to create product mapping
def create_product_mapping(api_products, transactions, output_file="data/enriched_sales_data.txt"):
    """
    Creates product mapping, enriches sales transactions, and saves enriched data to file.

    Returns:
        (product_mapping, enriched_transactions)
    """
    product_mapping = {}

    # 1) Create mapping: id -> info
    for product in api_products:
        try:
            product_id = product["id"]
            product_mapping[product_id] = {
                "title": product.get("title"),
                "category": product.get("category"),
                "brand": product.get("brand"),
                "rating": product.get("rating"),
            }
        except (KeyError, TypeError):
            continue

    # 2) Enrich transactions
    enriched_transactions = []
    for t in transactions:
        enriched = t.copy()

        # Convert ProductID like "P101" -> 101
        try:
            pid_num = int(str(t.get("ProductID", "")).replace("P", "").strip())
        except Exception:
            pid_num = None

        api_data = product_mapping.get(pid_num)

        if api_data:
            enriched["API_Category"] = api_data.get("category")
            enriched["API_Brand"] = api_data.get("brand")
            enriched["API_Rating"] = api_data.get("rating")
            enriched["API_Match"] = True
        else:
            enriched["API_Category"] = None
            enriched["API_Brand"] = None
            enriched["API_Rating"] = None
            enriched["API_Match"] = False

        enriched_transactions.append(enriched)

    # 3) Save enriched data
    save_enriched_data(enriched_transactions, filename=output_file)

    return product_mapping, enriched_transactions



    