-- ==============================================================================
-- ORACLE APEX / PL/SQL STEP 5 TEST VERIFICATION SCRIPT
-- Script Name: apex_verification_test.sql
-- Description: Executes Test Cases 1-3 against PKG_SUPPLIER_RISK_GOVERNANCE
-- ==============================================================================

SET SERVEROUTPUT ON;

DECLARE
    v_tc1_payload CLOB := '{
        "vendor_id": 100101,
        "overall_risk_rating": "LOW",
        "recommended_action": "APPROVE",
        "financial_risk_score": 15,
        "supply_chain_resilience_score": 95,
        "justification": "Supplier displays strong liquidity (Quick Ratio 1.8) and 96% on-time delivery.",
        "sox_compliance_flag": true
    }';

    v_tc2_payload CLOB := '{
        "vendor_id": 100102,
        "overall_risk_rating": "HIGH",
        "recommended_action": "HOLD_PO_PAYOUTS",
        "financial_risk_score": 85,
        "supply_chain_resilience_score": 60,
        "justification": "High liquidity risk (Quick Ratio 0.7 < 1.0, Debt/Equity 3.5 > 2.5) with $500k active POs.",
        "sox_compliance_flag": false
    }';

    v_tc3_payload CLOB := '{
        "vendor_id": 100103,
        "overall_risk_rating": "CRITICAL",
        "recommended_action": "REROUTE_SUPPLIER_ALLOCATION",
        "financial_risk_score": 70,
        "supply_chain_resilience_score": 30,
        "justification": "Critical supply chain bottleneck: Single source supplier with delivery rate 68% (<80%).",
        "sox_compliance_flag": false
    }';

BEGIN
    DBMS_OUTPUT.PUT_LINE('=== RUNNING STEP 5 TEST VERIFICATION MATRIX ===');

    -- Test Case 1: Healthy Vendor
    DBMS_OUTPUT.PUT_LINE('Executing Test Case 1: Healthy Vendor...');
    pkg_supplier_risk_governance.execute_governance_action(
        p_vendor_id       => 100101,
        p_risk_rating     => 'LOW',
        p_action          => 'APPROVE',
        p_financial_score => 15,
        p_scm_score       => 95,
        p_sox_flag        => 'TRUE',
        p_justification   => 'Supplier displays strong liquidity (Quick Ratio 1.8) and 96% on-time delivery.'
    );

    -- Test Case 2: Liquidity Crisis
    DBMS_OUTPUT.PUT_LINE('Executing Test Case 2: Liquidity Crisis...');
    pkg_supplier_risk_governance.execute_governance_action(
        p_vendor_id       => 100102,
        p_risk_rating     => 'HIGH',
        p_action          => 'HOLD_PO_PAYOUTS',
        p_financial_score => 85,
        p_scm_score       => 60,
        p_sox_flag        => 'FALSE',
        p_justification   => 'High liquidity risk (Quick Ratio 0.7 < 1.0, Debt/Equity 3.5 > 2.5) with $500k active POs.'
    );

    -- Test Case 3: Supply Bottleneck
    DBMS_OUTPUT.PUT_LINE('Executing Test Case 3: Supply Bottleneck...');
    pkg_supplier_risk_governance.execute_governance_action(
        p_vendor_id       => 100103,
        p_risk_rating     => 'CRITICAL',
        p_action          => 'REROUTE_SUPPLIER_ALLOCATION',
        p_financial_score => 70,
        p_scm_score       => 30,
        p_sox_flag        => 'FALSE',
        p_justification   => 'Critical supply chain bottleneck: Single source supplier with delivery rate 68% (<80%).'
    );

    DBMS_OUTPUT.PUT_LINE('=== TEST MATRIX EXECUTION COMPLETE. CHECKING AUDIT LOGS ===');
END;
/

-- Query Verification Results from SOX Audit Log
SELECT log_id, vendor_id, risk_rating, action_recommended, 
       financial_score, scm_resilience_score, sox_compliance_flag, creation_date
FROM ai_financial_audit_log
WHERE vendor_id IN (100101, 100102, 100103)
ORDER BY log_id ASC;
