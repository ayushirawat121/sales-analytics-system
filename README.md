# sales-analytics-system

------------------1. Project Overview--------------------

This project implements a complete Sales Analytics System using Python.
It reads raw sales transaction data, cleans and validates it, performs multiple analytical computations, enriches the data using an external API, and generates a comprehensive text-based sales report.
The system is modular and follows clean separation of concerns across data handling, processing, API integration, reporting, and execution flow.

-------------------2. Project Structure-----------------

sales-analytics-system/
├── main.py
├── requirements.txt
├── README.txt
├── utils/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── data_processor.py
│   ├── api_handler.py
│   └── report_generator.py
├── data/
│   ├── sales_data.txt
│   └── enriched_sales_data.txt   (generated)
└── output/
    └── sales_report.txt           (generated)


--------------------3. Features Implemented-------------------------

1. Robust file reading with encoding handling
2. Data parsing, cleaning, and validation
3. Optional filtering by region and transaction amount
4. Sales analytics:
        a. Total revenue
        b. Region-wise performance
        c. Top products and customers
        d. Daily sales trends
        e. Peak sales day
        f. Product performance analysis

5. API integration using DummyJSON Products API
6. Data enrichment and persistence
7. Comprehensive formatted text report generation
8. Graceful error handling and user-friendly console output

-----------------------4. Requirements----------------------

1. Python 3.8+
2.External dependency - requests>= 2.31.0

----------------------5. How to run the application------------

1. Ensure you are in the project root directory.
2. Place the input file at - data/sales_data.txt
3. Run the program - python main.py


----------------------6. Program Execution Flow-------------------

The application performs the following steps:
    a. Reads and parses the sales data file    
    b. Cleans and validates transactions
    c. Prompts the user for optional filters
    d. Performs sales analytics
    e. Fetches product data from the DummyJSON API
    f. Enriches sales transactions
    g. Saves enriched data to file
    h. Generates a comprehensive sales report
    i. Displays completion status and file locations

----------------------7. Output files Generated------------------

| File                           | Description                              |
| ------------------------------ | ---------------------------------------- |
| `data/enriched_sales_data.txt` | Sales data enriched with API information |
| `output/sales_report.txt`      | Detailed analytics report                |


---------------------8.Error Handling--------------------------

a. File I/O errors are handled gracefully
b. API failures do not crash the application
c. User-friendly messages are displayed for all major steps
d. The program continues execution wherever possible


