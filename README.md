# Fraud Lifecycle Management Demo

## Overview

This project simulates a banking Fraud Lifecycle Management system.

The system demonstrates how transaction data from Mobile Banking
is analyzed using eKYC, AML and Fraud Detection rules.

The solution follows a real banking architecture:

Core Banking
↓

Account / Card / Credit

↓

Transaction Event

↓

eKYC

↓

AML

↓

Transaction Screening

↓

Rule Engine

↓

Risk Engine

↓

Alert Engine

↓

Case Management

---

## Technology

Python 3.12

Streamlit

Pandas

Plotly

SQLite

NetworkX

---

## Folder Structure

```
FraudLifecycleManagement/

app.py

requirements.txt

README.md

database/

modules/

rules/

pages/

assets/

data/
```

---

## Features

✔ Dashboard

✔ Live Transaction

✔ eKYC

✔ AML

✔ Rule Engine

✔ Risk Score

✔ Fraud Alert

✔ Case Management

✔ Report

---

## Rules

Fr001

Fr023

Fr025

New Device

Large Amount

Velocity

Night Transaction

Merchant Risk

Foreign Country

AML High

KYC Incomplete

---

## Run

Install dependencies

```
pip install -r requirements.txt
```

Run project

```
streamlit run app.py
```

---

## Author
