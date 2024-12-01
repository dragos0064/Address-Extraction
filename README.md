# **Address Extraction**

This project is a Python-based solution for extracting and analyzing address data from a list of company websites. The extracted data is organized in a structured format and visualized to provide geographical insights.

---

## **Features**

- **Data Extraction**:
  - Extracts addresses in a structured format including **country**, **region**, **city**, **postcode**, **road**, and **house number**.
  - Processes data from both structured and unstructured website content.

- **Data Visualization**:
  - Generates pie charts for visualizing geographic distributions of the extracted data.
  - Focuses on countries and regions (e.g., U.S. states).

- **Integration Ready**:
  - Modular design supports integration with other datasets and workflows.
  - Advanced scraping techniques using random user agents for enhanced reliability.

---

## **File Structure**

### **Core Files**
- **`main.py`**: Coordinates execution, input handling, and invokes address parsing and visualization.
- **`parser.py`**: Parses and structures address data using geolocation services and regex.
- **`crawler.py`**: Fetches website data for processing.
- **`io_operations.py`**: Manages file input/output (e.g., CSV, Parquet).
- **`user_agent_provider.py`**: Supplies randomized user-agent strings to prevent scraping detection.

### **Input Files**
- **`website.snappy.parquet`**: Contains the list of company websites to process.
- **`user-agents.txt`**: A text file with user-agent strings for web crawling.

### **Output Files**
- **`addresses.csv`**: A structured CSV file containing the extracted addresses.
- **Pie Charts**: Visual charts showcasing address distributions.

# **Running the Program**

### **Prepare Input Files**
- Ensure `website.snappy.parquet` and `user-agents.txt` are in the project directory.


### **Run the Script**
To execute the program, run the following command:
```bash
python main.py bash
```
## **View Outputs**

- The extracted addresses will be saved as `output/addresses.csv`.
- Pie charts displaying geographic distributions will appear after processing.

---

## **Example Workflow**

### **Input**
A file like `website.snappy.parquet` containing company domains.

### **Output CSV**
Extracted address data is saved in a structured format:


![image](https://github.com/user-attachments/assets/1e819bfe-37b9-4600-b2d1-5eb6825c5bc8)

### **Pie Chart**

Visualize the proportion of addresses across different countries or regions using the generated pie charts. These charts provide an intuitive way to analyze the geographic distribution of the extracted addresses.


![image](https://github.com/user-attachments/assets/2d2b020f-c279-48f0-a802-2ed09bfbbfce)

---

### **Challenges**

- **Address Extraction**: Handling diverse formats and unstructured data from multiple sources can be complex.
- **Web Scraping**: Overcoming rate limits, CAPTCHAs, and dynamically loaded content requires robust techniques.


## **License**

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software under the terms of the license. 
















