-- ==============================================================================
-- ORACLE DATABASE DDL SCRIPT
-- Object Name: V_SUPPLIER_RISK_360
-- Description: Optimized 360-degree Supplier Risk View for Oracle Fusion / EBS
-- Target DB  : Oracle Autonomous Database (ADW/ATP) / E-Business Suite / Fusion ERP
-- 
-- Key Enhancements over standard flat joins:
--   1. Fixes Cartesian product multiplication (aggregates PO, Invoice, Delivery 
--      data in CTEs before joining to vendor master).
--   2. Prevents ORA-01722 errors on PO numbers (ph.segment1).
--   3. Maps Flexfield/Extended attributes (attribute1, attribute2, attribute3) 
--      safely with TO_NUMBER exception handling.
-- ==============================================================================

CREATE OR REPLACE VIEW V_SUPPLIER_RISK_360 AS
WITH 
--------------------------------------------------------------------------------
-- CTE 1: Supplier Base & Financial Attributes
--------------------------------------------------------------------------------
supplier_base AS (
    SELECT 
        v.vendor_id,
        v.vendor_name,
        v.segment1                                              AS vendor_number,
        COALESCE(v.attribute1, 'NR')                            AS credit_rating,
        -- Safe numeric conversion for flexfield attributes
        CASE 
            WHEN REGEXP_LIKE(v.attribute2, '^[0-9]+(\.[0-9]+)?$') 
            THEN TO_NUMBER(v.attribute2) 
            ELSE 0.00 
        END                                                     AS quick_ratio,
        CASE 
            WHEN REGEXP_LIKE(v.attribute3, '^[0-9]+(\.[0-9]+)?$') 
            THEN TO_NUMBER(v.attribute3) 
            ELSE 0.00 
        END                                                     AS debt_to_equity,
        CASE 
            WHEN v.vendor_type_lookup_code = 'CRITICAL_SINGLE_SOURCE' THEN 1 
            ELSE 0 
        END                                                     AS static_single_source_flag
    FROM po_vendors v
),

--------------------------------------------------------------------------------
-- CTE 2: Purchase Order Aggregations (Pre-aggregated to prevent Cartesian product)
--------------------------------------------------------------------------------
po_metrics AS (
    SELECT 
        ph.vendor_id,
        COUNT(DISTINCT ph.po_header_id)                         AS active_po_count,
        SUM(
            NVL(
                (SELECT SUM(NVL(l.quantity, 0) * NVL(l.unit_price, 0)) 
                 FROM po_lines_all l 
                 WHERE l.po_header_id = ph.po_header_id), 0
            )
        )                                                       AS total_po_value
    FROM po_headers_all ph
    WHERE ph.authorization_status = 'APPROVED'
      AND NVL(ph.cancel_flag, 'N') = 'N'
      AND ph.creation_date >= TRUNC(SYSDATE) - 180
    GROUP BY ph.vendor_id
),

--------------------------------------------------------------------------------
-- CTE 3: AP Invoice Payment Delay Aggregations
--------------------------------------------------------------------------------
payment_metrics AS (
    SELECT 
        inv.vendor_id,
        ROUND(
            AVG(
                NVL(inv.payment_due_date, SYSDATE) - NVL(inv.terms_date, inv.invoice_date)
            ), 1
        )                                                       AS avg_payment_delay_days
    FROM ap_invoices_all inv
    WHERE inv.creation_date >= TRUNC(SYSDATE) - 180
      AND NVL(inv.cancelled_date, SYSDATE + 1) > SYSDATE
    GROUP BY inv.vendor_id
),

--------------------------------------------------------------------------------
-- CTE 4: On-Time Delivery Performance Aggregations
--------------------------------------------------------------------------------
delivery_metrics AS (
    SELECT 
        ph.vendor_id,
        COUNT(pll.line_location_id)                             AS total_shipment_lines,
        COUNT(
            CASE 
                WHEN pll.promised_date IS NOT NULL 
                 AND NVL(pll.date_received, pll.last_accept_date) <= pll.promised_date 
                THEN 1 
            END
        )                                                       AS on_time_shipment_lines,
        ROUND(
            (COUNT(
                CASE 
                    WHEN pll.promised_date IS NOT NULL 
                     AND NVL(pll.date_received, pll.last_accept_date) <= pll.promised_date 
                    THEN 1 
                END
            ) * 100.0) / NULLIF(COUNT(pll.line_location_id), 0),
            2
        )                                                       AS on_time_delivery_rate
    FROM po_headers_all ph
    JOIN po_line_locations_all pll ON ph.po_header_id = pll.po_header_id
    WHERE ph.creation_date >= TRUNC(SYSDATE) - 180
      AND NVL(ph.cancel_flag, 'N') = 'N'
    GROUP BY ph.vendor_id
),

--------------------------------------------------------------------------------
-- CTE 5: Dynamic Item Category Single Source Analysis
--------------------------------------------------------------------------------
dynamic_single_source AS (
    SELECT 
        ph.vendor_id,
        MAX(
            CASE 
                WHEN cat_cnt.vendor_count = 1 THEN 1 
                ELSE 0 
            END
        ) AS dynamic_single_source_flag
    FROM po_headers_all ph
    JOIN po_lines_all pl ON ph.po_header_id = pl.po_header_id
    JOIN (
        SELECT 
            sub_l.category_id,
            COUNT(DISTINCT sub_h.vendor_id) AS vendor_count
        FROM po_headers_all sub_h
        JOIN po_lines_all sub_l ON sub_h.po_header_id = sub_l.po_header_id
        WHERE sub_h.creation_date >= TRUNC(SYSDATE) - 180
          AND sub_l.category_id IS NOT NULL
        GROUP BY sub_l.category_id
    ) cat_cnt ON pl.category_id = cat_cnt.category_id
    WHERE ph.creation_date >= TRUNC(SYSDATE) - 180
    GROUP BY ph.vendor_id
)

--------------------------------------------------------------------------------
-- Main Projection
--------------------------------------------------------------------------------
SELECT 
    sb.vendor_id,
    sb.vendor_name,
    sb.credit_rating,
    sb.quick_ratio,
    sb.debt_to_equity,
    
    -- Procurement & Payment Metrics
    NVL(pm.active_po_count, 0)                                  AS active_po_count,
    NVL(pm.total_po_value, 0.00)                                AS total_po_value,
    NVL(pay.avg_payment_delay_days, 0.0)                        AS avg_payment_delay_days,
    NVL(dm.on_time_delivery_rate, 0.00)                         AS on_time_delivery_rate,
    
    -- Single Source Flag (Prefers dynamic category analysis; falls back to static vendor type)
    CASE 
        WHEN dss.dynamic_single_source_flag IS NOT NULL THEN dss.dynamic_single_source_flag
        ELSE sb.static_single_source_flag
    END                                                         AS single_source_flag
FROM supplier_base sb
LEFT JOIN po_metrics pm           ON sb.vendor_id = pm.vendor_id
LEFT JOIN payment_metrics pay     ON sb.vendor_id = pay.vendor_id
LEFT JOIN delivery_metrics dm     ON sb.vendor_id = dm.vendor_id
LEFT JOIN dynamic_single_source dss ON sb.vendor_id = dss.vendor_id;
