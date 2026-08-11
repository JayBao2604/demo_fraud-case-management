# Fraud Lifecycle Management

A banking fraud detection and case management simulation built with **Python, Streamlit, Pandas, Plotly, SQLite, and NetworkX**.

The project demonstrates a simplified **Fraud Lifecycle Management (FLM)** solution, where banking transaction events are processed through KYC, AML, transaction screening, rule evaluation, risk scoring, alert generation, and case management.

---

## 1. Project Overview

**Fraud Lifecycle Management** simulates how a modern banking system can detect, assess, and manage potentially fraudulent transactions.

The system processes transaction data originating from **Mobile Banking** and applies multiple layers of controls, including:

* **eKYC** – Customer identity and KYC status verification
* **AML** – Anti-Money Laundering screening
* **Transaction Screening** – Transaction-level risk checks
* **Rule Engine** – Detection of predefined fraud patterns
* **Risk Engine** – Calculation of transaction risk scores
* **Alert Engine** – Generation and prioritization of fraud alerts
* **Case Management** – Investigation and lifecycle management of suspicious cases
* **Reporting** – Monitoring and analysis of fraud-related activities

The project is designed primarily for **demonstration, learning, and prototyping purposes**.

---

## 2. Key Features

### Dashboard

Provides an overview of the fraud monitoring environment, including transaction activity, risk indicators, alerts, and case statistics.

### Live Transaction

Simulates incoming banking transactions and demonstrates how they are processed through the fraud detection pipeline.

### eKYC

Evaluates customer KYC information and identifies incomplete or potentially problematic customer profiles.

### AML

Performs basic Anti-Money Laundering checks to identify transactions or customers associated with higher AML risk.

### Rule Engine

Applies predefined fraud detection rules to transaction data.

### Risk Score

Calculates a risk score based on detected indicators and rule violations.

### Fraud Alert

Generates alerts when transactions exceed predefined risk thresholds.

### Case Management

Allows suspicious transactions and alerts to be organized into investigation cases and tracked through their lifecycle.

### Report

Provides reporting and analytical views for fraud monitoring and investigation activities.

---

## 3. Fraud Detection Rules

The demo includes a collection of rule scenarios representing common fraud risk indicators:

| Rule                | Description                                            |
| ------------------- | ------------------------------------------------------ |
| `Fr001`             | Fraud detection rule                                   |
| `Fr023`             | Fraud detection rule                                   |
| `Fr025`             | Fraud detection rule                                   |
| `New Device`        | Transaction from a previously unseen device            |
| `Large Amount`      | Transaction exceeds a predefined amount threshold      |
| `Velocity`          | Unusual transaction frequency within a specific period |
| `Night Transaction` | Transaction performed during a high-risk time period   |
| `Merchant Risk`     | Transaction involving a high-risk merchant             |
| `Foreign Country`   | Transaction associated with a foreign country          |
| `AML High`          | High AML risk indicator                                |
| `KYC Incomplete`    | Customer KYC information is incomplete                 |

> The rules are configurable and can be extended to support additional fraud scenarios.

---

## 4. Technology Stack

| Technology      | Purpose                                       |
| --------------- | --------------------------------------------- |
| **Python 3.12** | Core application and business logic           |
| **Streamlit**   | Web-based application interface               |
| **Pandas**      | Transaction and data processing               |
| **Plotly**      | Interactive data visualization                |
| **SQLite**      | Lightweight database storage                  |
| **NetworkX**    | Relationship and transaction network analysis |

---

## 5. Project Structure

```text
FraudLifecycleManagement/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   └── ...
│
├── modules/
│   └── ...
│
├── rules/
│   └── ...
│
├── pages/
│   └── ...
│
├── assets/
│   └── ...
│
└── data/
    └── ...
```

### Directory Description

* **`app.py`** – Main Streamlit application entry point
* **`database/`** – Database configuration, schema, and data access components
* **`modules/`** – Core application modules and business logic
* **`rules/`** – Fraud and AML detection rules
* **`pages/`** – Streamlit application pages
* **`assets/`** – Static assets such as images and UI resources
* **`data/`** – Sample transaction and supporting datasets
* **`requirements.txt`** – Python dependencies

---

## 6. Installation

### Prerequisites

Make sure the following are installed:

* Python 3.12 or later
* pip

### Install Dependencies

Clone the repository and navigate to the project directory:

```bash
cd FraudLifecycleManagement
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 7. Run the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

After starting the application, open the URL displayed in the terminal to access the **Fraud Lifecycle Management Dashboard**.

---

## 8. Project Objectives

This project is intended to demonstrate:

* How banking transaction events can be monitored for fraud
* How KYC and AML controls can be integrated into transaction screening
* How configurable fraud rules can be implemented
* How multiple risk indicators can contribute to a risk score
* How suspicious transactions can trigger fraud alerts
* How alerts can be converted into investigation cases
* How transaction relationships can be analyzed using network-based techniques
* How fraud monitoring data can be presented through an interactive dashboard

---

## 9. Disclaimer

This project is a **simulation and proof-of-concept** for educational and demonstration purposes.

It does not represent a production-ready banking fraud detection platform and should not be used as a replacement for real-world financial crime monitoring, AML compliance, KYC processes, or banking security controls.

---

## 10. Author

**Author:**
