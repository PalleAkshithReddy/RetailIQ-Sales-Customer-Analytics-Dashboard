# 🛒 RetailIQ — Sales & Customer Analytics Dashboard

> **A complete end-to-end Data Analytics portfolio project** demonstrating Python, SQL, EDA,
> RFM Analysis, KPI Dashboards, and Business Intelligence using real-world retail data patterns.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-336791?logo=postgresql&logoColor=white)

---

## 📌 Project Overview

**RetailIQ** simulates a real-world Indian retail analytics workflow:

- 🏭 **50,000 transactions** across 3 years (2022–2024)
- 👥 **2,000 customers** with segmentation & demographics
- 🛍️ **80 products** across 8 categories
- 🏪 **12 stores** across major Indian cities
- 💡 **25+ SQL queries** covering KPIs, cohorts, RFM, churn
- 📊 **10 matplotlib charts** + interactive Streamlit dashboard

---

## 🗂️ Project Structure

```
retailiq/
├── data/
│   ├── generate_data.py        # Synthetic data generator
│   ├── customers.csv           # 2,000 customer records
│   ├── products.csv            # 80 products, 8 categories
│   ├── stores.csv              # 12 store locations
│   ├── transactions.csv        # 50,000 transactions
│   └── rfm_segments.csv        # RFM analysis output
│
├── analysis/
│   └── eda_analysis.py         # EDA + 10 matplotlib charts
│
├── sql/
│   └── retail_analytics.sql    # 25+ SQL queries (7 sections)
│
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
│
├── reports/
│   ├── 01_monthly_revenue.png
│   ├── 02_category_revenue.png
│   ├── 03_customer_segments.png
│   ├── 04_top_products.png
│   ├── 05_payment_channels.png
│   ├── 06_city_revenue.png
│   ├── 07_demographics.png
│   ├── 08_quarterly_yoy.png
│   ├── 09_discount_analysis.png
│   ├── 10_rfm_segments.png
│   └── business_insights.txt
│
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourname/retailiq.git
cd retailiq
pip install -r requirements.txt
```

### 2. Generate Data
```bash
python data/generate_data.py
```

### 3. Run EDA Analysis (generates 10 charts)
```bash
python analysis/eda_analysis.py
```

### 4. Launch Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. SQL Queries
Load the CSV files into PostgreSQL and run `sql/retail_analytics.sql`.

---

## 📊 Key Business KPIs

| Metric | Value |
|--------|-------|
| Total Revenue | ₹68.6 Crore |
| Total Profit | ₹25.6 Crore |
| Profit Margin | 37.3% |
| Total Transactions | 50,000 |
| Unique Customers | 2,000 |
| Avg Order Value | ₹13,718 |
| Return Rate | 4.86% |
| Avg Rating | 4.02 / 5 |

---

## 🧠 Analytics Modules

### 1. Data Generation (`data/generate_data.py`)
- Synthetic Faker-based customer profiles
- Seasonal transaction patterns (Q4 festive surge)
- Realistic pricing with cost & margin modeling
- RFM-ready customer & transaction structure

### 2. Exploratory Data Analysis (`analysis/eda_analysis.py`)
| Chart | Insight |
|-------|---------|
| Monthly Revenue Trend | Seasonal patterns & growth |
| Category Revenue | Best performing categories |
| Customer Segments | Premium vs Regular vs Budget |
| Top 10 Products | Revenue leaders |
| Payment Methods | UPI dominance in India |
| City Revenue | Geographic hotspots |
| Demographics | Age & gender revenue split |
| Quarterly YoY | Year-over-year growth |
| Discount Analysis | Discount impact on AOV |
| RFM Heatmap | Customer value segments |

### 3. SQL Query Library (`sql/retail_analytics.sql`)
**7 sections, 25+ queries:**
- Section 1: Revenue & Profit KPIs
- Section 2: Product & Category Analysis (with ABC classification)
- Section 3: Customer Analytics (RFM, CLV, Churn)
- Section 4: Store & Regional Analysis
- Section 5: Payment & Channel Analytics
- Section 6: Discount & Return Analysis
- Section 7: Advanced (Moving Averages, Market Basket Analysis)

### 4. Streamlit Dashboard (`dashboard/app.py`)
- Real-time filters: Year, Category, Segment, Channel
- Interactive Plotly charts (hover, zoom, filter)
- KPI cards with live calculations
- Data explorer table with 500 rows

---

## 💡 Key Business Insights

1. **Electronics** is the top revenue category — focus marketing budgets here
2. **Q4 (Oct–Dec)** shows peak sales due to Diwali festive season
3. **Premium segment** customers have 2.3× higher average order value
4. **Loyalty members** spend ~35% more per transaction
5. **26–45 age group** contributes ~55% of total revenue
6. **UPI & Net Banking** dominate payment methods
7. **In-Store channel** drives the most transactions
8. **Return rate of ~5%** is primarily driven by Electronics

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib + Seaborn | Static visualizations |
| Plotly | Interactive charts |
| Streamlit | Web dashboard |
| Faker | Synthetic data generation |
| SQL (PostgreSQL) | Data querying & analytics |
| Excel/CSV | Data storage & reporting |

---

## 📁 Portfolio Use

This project demonstrates:
- ✅ End-to-end data pipeline (generation → cleaning → analysis → visualization)
- ✅ Python proficiency (OOP, Pandas, NumPy, Matplotlib)
- ✅ SQL mastery (window functions, CTEs, subqueries, aggregations)
- ✅ Business acumen (KPIs, RFM, CLV, churn analysis)
- ✅ Dashboard development (Streamlit + Plotly)
- ✅ Data storytelling (insights report)

---

## 👤 Author

**[Palle Akshith Reddy]**  
Data Analyst | Python • SQL • Power BI  
📧 palleakshithreddy394@gmail.com  
🔗 [LinkedIn]([https://linkedin.com](https://www.linkedin.com/in/palle394))

---

*RetailIQ is a portfolio project using 100% synthetic data. No real customer information is used.*
