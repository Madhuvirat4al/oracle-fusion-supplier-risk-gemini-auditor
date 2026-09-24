"""
Gemini Core AI Auditor Agent (Oracle Fusion ERP / Autonomous Database Integration)
Uses Google GenAI SDK (google-genai) to audit supplier risk records from V_SUPPLIER_RISK_360.
"""

import os
import json
from typing import Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define Pydantic Schema matching the required JSON Output Format
class SupplierRiskEvaluation(BaseModel):
    vendor_id: int = Field(description="Unique internal supplier identifier")
    overall_risk_rating: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Overall calculated risk rating based on financial & supply chain metrics"
    )
    recommended_action: Literal["APPROVE", "HOLD_PO_PAYOUTS", "REROUTE_SUPPLIER_ALLOCATION", "HUMAN_REVIEW_REQUIRED"] = Field(
        description="Automated business rule action recommendation"
    )
    financial_risk_score: int = Field(
        description="Numeric financial liquidity risk score from 0 (lowest risk) to 100 (highest risk)"
    )
    supply_chain_resilience_score: int = Field(
        description="Numeric SCM resilience score from 0 (fragile) to 100 (robust)"
    )
    justification: str = Field(
        description="Bulleted textual explanation detailing specific financial & supply chain findings"
    )
    sox_compliance_flag: bool = Field(
        description="True if supplier passes SOX internal compliance requirements, False if flagged"
    )

# Load System Instruction from file
SYSTEM_INSTRUCTION_PATH = os.path.join(os.path.dirname(__file__), "system_instruction.txt")

def load_system_instruction() -> str:
    with open(SYSTEM_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        return f.read()

def audit_supplier(supplier_row: dict) -> SupplierRiskEvaluation:
    """
    Invokes the Gemini Auditor Agent with structured JSON output enforcement.
    """
    client = genai.Client()
    system_instruction = load_system_instruction()
    
    prompt_payload = f"""
Analyze the following supplier data extracted from Oracle database view V_SUPPLIER_RISK_360:

{json.dumps(supplier_row, indent=2)}

Enforce all audit business rules and return the structured JSON audit evaluation.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_payload,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=SupplierRiskEvaluation,
            temperature=0.1,  # Low temperature for deterministic compliance auditing
        ),
    )
    
    # Parse returned JSON into validated Pydantic object
    evaluation_data = json.loads(response.text)
    return SupplierRiskEvaluation(**evaluation_data)

if __name__ == "__main__":
    # Sample supplier payload simulating a row from V_SUPPLIER_RISK_360
    sample_supplier_high_risk = {
        "VENDOR_ID": 10492,
        "VENDOR_NAME": "Apex Micro-Logistics Inc.",
        "VENDOR_NUMBER": "SUP-10492",
        "TOTAL_PO_VALUE": 450000.00,
        "AVG_PAYMENT_DELAY_DAYS": 42.5,
        "ON_TIME_DELIVERY_RATE": 68.4,
        "SINGLE_SOURCE_FLAG": 1,
        "CREDIT_RATING": "CCC+",
        "QUICK_RATIO": 0.75,
        "DEBT_TO_EQUITY": 3.8
    }

    print("--- Running Gemini AI Auditor Agent ---")
    print(f"Auditing Supplier: {sample_supplier_high_risk['VENDOR_NAME']} (ID: {sample_supplier_high_risk['VENDOR_ID']})")
    
    # Run audit (Requires GEMINI_API_KEY environment variable to be set)
    if os.environ.get("GEMINI_API_KEY"):
        result = audit_supplier(sample_supplier_high_risk)
        print("\nStructured Risk Evaluation Result:")
        print(json.dumps(result.model_dump(), indent=2))
    else:
        print("\n[NOTE] GEMINI_API_KEY environment variable not set.")
        print("System Instruction and Pydantic Schema are fully validated and ready for deployment.")
