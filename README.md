<div align="center">

# 🛡️ AEGIS AI AUDITOR
### **Oracle Fusion Cloud ERP Autonomous Supplier Diligence & Governance System**

![Oracle ERP](https://img.shields.io/badge/Oracle-Fusion_Cloud_ERP-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-8E44AD?style=for-the-badge&logo=googlecloud&logoColor=white)
![Oracle Autonomous DB](https://img.shields.io/badge/Oracle-Autonomous_Database-C70039?style=for-the-badge&logo=oracle&logoColor=white)
![SOX Compliance](https://img.shields.io/badge/SOX-Internal_Controls_Compliant-10B981?style=for-the-badge&logo=shield&logoColor=white)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PL/SQL](https://img.shields.io/badge/Oracle-PL%2FSQL_APEX-00F2FE?style=for-the-badge&logo=oracle&logoColor=black)

<p align="center">
  <b>An end-to-end enterprise solution combining Oracle ERP database aggregation, Google Gemini GenAI agents, OCI Functions, Oracle APEX PL/SQL governance handlers, and an interactive real-time Command Center with an integrated Universal RAG Chatbot.</b>
</p>

[Key Features](#-key-features) • [System Screenshots](#-system-screenshots) • [System Architecture](#-system-architecture) • [5-Step Technical Stack](#-5-step-technical-stack) • [Quick Start & Local Dashboard](#-quick-start--local-dashboard)

---

</div>

> [!IMPORTANT]
> **BUSINESS PROBLEM SOLVED**: Enterprise procurement systems in Oracle Fusion ERP often suffer from fragmented supplier visibility. Financial distress (low quick ratio, high debt-to-equity) combined with single-source supply chain bottlenecks leads to costly line-down shutdowns. **Aegis AI Auditor** continuously calculates a 360-degree supplier risk matrix over rolling 180-day windows and autonomously enforces purchase order holds and BPM workflow escalations.

---

## 📸 System Screenshots

### 1. Enterprise Command Center Dashboard
![Enterprise Command Center Dashboard Overview](assets/dashboard_overview.png)

### 2. Interactive Telemetry Stress-Test Sandbox
![Supplier Risk Telemetry Sandbox](assets/stress_test_sandbox.png)

### 3. Universal Gemini RAG AI Chatbot Assistant
![Universal Gemini Enterprise Assistant Chatbot](assets/universal_rag_chatbot.png)

---

## 🌟 Key Features

| Feature | Description | Enterprise Impact |
| :--- | :--- | :--- |
| **360° Supplier Risk Engine** | Aggregates `PO_VENDORS`, `PO_HEADERS_ALL`, `AP_INVOICES_ALL`, and `PO_LINE_LOCATIONS_ALL`. | Eliminates Cartesian join metric inflation; calculates 180-day delivery & liquidity metrics. |
| **Gemini 2.5 Flash Auditor Agent** | GenAI agent trained on financial diligence & SCM business rules with strict JSON Schema output. | Evaluates Quick Ratio, Debt-to-Equity, Credit Ratings, and Single-Source Category risks. |
| **Oracle APEX & PL/SQL Governance** | Package `PKG_SUPPLIER_RISK_GOVERNANCE` with table `AI_FINANCIAL_AUDIT_LOG`. | Automatically places `ON_HOLD` status on open POs or triggers Oracle BPM escalation tasks. |
| **Universal RAG AI Chatbot** | Embedded real-time natural language query assistant for ERP data & general knowledge. | Answers complex queries like *"suppliers with rejection data"* or *"who is Virat Kohli"* with zero restrictions. |
| **Interactive Stress-Test Sandbox** | Live web command center with sliders for Quick Ratio, PO Value, Delivery Rates, and Credit Ratings. | Real-time visual feedback, risk badges (`LOW`, `HIGH`, `CRITICAL`), and reasoning logs. |

---

## 📐 System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                ORACLE FUSION CLOUD ERP LAYER                                      |
|  +--------------------+  +------------------+  +-------------------+  +------------------------+  |
|  |     PO_VENDORS     |  |  PO_HEADERS_ALL  |  |  AP_INVOICES_ALL  |  |  PO_LINE_LOCATIONS_ALL |  |
|  +---------+----------+  +--------+---------+  +---------+---------+  +-----------+------------+  |
+------------|----------------------|----------------------|------------------------|---------------+
             +----------------------+----------+-----------+------------------------+
                                               |
                                               v
                        +----------------------------------------------+
                        |      VIEW: V_SUPPLIER_RISK_360 (Oracle DDL)  |
                        |      Calculates 180-Day Metrics per Vendor   |
                        +----------------------+-----------------------+
                                               |
                                               v
                        +----------------------------------------------+
                        |        OCI FUNCTIONS / REST PAYLOAD ENGINE   |
                        |        Combines ERP Metrics + External Signals|
                        +----------------------+-----------------------+
                                               |
                                               v
                        +----------------------------------------------+
                        |    GOOGLE GEMINI 2.5 FLASH AUDITOR AGENT     |
                        |    Enforces Liquidity & Bottleneck Rules     |
                        +----------------------+-----------------------+
                                               |
                                               v
                        +----------------------------------------------+
                        |  ORACLE APEX / PL/SQL GOVERNANCE PACKAGE     |
                        |  (PKG_SUPPLIER_RISK_GOVERNANCE)              |
                        |  - Updates PO_HEADERS_ALL to ON_HOLD          |
                        |  - Logs to AI_FINANCIAL_AUDIT_LOG (SOX Pass) |
                        +-------------------------------+--------------+
                                                        |
                                                        v
                        +----------------------------------------------+
                        |   AEGIS AI COMMAND CENTER & RAG CHATBOT UI   |
                        |   Interactive Telemetry & Stress Test Sandbox|
                        +----------------------------------------------+
```

---

## 🛠️ 5-Step Technical Stack

### Step 1: Database Aggregation View (`v_supplier_risk_360.sql`)
Creates an optimized database view preventing multi-table row explosion using modular Common Table Expressions (CTEs).

### Step 2: Gemini Core System Instructions (`system_instruction.txt` & `gemini_auditor_agent.py`)
Enforces financial liquidity and supply chain disruption rules with Pydantic JSON schema output.

### Step 3: Payload Integration Engine (`handler.py` & `func.yaml`)
Prepares structured JSON payloads combining Oracle DB metrics with real-time port congestion indices for OCI Functions deployment.

### Step 4: Oracle APEX & PL/SQL Governance Package (`supplier_risk_governance_pkg.sql`)
Executes governance decisions inside Oracle Fusion Cloud ERP via PL/SQL package `PKG_SUPPLIER_RISK_GOVERNANCE`.

### Step 5: Test Verification Matrix (`test_suite.json` & `run_verification_matrix.py`)
Provides complete end-to-end verification across Test Cases 1 (Healthy), 2 (Liquidity Crisis), and 3 (Supply Bottleneck).

---

## 💻 Quick Start & Local Dashboard

### 1. Run the Command Center Server
```bash
cd oracle-fusion-supplier-risk-gemini-auditor
python3 server.py
```

### 2. Access the Interactive Dashboard
Open your browser at **[http://localhost:8080](http://localhost:8080)**.

### 3. Detailed Walkthrough Document
For complete working steps and SQL code scripts, see [WALKTHROUGH.md](WALKTHROUGH.md).

---

<div align="center">
  <b>Built for Oracle Fusion Cloud ERP & Autonomous Database Integration</b><br>
  <i>Powered by Google Gemini 2.5 Flash & Aegis AI Architecture</i>
</div>
