"""
Step 5: Test Verification Matrix Runner (Matching M0-M5 Evaluation Logic)
Executes test cases against Gemini AI Auditor and verifies risk ratings & actions.
"""

import os
import json
import sys
from google import genai
from google.genai import types

TEST_SUITE_PATH = os.path.join(os.path.dirname(__file__), "test_suite.json")
SYSTEM_INSTRUCTION_PATH = os.path.join(os.path.dirname(__file__), "system_instruction.txt")

def load_system_instruction() -> str:
    with open(SYSTEM_INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        return f.read()

def run_test_case(client: genai.Client, system_instruction: str, test_case: dict) -> dict:
    payload = test_case["input_payload"]
    prompt = f"Analyze this supplier payload and produce the JSON audit assessment:\n{json.dumps(payload, indent=2)}"
    
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

def main():
    with open(TEST_SUITE_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    system_instruction = load_system_instruction()
    api_key = os.environ.get("GEMINI_API_KEY")

    print("==========================================================================")
    print("      STEP 5: TEST VERIFICATION MATRIX (M0-M5 EVALUATION LOGIC)          ")
    print("==========================================================================")

    if not api_key:
        print("\n[NOTE] GEMINI_API_KEY environment variable is not set.")
        print("Displaying Test Matrix Definitions & Expected Triggered Actions:\n")
        for tc in test_cases:
            print(f"Test Case {tc['test_case_id']}: {tc['test_name']}")
            print(f"  Inputs          : {tc['description']}")
            print(f"  Expected Rating : {tc['expected_output']['overall_risk_rating']}")
            print(f"  Expected Action : {tc['expected_output']['recommended_action']}")
            print(f"  Triggered Action: {tc['expected_triggered_action']}")
            print("-" * 74)
        return

    client = genai.Client()
    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        print(f"\nRunning Test Case {tc['test_case_id']}: {tc['test_name']}...")
        result = run_test_case(client, system_instruction, tc)
        
        rating_match = (result.get("overall_risk_rating") == tc["expected_output"]["overall_risk_rating"])
        action_match = (result.get("recommended_action") == tc["expected_output"]["recommended_action"])

        print(f"  - Vendor ID          : {result.get('vendor_id')}")
        print(f"  - Returned Rating    : {result.get('overall_risk_rating')} (Expected: {tc['expected_output']['overall_risk_rating']})")
        print(f"  - Returned Action    : {result.get('recommended_action')} (Expected: {tc['expected_output']['recommended_action']})")
        print(f"  - SOX Compliance Flag: {result.get('sox_compliance_flag')}")
        print(f"  - Agent Justification: {result.get('justification')}")

        if rating_match and action_match:
            print(f"  ==> RESULT: [PASSED] Matches M0-M5 Evaluation Logic")
            passed += 1
        else:
            print(f"  ==> RESULT: [MISMATCH] Review Rule Thresholds")

    print("\n==========================================================================")
    print(f"  TEST VERIFICATION SUMMARY: {passed}/{total} Test Cases Passed")
    print("==========================================================================")

if __name__ == "__main__":
    main()
