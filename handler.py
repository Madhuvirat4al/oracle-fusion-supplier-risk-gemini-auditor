"""
OCI Function Entrypoint (handler.py)
Oracle Cloud Infrastructure (OCI) Function & Gemini Integration Engine for Oracle Fusion ERP.
"""

import io
import json
import os
import logging
from google import genai
from google.genai import types

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load System Instruction Prompt
SYSTEM_INSTRUCTION_PATH = os.path.join(os.path.dirname(__file__), "system_instruction.txt")

def get_system_instruction() -> str:
    if os.path.exists(SYSTEM_INSTRUCTION_PATH):
        with open(SYSTEM_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return """You are the Enterprise Financial Diligence & Supply Chain Resilience Auditor for Oracle Fusion ERP.
Your task is to analyze supplier financial health metrics alongside supply chain delivery data and output a structured risk evaluation in JSON.

BUSINESS RULES TO ENFORCE:
1. FINANCIAL LIQUIDITY RISK:
   - If Quick Ratio < 1.0 OR Debt-to-Equity > 2.5, set financial_risk to "HIGH".
   - If Credit Rating is below 'BBB-', set financial_risk to "HIGH".

2. SUPPLY CHAIN DISRUPTION RISK:
   - If On-Time Delivery Rate < 80% AND Single Source Flag == 1, set supply_chain_risk to "CRITICAL".
   - If Average Payment Delay > 30 days, flag for liquidity bottleneck.

3. ACTION MATRIX:
   - If financial_risk == "HIGH" AND active PO total > $100,000 -> Action: "HOLD_PO_PAYOUTS".
   - If supply_chain_risk == "CRITICAL" -> Action: "REROUTE_SUPPLIER_ALLOCATION".
   - If both risks are LOW/MEDIUM -> Action: "APPROVE".
   - If complex conflicting factors exist -> Action: "HUMAN_REVIEW_REQUIRED".

OUTPUT FORMAT:
Return STRICT JSON ONLY matching this schema:
{
  "vendor_id": NUMBER,
  "overall_risk_rating": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "recommended_action": "APPROVE" | "HOLD_PO_PAYOUTS" | "REROUTE_SUPPLIER_ALLOCATION" | "HUMAN_REVIEW_REQUIRED",
  "financial_risk_score": NUMBER (0-100),
  "supply_chain_resilience_score": NUMBER (0-100),
  "justification": "Clear bulleted textual reason explaining financial & SCM findings.",
  "sox_compliance_flag": BOOLEAN
}"""

def run_financial_diligence_agent(request_payload: dict) -> dict:
    """
    Core Execution Engine: Sends supplier context + real-time signals to Gemini 2.5 Flash
    with strict JSON response mime type enforcement.
    """
    client = genai.Client()
    system_instruction = get_system_instruction()
    
    prompt = f"Analyze this supplier payload and produce the JSON audit assessment:\n{json.dumps(request_payload, indent=2)}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    
    return json.loads(response.text)

def handler(ctx, data: io.BytesIO = None):
    """
    OCI Functions Fn Project Entrypoint
    """
    logger.info("OCI Function handler invoked for Supplier Diligence Audit")
    try:
        body = json.loads(data.getvalue()) if data else {}
    except Exception as e:
        logger.error(f"Failed to parse input JSON payload: {e}")
        body = {}
        
    try:
        audit_result = run_financial_diligence_agent(body)
        
        # Check if running under OCI Fn FDK environment
        try:
            from fdk import response
            return response.Response(
                ctx,
                response_data=json.dumps(audit_result),
                headers={"Content-Type": "application/json"}
            )
        except ImportError:
            # Standalone / non-FDK fallback execution
            return audit_result
            
    except Exception as err:
        logger.error(f"Error executing Gemini Diligence Audit: {err}", exc_info=True)
        err_response = {
            "error": str(err),
            "status": "FAILED"
        }
        try:
            from fdk import response
            return response.Response(
                ctx,
                status_code=500,
                response_data=json.dumps(err_response),
                headers={"Content-Type": "application/json"}
            )
        except ImportError:
            return err_response

if __name__ == "__main__":
    # Local verification mode using sample_payload.json
    payload_path = os.path.join(os.path.dirname(__file__), "sample_payload.json")
    if os.path.exists(payload_path):
        with open(payload_path, "r") as f:
            sample_data = json.load(f)
            
        print("=== Local Execution Test ===")
        print(f"Payload Vendor: {sample_data['supplier_context']['vendor_name']}")
        
        if os.environ.get("GEMINI_API_KEY"):
            res = run_financial_diligence_agent(sample_data)
            print("\nAudit Response:")
            print(json.dumps(res, indent=2))
        else:
            print("\n[NOTE] Set GEMINI_API_KEY environment variable to test live Gemini execution.")
