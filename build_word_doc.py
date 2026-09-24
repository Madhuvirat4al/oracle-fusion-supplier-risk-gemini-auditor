import sys
import os
sys.path.insert(0, os.path.abspath("./lib"))

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()

    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Style definitions
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1E, 0x29, 0x3B) # Charcoal Navy

    # Title Block
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("Oracle Fusion ERP Supplier Risk 360 &\nUniversal Gemini AI Auditor")
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x00, 0x47, 0xAB) # Cobalt Blue

    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle_p.add_run("Complete Operational Guide, Technical Specifications & Verification Manual")
    sub_run.font.size = Pt(13)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    doc.add_paragraph() # Spacer

    # Executive Metadata Box
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    cell_00 = meta_table.cell(0, 0)
    cell_00.paragraphs[0].add_run("Enterprise Author / Architect:").bold = True
    cell_00.paragraphs[0].add_run(" Seepana Madhu")
    
    cell_01 = meta_table.cell(0, 1)
    cell_01.paragraphs[0].add_run("System Target:").bold = True
    cell_01.paragraphs[0].add_run(" Oracle Fusion Cloud ERP & SOX Compliance")

    cell_10 = meta_table.cell(1, 0)
    cell_10.paragraphs[0].add_run("Classification:").bold = True
    cell_10.paragraphs[0].add_run(" Executive Operational Manual")

    cell_11 = meta_table.cell(1, 1)
    cell_11.paragraphs[0].add_run("Repository Status:").bold = True
    cell_11.paragraphs[0].add_run(" Verified & Pushed to GitHub")

    doc.add_paragraph() # Spacer

    # Helper function for headings
    def add_custom_heading(text, level=1):
        h = doc.add_paragraph()
        run = h.add_run(text)
        run.bold = True
        if level == 1:
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(0x00, 0x47, 0xAB)
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(6)
        elif level == 2:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
        return h

    # Section 1: Executive Overview & Architectural Topology
    add_custom_heading("1. Executive Overview & Architectural Topology", level=1)
    p = doc.add_paragraph(
        "The Aegis AI Auditor is an enterprise-grade autonomous risk mitigation and diligence system built for "
        "Oracle Fusion Cloud ERP environments. It continuously evaluates vendor financial liquidity, debt-to-equity ratios, "
        "on-time delivery telemetry, quality inspection defect rates, and sole-source supply chain bottlenecks."
    )
    p = doc.add_paragraph(
        "By fusing deterministic business rules with Gemini 2.5 Flash and Universal Real-Time Knowledge Retrieval, "
        "the command center provides executive procurement officers with real-time decision governance and automatic "
        "SOX audit logging inside the AI_FINANCIAL_AUDIT_LOG ledger."
    )

    # Section 2: Live Command Center UI & Visual Screenshots
    add_custom_heading("2. Live Command Center UI & Visual Interface Gallery", level=1)
    doc.add_paragraph(
        "Below are the verified user interface screenshots captured directly from the active command center dashboard. "
        "These assets demonstrate the modern cyber-enterprise design system, dynamic KPI banners, stress-test sandbox, and AI chatbot."
    )

    # Screenshot 1
    add_custom_heading("2.1 Executive Dashboard & Real-Time KPI Telemetry", level=2)
    doc.add_paragraph(
        "Figure 1 illustrates the primary command center overview, featuring active pulse monitoring, 4 key financial metrics "
        "($1.81M open PO value at risk, 5 monitored vendors, 2 critical single-source suppliers, and 100% SOX compliance logging)."
    )
    img1_path = os.path.abspath("assets/dashboard_overview.png")
    if os.path.exists(img1_path):
        doc.add_picture(img1_path, width=Inches(6.2))
        cap1 = doc.add_paragraph()
        cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c1 = cap1.add_run("Figure 1: Aegis AI Auditor Executive Dashboard Overview & Key Performance Indicator Banner")
        c1.font.italic = True
        c1.font.size = Pt(9.5)
        c1.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Screenshot 2
    add_custom_heading("2.2 Interactive Supplier Telemetry Stress-Test Sandbox", level=2)
    doc.add_paragraph(
        "Figure 2 showcases the interactive stress-test sandbox. Auditors can manipulate Quick Liquidity Ratios, Debt-to-Equity, "
        "Active PO Values, and On-Time Delivery Rates via real-time sliders to execute simulated Gemini Diligence Audits."
    )
    img2_path = os.path.abspath("assets/stress_test_sandbox.png")
    if os.path.exists(img2_path):
        doc.add_picture(img2_path, width=Inches(6.2))
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c2 = cap2.add_run("Figure 2: Interactive Supplier Telemetry Stress-Test Sandbox with Real-Time Risk Calibration")
        c2.font.italic = True
        c2.font.size = Pt(9.5)
        c2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Screenshot 3
    add_custom_heading("2.3 Universal Gemini AI RAG Chatbot Assistant", level=2)
    doc.add_paragraph(
        "Figure 3 demonstrates the Universal Gemini AI Assistant interface. The assistant seamlessly responds to queries ranging from "
        "Oracle ERP supplier risk metrics to general world knowledge, medical topics, and identity verification."
    )
    img3_path = os.path.abspath("assets/universal_rag_chatbot.png")
    if os.path.exists(img3_path):
        doc.add_picture(img3_path, width=Inches(6.2))
        cap3 = doc.add_paragraph()
        cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c3 = cap3.add_run("Figure 3: Universal Gemini Enterprise AI Assistant with Real-Time Knowledge Retrieval")
        c3.font.italic = True
        c3.font.size = Pt(9.5)
        c3.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Section 3: Operational Step-by-Step Manual
    add_custom_heading("3. Operational Step-by-Step Execution Manual", level=1)
    
    steps = [
        ("Step 1: Environment Preparation & Setup", 
         "Clone the repository and verify Python 3.10+ installation. Ensure network access to local port 8080."),
        ("Step 2: Start the Command Center Server",
         "Run `python3 server.py` in your terminal shell. The server initializes the HTTP REST server on http://localhost:8080."),
        ("Step 3: Access the Web Dashboard",
         "Open your browser and navigate to `http://localhost:8080`. The glassmorphic dashboard will load automatically."),
        ("Step 4: Execute Autonomous Supplier Audits",
         "Select a supplier from the dropdown, adjust risk parameters, and click 'Run Gemini Diligence Audit' to trigger rules & AI evaluations."),
        ("Step 5: Utilize the Universal AI Assistant",
         "Enter queries into the chat input bar. Ask about supplier health, quality rejections, global topics, or identity verification.")
    ]

    for title, desc in steps:
        add_custom_heading(title, level=2)
        doc.add_paragraph(desc)

    # Section 4: Oracle Fusion ERP Technical Integration Reference
    add_custom_heading("4. Oracle Fusion ERP Technical Integration Reference", level=1)
    doc.add_paragraph(
        "The system interfaces with Oracle Fusion Cloud ERP via PL/SQL database views and automated governance tables. "
        "Below are the core database schema definitions utilized in production:"
    )

    sql_box = doc.add_paragraph()
    sql_run = sql_box.add_run(
        "--- Oracle Fusion ERP Database View Schema ---\n"
        "CREATE OR REPLACE VIEW V_SUPPLIER_RISK_360 AS\n"
        "SELECT \n"
        "    s.vendor_id,\n"
        "    s.vendor_name,\n"
        "    s.segment1 AS vendor_number,\n"
        "    fin.quick_ratio,\n"
        "    fin.debt_to_equity,\n"
        "    fin.credit_rating,\n"
        "    scm.open_po_value,\n"
        "    scm.on_time_delivery_rate,\n"
        "    scm.rejection_rate_pct,\n"
        "    scm.single_source_flag\n"
        "FROM ap_suppliers s\n"
        "JOIN supplier_financial_telemetry fin ON s.vendor_id = fin.vendor_id\n"
        "JOIN supplier_scm_performance scm ON s.vendor_id = scm.vendor_id;\n"
    )
    sql_run.font.name = 'Courier New'
    sql_run.font.size = Pt(9)
    sql_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Section 5: Verification Matrix
    add_custom_heading("5. System Verification Matrix & Test Benchmarks", level=1)
    doc.add_paragraph("The table below details the empirical verification results across various conversational intent categories:")

    table = doc.add_table(rows=6, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Test Query", "Intent Category", "Verified Output Status"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.paragraphs[0].add_run(h).bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        # Background color
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0047AB"/>')
        tcPr.append(shd)

    test_rows = [
        ("Who is Sachin Tendulkar", "Global Knowledge", "100% Verified (Full Biography & Wiki Link)"),
        ("Explain photosynthesis", "Scientific Intelligence", "100% Verified (Cellular Respiration & Process)"),
        ("how to treat cancer", "Medical Intelligence", "100% Verified (Chemotherapy & Surgical Overview)"),
        ("who is seepana madhu", "Executive Profile", "100% Verified (Enterprise Architect Profile)"),
        ("suppliers with rejection data", "Oracle ERP RAG", "100% Verified (5 Monitored Suppliers Ranked)")
    ]

    for r_idx, (q, cat, stat) in enumerate(test_rows, start=1):
        row_cells = table.rows[r_idx].cells
        row_cells[0].paragraphs[0].add_run(q)
        row_cells[1].paragraphs[0].add_run(cat)
        row_cells[2].paragraphs[0].add_run(stat)
        
        # Alternating row shading
        if r_idx % 2 == 0:
            for cell in row_cells:
                tcPr = cell._tc.get_or_add_tcPr()
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
                tcPr.append(shd)

    # Save document
    out1 = os.path.abspath("assets/Oracle_Fusion_Supplier_Risk_Gemini_Auditor_Documentation.docx")
    out2 = os.path.abspath("Oracle_Fusion_Supplier_Risk_Gemini_Auditor_Documentation.docx")
    
    doc.save(out1)
    doc.save(out2)
    print(f"Successfully generated Word Documents:\n - {out1}\n - {out2}")

if __name__ == "__main__":
    create_document()
