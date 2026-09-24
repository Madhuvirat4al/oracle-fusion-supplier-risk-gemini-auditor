"""
AEGIS AI AUDITOR - Oracle Fusion Cloud ERP Risk Command Center
Persistent Test Server (Listens on 0.0.0.0:8080 and 127.0.0.1:8080)
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
from datetime import datetime

PORT = 8080

AUDIT_LOGS = []
LOG_ID_COUNTER = 10001

MOCK_SUPPLIERS = [
    {
        "vendor_id": 100101,
        "vendor_name": "Apex Semiconductor Systems",
        "vendor_number": "SUP-100101",
        "category": "Critical Microcontrollers",
        "financials": {
            "quick_ratio": 1.85,
            "debt_to_equity": 1.10,
            "credit_rating": "AA-",
            "cash_reserves_m": 42.5
        },
        "scm_performance": {
            "total_po_value": 75000.00,
            "avg_payment_delay_days": 4.0,
            "on_time_delivery_rate": 96.5,
            "single_source_flag": 0
        },
        "external_risk_signals": {
            "port_congestion_index": "LOW",
            "recent_credit_downgrade": False,
            "geopolitical_risk_score": 12
        }
    },
    {
        "vendor_id": 100102,
        "vendor_name": "Vanguard Logistics & Components",
        "vendor_number": "SUP-100102",
        "category": "Intermodal Freight & Sub-Assemblies",
        "financials": {
            "quick_ratio": 0.68,
            "debt_to_equity": 3.65,
            "credit_rating": "B-",
            "cash_reserves_m": 4.2
        },
        "scm_performance": {
            "total_po_value": 540000.00,
            "avg_payment_delay_days": 42.0,
            "on_time_delivery_rate": 86.0,
            "single_source_flag": 0
        },
        "external_risk_signals": {
            "port_congestion_index": "HIGH",
            "recent_credit_downgrade": True,
            "geopolitical_risk_score": 68
        }
    },
    {
        "vendor_id": 100103,
        "vendor_name": "Titan Precision Forgings",
        "vendor_number": "SUP-100103",
        "category": "Aerospace Grade Titanium Alloys",
        "financials": {
            "quick_ratio": 0.92,
            "debt_to_equity": 2.25,
            "credit_rating": "BB",
            "cash_reserves_m": 11.0
        },
        "scm_performance": {
            "total_po_value": 380000.00,
            "avg_payment_delay_days": 29.0,
            "on_time_delivery_rate": 64.5,
            "single_source_flag": 1
        },
        "external_risk_signals": {
            "port_congestion_index": "CRITICAL",
            "recent_credit_downgrade": True,
            "geopolitical_risk_score": 84
        }
    },
    {
        "vendor_id": 100104,
        "vendor_name": "Global Polychem Industries",
        "vendor_number": "SUP-100104",
        "category": "Industrial Polymers",
        "financials": {
            "quick_ratio": 1.45,
            "debt_to_equity": 1.70,
            "credit_rating": "A-",
            "cash_reserves_m": 28.0
        },
        "scm_performance": {
            "total_po_value": 195000.00,
            "avg_payment_delay_days": 12.0,
            "on_time_delivery_rate": 91.0,
            "single_source_flag": 0
        },
        "external_risk_signals": {
            "port_congestion_index": "MEDIUM",
            "recent_credit_downgrade": False,
            "geopolitical_risk_score": 25
        }
    },
    {
        "vendor_id": 100105,
        "vendor_name": "Kuroda Optical Sensors Ltd",
        "vendor_number": "SUP-100105",
        "category": "LiDAR Sensor Assemblies",
        "financials": {
            "quick_ratio": 0.75,
            "debt_to_equity": 2.85,
            "credit_rating": "CCC+",
            "cash_reserves_m": 3.1
        },
        "scm_performance": {
            "total_po_value": 620000.00,
            "avg_payment_delay_days": 54.0,
            "on_time_delivery_rate": 71.0,
            "single_source_flag": 1
        },
        "external_risk_signals": {
            "port_congestion_index": "HIGH",
            "recent_credit_downgrade": True,
            "geopolitical_risk_score": 91
        }
    }
]

def evaluate_supplier_rules(supplier_ctx: dict) -> dict:
    fin = supplier_ctx.get("financials", {})
    scm = supplier_ctx.get("scm_performance", {})
    ext = supplier_ctx.get("external_risk_signals", {})
    
    quick_ratio = fin.get("quick_ratio", 1.0)
    debt_equity = fin.get("debt_to_equity", 0.0)
    rating = str(fin.get("credit_rating", "BBB"))
    
    delivery_rate = scm.get("on_time_delivery_rate", 100.0)
    single_source = scm.get("single_source_flag", 0)
    po_value = scm.get("total_po_value", 0.0)
    payment_delay = scm.get("avg_payment_delay_days", 0.0)
    downgrade = ext.get("recent_credit_downgrade", False)

    below_bbb = rating in ["BB+", "BB", "B-", "CCC+", "CCC", "CC", "C", "D", "NR"]
    fin_risk_high = (quick_ratio < 1.0 or debt_equity > 2.5 or below_bbb)
    scm_risk_critical = (delivery_rate < 80.0 and single_source == 1)

    fin_score = min(100, max(10, int((1.0 - min(quick_ratio, 1.5)/1.5)*50 + (debt_equity/4.0)*50)))
    scm_score = min(100, max(10, int(delivery_rate * 0.7 + (0 if single_source else 30))))

    if scm_risk_critical or (fin_risk_high and single_source == 1 and po_value > 250000):
        overall_rating = "CRITICAL"
        action = "REROUTE_SUPPLIER_ALLOCATION"
        sox_flag = False
        justification = (
            f"• CRITICAL SUPPLY CHAIN BOTTLE NECK DETECTED:\n"
            f"  - Sole-Source Supplier Flag = {single_source} for critical category.\n"
            f"  - On-Time Delivery Performance is fragile at {delivery_rate}% (< 80% threshold).\n"
            f"  - Credit Grade: {rating} (Recent Downgrade: {'YES' if downgrade else 'NO'}).\n"
            f"• AUTOMATED GOVERNANCE DECISION:\n"
            f"  - Triggering Oracle BPM Workflow Task 'SUPPLIER_RISK_ESCALATION'.\n"
            f"  - Re-allocating 40% PO volume to pre-approved secondary tier vendor."
        )
    elif fin_risk_high and po_value > 100000:
        overall_rating = "HIGH"
        action = "HOLD_PO_PAYOUTS"
        sox_flag = False
        justification = (
            f"• FINANCIAL LIQUIDITY RISK EXCEEDED THRESHOLDS:\n"
            f"  - Quick Ratio {quick_ratio:.2f} (< 1.0) | Debt-to-Equity {debt_equity:.2f} (> 2.5).\n"
            f"  - Credit Rating grade '{rating}' below investment grade BBB-.\n"
            f"  - Active open PO value ${po_value:,.2f} exceeds exposure limit ($100,000).\n"
            f"• AUTOMATED GOVERNANCE DECISION:\n"
            f"  - Updating Oracle Fusion PO status to ON_HOLD (PO_HEADERS_ALL).\n"
            f"  - Suspending automated AP check disbursements pending treasury review."
        )
    elif fin_risk_high or payment_delay > 30:
        overall_rating = "MEDIUM"
        action = "HUMAN_REVIEW_REQUIRED"
        sox_flag = True
        justification = (
            f"• MODERATE RISK ELEVATION:\n"
            f"  - Average Payment Delay {payment_delay:.1f} days indicates minor cash flow friction.\n"
            f"  - Financial Liquidity indicators moderate (Quick Ratio {quick_ratio:.2f}).\n"
            f"• AUTOMATED GOVERNANCE DECISION:\n"
            f"  - Routing audit report to SCM Compliance Officer for manual verification."
        )
    else:
        overall_rating = "LOW"
        action = "APPROVE"
        sox_flag = True
        justification = (
            f"• SUPPLIER IN EXCELLENT FINANCIAL & OPERATIONAL STANDING:\n"
            f"  - Quick Ratio {quick_ratio:.2f} & Debt-to-Equity {debt_equity:.2f} well within safe boundaries.\n"
            f"  - High On-Time Delivery Rate: {delivery_rate:.1f}%.\n"
            f"• AUTOMATED GOVERNANCE DECISION:\n"
            f"  - Full clearance granted for instant PO processing and AP invoice payout."
        )

    return {
        "vendor_id": supplier_ctx.get("vendor_id"),
        "overall_risk_rating": overall_rating,
        "recommended_action": action,
        "financial_risk_score": fin_score,
        "supply_chain_resilience_score": scm_score,
        "justification": justification,
        "sox_compliance_flag": sox_flag
    }

class AegisAuditorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.render_dashboard().encode("utf-8"))
        elif parsed.path == "/api/suppliers":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(MOCK_SUPPLIERS).encode("utf-8"))
        elif parsed.path == "/api/audit-logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(AUDIT_LOGS).encode("utf-8"))
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/audit":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode("utf-8"))
                supplier_ctx = payload.get("supplier_context", payload)
                
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    try:
                        from google import genai
                        from google.genai import types
                        client = genai.Client()
                        sys_instruction_path = os.path.join(os.path.dirname(__file__), "system_instruction.txt")
                        with open(sys_instruction_path, "r") as f:
                            sys_instruction = f.read()
                            
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"Analyze supplier payload:\n{json.dumps(payload, indent=2)}",
                            config=types.GenerateContentConfig(
                                system_instruction=sys_instruction,
                                response_mime_type="application/json",
                                temperature=0.1
                            )
                        )
                        result = json.loads(response.text)
                    except Exception as ge:
                        print(f"Gemini API fallback: {ge}")
                        result = evaluate_supplier_rules(supplier_ctx)
                else:
                    result = evaluate_supplier_rules(supplier_ctx)

                global LOG_ID_COUNTER
                log_entry = {
                    "log_id": LOG_ID_COUNTER,
                    "vendor_id": result.get("vendor_id"),
                    "vendor_name": supplier_ctx.get("vendor_name", "Supplier #" + str(result.get("vendor_id"))),
                    "risk_rating": result.get("overall_risk_rating"),
                    "action_recommended": result.get("recommended_action"),
                    "financial_score": result.get("financial_risk_score"),
                    "scm_resilience_score": result.get("supply_chain_resilience_score"),
                    "sox_compliance_flag": result.get("sox_compliance_flag"),
                    "justification": result.get("justification"),
                    "created_by": "APEX_SOX_AUDITOR",
                    "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                LOG_ID_COUNTER += 1
                AUDIT_LOGS.insert(0, log_entry)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"audit_result": result, "log_entry": log_entry}).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def render_dashboard(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS AI - Oracle Fusion ERP Supplier Risk Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #080d1a;
            --panel-bg: rgba(18, 26, 47, 0.75);
            --panel-border: rgba(56, 189, 248, 0.15);
            --panel-border-glow: rgba(56, 189, 248, 0.4);
            --accent-cyan: #00f2fe;
            --accent-blue: #38bdf8;
            --accent-indigo: #6366f1;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-crimson: #ff0055;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --font-main: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--font-main);
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(99, 102, 241, 0.1) 0%, transparent 45%);
            color: var(--text-main);
            padding: 2rem;
            min-height: 100vh;
        }

        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(16px);
            border: 1px solid var(--panel-border);
            padding: 1rem 1.75rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.2rem;
            color: #080d1a;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.5);
        }

        .brand-title h1 {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-title p {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .live-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--accent-emerald);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-emerald);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .metrics-banner {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--panel-border);
            padding: 1.25rem;
            border-radius: 14px;
            transition: all 0.3s ease;
        }

        .kpi-card:hover {
            border-color: var(--panel-border-glow);
            transform: translateY(-2px);
        }

        .kpi-title {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .kpi-value {
            font-family: var(--font-mono);
            font-size: 1.6rem;
            font-weight: 700;
            margin-top: 0.4rem;
            color: #ffffff;
        }

        .kpi-sub {
            font-size: 0.75rem;
            color: var(--accent-cyan);
            margin-top: 0.25rem;
        }

        .layout-grid {
            display: grid;
            grid-template-columns: 1.1fr 1fr;
            gap: 1.75rem;
        }

        .glass-panel {
            background: var(--panel-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 1.75rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--panel-border);
        }

        .panel-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .scenario-chips {
            display: flex;
            gap: 0.5rem;
        }

        .chip-btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--panel-border);
            color: var(--text-muted);
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .chip-btn:hover, .chip-btn.active {
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.2), rgba(99, 102, 241, 0.2));
            color: var(--accent-cyan);
            border-color: var(--accent-cyan);
        }

        .slider-group {
            margin-bottom: 1rem;
        }

        .slider-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
        }

        .slider-label span:last-child {
            font-family: var(--font-mono);
            color: var(--accent-cyan);
            font-weight: 700;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #1e293b;
            outline: none;
            accent-color: var(--accent-cyan);
        }

        .btn-trigger {
            width: 100%;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
            color: #080d1a;
            font-weight: 800;
            font-size: 1rem;
            padding: 0.9rem;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
            transition: all 0.3s;
        }

        .btn-trigger:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 35px rgba(0, 242, 254, 0.6);
        }

        .risk-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.9rem;
            border-radius: 8px;
            font-weight: 800;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }

        .badge-LOW { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
        .badge-HIGH { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
        .badge-CRITICAL { background: rgba(255, 0, 85, 0.2); color: #ff4d7d; border: 1px solid rgba(255, 0, 85, 0.4); box-shadow: 0 0 15px rgba(255, 0, 85, 0.3); }

        .action-box {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 1.25rem;
            margin-top: 1rem;
        }

        .action-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }

        .action-title {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        .action-value {
            font-family: var(--font-mono);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--accent-cyan);
        }

        .reasoning-terminal {
            background: #040812;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 1rem;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: #a5f3fc;
            line-height: 1.6;
            max-height: 220px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        .table-container {
            margin-top: 2rem;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        th {
            background: rgba(15, 23, 42, 0.9);
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--panel-border);
        }

        td {
            padding: 0.85rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        tr:hover td {
            background: rgba(56, 189, 248, 0.03);
        }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="brand-logo">
            <div class="brand-icon">A</div>
            <div class="brand-title">
                <h1>AEGIS AI COMMAND CENTER</h1>
                <p>Oracle Fusion Cloud ERP &bull; Autonomous Diligence Agent</p>
            </div>
        </div>
        <div class="live-status">
            <div class="pulse-dot"></div>
            <span>PORT 8080 READY</span>
        </div>
    </div>

    <div class="metrics-banner">
        <div class="kpi-card">
            <div class="kpi-title">Active Monitored Vendors</div>
            <div class="kpi-value">5</div>
            <div class="kpi-sub">V_SUPPLIER_RISK_360 View</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total PO Value at Risk</div>
            <div class="kpi-value" style="color: var(--accent-amber);">$1,810,000</div>
            <div class="kpi-sub">Rolling 180-Day Window</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Critical Single Source Vendors</div>
            <div class="kpi-value" style="color: var(--accent-crimson);">2</div>
            <div class="kpi-sub">Sole Category Suppliers</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">SOX Audit Compliance</div>
            <div class="kpi-value" style="color: var(--accent-emerald);">100% Logged</div>
            <div class="kpi-sub">AI_FINANCIAL_AUDIT_LOG</div>
        </div>
    </div>

    <div class="layout-grid">
        <div class="glass-panel">
            <div class="panel-header">
                <div class="panel-title">
                    <span>1. Supplier Telemetry & Stress Test</span>
                </div>
                <div class="scenario-chips">
                    <button class="chip-btn active" onclick="loadPreset(0)">TC1: Safe</button>
                    <button class="chip-btn" onclick="loadPreset(1)">TC2: Liquidity</button>
                    <button class="chip-btn" onclick="loadPreset(2)">TC3: Bottleneck</button>
                </div>
            </div>

            <div style="margin-bottom: 1.25rem;">
                <label style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Select Vendor Record</label>
                <select id="vendorSelect" onchange="onVendorSelect()" style="width:100%; padding:0.75rem; background:#0b1329; border:1px solid var(--panel-border); color:#fff; border-radius:8px; margin-top:0.4rem; font-family:var(--font-main);">
                </select>
            </div>

            <div class="slider-group">
                <div class="slider-label">
                    <span>Quick Liquidity Ratio</span>
                    <span id="lblQuickRatio">1.80</span>
                </div>
                <input type="range" id="rngQuickRatio" min="0.30" max="2.50" step="0.05" value="1.80" oninput="updateSliderLabels()">
            </div>

            <div class="slider-group">
                <div class="slider-label">
                    <span>Debt-to-Equity Ratio</span>
                    <span id="lblDebtEquity">1.10</span>
                </div>
                <input type="range" id="rngDebtEquity" min="0.50" max="5.00" step="0.10" value="1.10" oninput="updateSliderLabels()">
            </div>

            <div class="slider-group">
                <div class="slider-label">
                    <span>Active Open PO Value ($)</span>
                    <span id="lblPoValue">$75,000</span>
                </div>
                <input type="range" id="rngPoValue" min="10000" max="1000000" step="10000" value="75000" oninput="updateSliderLabels()">
            </div>

            <div class="slider-group">
                <div class="slider-label">
                    <span>On-Time Delivery Rate (%)</span>
                    <span id="lblOnTime">96.0%</span>
                </div>
                <input type="range" id="rngOnTime" min="40.0" max="100.0" step="0.5" value="96.0" oninput="updateSliderLabels()">
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem; margin-top:1rem;">
                <div>
                    <label style="font-size:0.75rem; color:var(--text-muted);">SINGLE SOURCE SUPPLIER</label>
                    <select id="selSingleSource" style="width:100%; padding:0.6rem; background:#0b1329; border:1px solid var(--panel-border); color:#fff; border-radius:6px; margin-top:0.3rem;" onchange="updateSliderLabels()">
                        <option value="0">0 - Multi-Sourced Category</option>
                        <option value="1">1 - Sole Vendor for Category</option>
                    </select>
                </div>
                <div>
                    <label style="font-size:0.75rem; color:var(--text-muted);">CREDIT RATING</label>
                    <select id="selCreditRating" style="width:100%; padding:0.6rem; background:#0b1329; border:1px solid var(--panel-border); color:#fff; border-radius:6px; margin-top:0.3rem;" onchange="updateSliderLabels()">
                        <option value="AA-">AA- (Investment Grade)</option>
                        <option value="A-">A- (Investment Grade)</option>
                        <option value="BBB-">BBB- (Minimum Threshold)</option>
                        <option value="BB+">BB+ (Non-Investment Grade)</option>
                        <option value="BB">BB (Speculative)</option>
                        <option value="B-">B- (High Vulnerability)</option>
                        <option value="CCC+">CCC+ (Default Risk)</option>
                    </select>
                </div>
            </div>

            <button class="btn-trigger" onclick="runAutonomousAudit()">⚡ Run Gemini Diligence Audit</button>
        </div>

        <div class="glass-panel">
            <div class="panel-header">
                <div class="panel-title">
                    <span>2. Gemini Agent Audit Assessment</span>
                </div>
                <span id="auditTimestamp" style="font-size: 0.75rem; color: var(--text-muted);">Ready for Analysis</span>
            </div>

            <div id="outputDisplay">
                <div style="text-align:center; padding:3rem 1rem; color:var(--text-muted);">
                    <p style="font-size:1.1rem; margin-bottom:0.5rem;">Awaiting Supplier Audit Trigger</p>
                    <p style="font-size:0.8rem;">Click "Run Gemini Diligence Audit" to execute business rules & SOX governance checks.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="glass-panel" style="margin-top: 2rem;">
        <div class="panel-header">
            <div class="panel-title">
                <span>3. SOX Compliance Decision Ledger (`AI_FINANCIAL_AUDIT_LOG`)</span>
            </div>
            <button class="chip-btn" onclick="fetchAuditLogs()">Refresh Audit Trail</button>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Log ID</th>
                        <th>Vendor Name</th>
                        <th>Risk Classification</th>
                        <th>ERP Action Executed</th>
                        <th>Fin Score</th>
                        <th>SCM Score</th>
                        <th>SOX Status</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody id="auditTableBody">
                    <tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">No audit records generated yet.</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let suppliersList = [];

        async function init() {
            const res = await fetch('/api/suppliers');
            suppliersList = await res.json();
            
            const sel = document.getElementById('vendorSelect');
            sel.innerHTML = suppliersList.map((s, i) => `<option value="${i}">${s.vendor_name} (${s.category})</option>`).join('');
            
            loadPreset(0);
            fetchAuditLogs();
        }

        function loadPreset(idx) {
            document.querySelectorAll('.chip-btn').forEach((b, i) => {
                if (i < 3) b.classList.toggle('active', i === idx);
            });

            document.getElementById('vendorSelect').value = idx;
            const s = suppliersList[idx];
            if (!s) return;

            document.getElementById('rngQuickRatio').value = s.financials.quick_ratio;
            document.getElementById('rngDebtEquity').value = s.financials.debt_to_equity;
            document.getElementById('rngPoValue').value = s.scm_performance.total_po_value;
            document.getElementById('rngOnTime').value = s.scm_performance.on_time_delivery_rate;
            document.getElementById('selSingleSource').value = s.scm_performance.single_source_flag;
            document.getElementById('selCreditRating').value = s.financials.credit_rating;

            updateSliderLabels();
        }

        function onVendorSelect() {
            const idx = document.getElementById('vendorSelect').value;
            loadPreset(parseInt(idx));
        }

        function updateSliderLabels() {
            document.getElementById('lblQuickRatio').innerText = parseFloat(document.getElementById('rngQuickRatio').value).toFixed(2);
            document.getElementById('lblDebtEquity').innerText = parseFloat(document.getElementById('rngDebtEquity').value).toFixed(2);
            document.getElementById('lblPoValue').innerText = '$' + parseInt(document.getElementById('rngPoValue').value).toLocaleString();
            document.getElementById('lblOnTime').innerText = parseFloat(document.getElementById('rngOnTime').value).toFixed(1) + '%';
        }

        async function runAutonomousAudit() {
            const idx = document.getElementById('vendorSelect').value;
            const baseSupplier = suppliersList[idx] || {};

            const payload = {
                supplier_context: {
                    vendor_id: baseSupplier.vendor_id || 100101,
                    vendor_name: baseSupplier.vendor_name || 'Selected Supplier',
                    vendor_number: baseSupplier.vendor_number || 'SUP-100101',
                    category: baseSupplier.category || 'General Procurement',
                    financials: {
                        quick_ratio: parseFloat(document.getElementById('rngQuickRatio').value),
                        debt_to_equity: parseFloat(document.getElementById('rngDebtEquity').value),
                        credit_rating: document.getElementById('selCreditRating').value
                    },
                    scm_performance: {
                        total_po_value: parseFloat(document.getElementById('rngPoValue').value),
                        avg_payment_delay_days: baseSupplier.scm_performance ? baseSupplier.scm_performance.avg_payment_delay_days : 20,
                        on_time_delivery_rate: parseFloat(document.getElementById('rngOnTime').value),
                        single_source_flag: parseInt(document.getElementById('selSingleSource').value)
                    },
                    external_risk_signals: baseSupplier.external_risk_signals || { port_congestion_index: "MEDIUM" }
                }
            };

            document.getElementById('outputDisplay').innerHTML = `
                <div style="padding:2rem; text-align:center;">
                    <div style="color:var(--accent-cyan); font-weight:700; font-size:1.1rem; margin-bottom:0.5rem;">⚡ Gemini Auditor Reasoning in Progress...</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">Enforcing Financial Liquidity & Supply Chain Disruption Business Rules</div>
                </div>
            `;

            try {
                const res = await fetch('/api/audit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                document.getElementById('auditTimestamp').innerText = 'Audited at ' + new Date().toLocaleTimeString();
                renderAuditOutput(data.audit_result);
                fetchAuditLogs();
            } catch (err) {
                document.getElementById('outputDisplay').innerHTML = `<p style="color:var(--accent-crimson);">Audit execution failed: ${err.message}</p>`;
            }
        }

        function renderAuditOutput(res) {
            const rating = res.overall_risk_rating || 'LOW';
            const action = res.recommended_action || 'APPROVE';
            const badgeClass = 'badge-' + rating;

            document.getElementById('outputDisplay').innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
                    <div>
                        <span class="risk-badge ${badgeClass}">${rating} RISK</span>
                    </div>
                    <div style="font-size:0.85rem; color:var(--text-muted);">
                        SOX Compliance: <strong style="color:${res.sox_compliance_flag ? '#34d399' : '#ff4d7d'};">${res.sox_compliance_flag ? 'PASSED ✅' : 'FLAGGED ⚠️'}</strong>
                    </div>
                </div>

                <div class="action-box">
                    <div class="action-header">
                        <span class="action-title">RECOMMENDED ORACLE ERP ACTION</span>
                        <span class="action-value">${action}</span>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.08); padding-top:0.75rem; margin-top:0.5rem;">
                        <div>Financial Risk Index: <strong style="color:var(--accent-cyan);">${res.financial_risk_score}/100</strong></div>
                        <div>SCM Resilience Index: <strong style="color:var(--accent-indigo);">${res.supply_chain_resilience_score}/100</strong></div>
                    </div>
                </div>

                <div style="margin-top:1.25rem;">
                    <label style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:700;">GEMINI AGENT AUDIT JUSTIFICATION</label>
                    <div class="reasoning-terminal" style="margin-top:0.4rem;">${res.justification}</div>
                </div>
            `;
        }

        async function fetchAuditLogs() {
            const res = await fetch('/api/audit-logs');
            const logs = await res.json();
            const tbody = document.getElementById('auditTableBody');

            if (!logs || logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">No audit records generated yet.</td></tr>';
                return;
            }

            tbody.innerHTML = logs.map(l => `
                <tr>
                    <td style="font-family:var(--font-mono); font-weight:700; color:var(--accent-cyan);">#${l.log_id}</td>
                    <td><strong>${l.vendor_name}</strong></td>
                    <td><span class="risk-badge badge-${l.risk_rating}">${l.risk_rating}</span></td>
                    <td><strong style="font-family:var(--font-mono); color:#fff;">${l.action_recommended}</strong></td>
                    <td style="font-family:var(--font-mono);">${l.financial_score}/100</td>
                    <td style="font-family:var(--font-mono);">${l.scm_resilience_score}/100</td>
                    <td>${l.sox_compliance_flag ? '✅ PASS' : '⚠️ FLAGGED'}</td>
                    <td style="font-size:0.75rem; color:var(--text-muted);">${l.creation_date}</td>
                </tr>
            `).join('');
        }

        window.onload = init;
    </script>
</body>
</html>"""

def run_server():
    os.chdir(os.path.dirname(__file__))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), AegisAuditorHandler) as httpd:
        print(f"==========================================================================")
        print(f"  AEGIS AI AUDITOR - ORACLE FUSION ERP RISK COMMAND CENTER                 ")
        print(f"==========================================================================")
        print(f"  Local Listening Endpoint: http://0.0.0.0:{PORT}")
        print(f"  Local Web Dashboard URL  : http://localhost:{PORT}")
        print(f"==========================================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
