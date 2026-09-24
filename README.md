# Oracle Fusion / Autonomous DB: End-to-End Enterprise 360° Supplier Risk Auditor

## System Architecture

```
+------------------------------------+      +----------------------------------+
|  Oracle Fusion / Autonomous DB     |      | Real-Time External Risk Signals  |
|  View: V_SUPPLIER_RISK_360         |      | (Port Congestion, Downgrades)   |
+-----------------+------------------+      +-----------------+----------------+
                  |                                           |
                  +---------------------+---------------------+
                                        |
                                        v (Unified JSON Payload)
                  +---------------------+---------------------+
                  |  Step 3: OCI Functions Engine             |
                  |  File: handler.py (google-genai SDK)      |
                  +---------------------+---------------------+
                                        |
                                        v (Gemini 2.5 Flash API)
                  +---------------------+---------------------+
                  |  Step 2: Gemini AI Auditor Agent          |
                  |  Structured JSON Audit Output             |
                  +---------------------+---------------------+
                                        |
                                        v (APEX_WEB_SERVICE / ORDS)
                  +---------------------+---------------------+
                  |  Step 4: Oracle APEX PL/SQL Governance    |
                  |  Package: PKG_SUPPLIER_RISK_GOVERNANCE    |
                  |  Table  : AI_FINANCIAL_AUDIT_LOG          |
                  +---------------------+---------------------+
                                        |
                                        +---> HOLD_PO_PAYOUTS (UPDATE po_headers_all)
                                        +---> REROUTE_SUPPLIER_ALLOCATION (APEX_APPROVAL)
                                        +---> APPROVE (Log Audit Clear)
```

---

## Workspace Project Files

| File | Description |
| :--- | :--- |
| 🗄️ [`v_supplier_risk_360.sql`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/v_supplier_risk_360.sql) | **Step 1**: Oracle SQL DDL script for 360-degree supplier risk database view. |
| 🤖 [`system_instruction.txt`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/system_instruction.txt) | **Step 2**: Plaintext System Instruction prompt for Gemini AI Auditor. |
| 🐍 [`gemini_auditor_agent.py`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/gemini_auditor_agent.py) | **Step 2**: Python SDK implementation (`google-genai`) with Pydantic JSON validation. |
| 📄 [`sample_payload.json`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/sample_payload.json) | **Step 3**: Input JSON payload combining `V_SUPPLIER_RISK_360` & external SCM signals. |
| ⚙️ [`handler.py`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/handler.py) | **Step 3**: OCI Function entrypoint script. |
| 📦 [`func.yaml`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/func.yaml) | **Step 3**: OCI Functions deployment manifest. |
| 🛠️ [`supplier_risk_governance_pkg.sql`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/supplier_risk_governance_pkg.sql) | **Step 4**: PL/SQL audit log table DDL & governance package for APEX/ORDS. |
| 🧪 [`test_suite.json`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/test_suite.json) | **Step 5**: Test matrix JSON definitions for Test Cases 1, 2, and 3. |
| 🐍 [`run_verification_matrix.py`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/run_verification_matrix.py) | **Step 5**: Python verification script for testing M0-M5 evaluation logic. |
| 📜 [`apex_verification_test.sql`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/apex_verification_test.sql) | **Step 5**: PL/SQL test script for APEX / SQL Developer verification. |

---

## Step 5: Test Verification Matrix (M0–M5 Evaluation Logic)

| Test Case | Inputs | Expected Gemini Output | Triggered Action |
| :--- | :--- | :--- | :--- |
| **1. Healthy Vendor** | Quick Ratio: `1.8`, Debt/Equity: `1.1`, On-Time Delivery: `96%` | `overall_risk_rating`: `"LOW"`<br>`recommended_action`: `"APPROVE"` | POs remain active; logged in `AI_FINANCIAL_AUDIT_LOG`. |
| **2. Liquidity Crisis** | Quick Ratio: `0.7`, Debt/Equity: `3.5`, Active POs: `$500k` | `overall_risk_rating`: `"HIGH"`<br>`recommended_action`: `"HOLD_PO_PAYOUTS"` | Updates `po_headers_all` status to `ON_HOLD`. |
| **3. Supply Bottleneck** | Single Source: `1`, Delivery: `68%`, Credit Rating: `BB` | `overall_risk_rating`: `"CRITICAL"`<br>`recommended_action`: `"REROUTE_SUPPLIER_ALLOCATION"` | Triggers Oracle BPM approval escalation task. |

---

## Running Verification Tests

### Python Automated Runner:
```bash
export GEMINI_API_KEY="your-api-key"
python run_verification_matrix.py
```

### Oracle APEX / PL/SQL Verification:
Run [`apex_verification_test.sql`](file:///config/.gemini/antigravity/scratch/oracle-supplier-risk-360/apex_verification_test.sql) in SQL Developer or APEX SQL Workshop to verify database table insertion and automated workflow triggers.
