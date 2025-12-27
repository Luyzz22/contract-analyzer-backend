# app/pdf_report.py
"""
PDF Report Generator für Vertragsanalysen.
Erstellt professionelle PDF-Reports mit SBS-Branding.
"""

import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# SBS Farben
SBS_BLUE = colors.HexColor("#003856")
SBS_BLUE_DARK = colors.HexColor("#002a42")
SBS_YELLOW = colors.HexColor("#FFB900")
SBS_GREEN = colors.HexColor("#16a34a")
SBS_RED = colors.HexColor("#dc2626")
SBS_ORANGE = colors.HexColor("#ea580c")
SBS_GRAY = colors.HexColor("#6b7280")


def get_risk_color(level: str) -> colors.Color:
    """Gibt die Farbe für ein Risiko-Level zurück."""
    return {
        "critical": SBS_RED,
        "high": SBS_ORANGE,
        "medium": SBS_YELLOW,
        "low": SBS_GREEN,
    }.get(level, SBS_GRAY)


def get_risk_label(level: str) -> str:
    """Gibt das deutsche Label für ein Risiko-Level zurück."""
    return {
        "critical": "KRITISCH",
        "high": "HOCH",
        "medium": "MITTEL",
        "low": "NIEDRIG",
    }.get(level, "UNBEKANNT")


def create_styles() -> Dict[str, ParagraphStyle]:
    """Erstellt die Paragraph-Styles für den Report."""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=24,
            textColor=SBS_BLUE,
            spaceAfter=12,
            fontName="Helvetica-Bold",
        ),
        "Heading1": ParagraphStyle(
            "Heading1",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=SBS_BLUE,
            spaceBefore=20,
            spaceAfter=10,
            fontName="Helvetica-Bold",
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=SBS_BLUE_DARK,
            spaceBefore=12,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "Normal": ParagraphStyle(
            "Normal",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=8,
            textColor=SBS_GRAY,
        ),
        "RiskHigh": ParagraphStyle(
            "RiskHigh",
            parent=styles["Normal"],
            fontSize=10,
            textColor=SBS_RED,
            fontName="Helvetica-Bold",
        ),
        "RiskMedium": ParagraphStyle(
            "RiskMedium",
            parent=styles["Normal"],
            fontSize=10,
            textColor=SBS_ORANGE,
            fontName="Helvetica-Bold",
        ),
        "RiskLow": ParagraphStyle(
            "RiskLow",
            parent=styles["Normal"],
            fontSize=10,
            textColor=SBS_GREEN,
            fontName="Helvetica-Bold",
        ),
        "Footer": ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=SBS_GRAY,
            alignment=TA_CENTER,
        ),
    }
    
    return custom_styles


def generate_contract_pdf(analysis: Dict[str, Any]) -> bytes:
    """
    Generiert ein PDF-Report für eine Vertragsanalyse.
    
    Args:
        analysis: Das Analyse-Ergebnis aus der API
    
    Returns:
        PDF als bytes
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    styles = create_styles()
    story = []
    
    # === HEADER ===
    story.append(Paragraph("SBS Contract Intelligence", styles["Title"]))
    story.append(Paragraph("KI-gestützte Vertragsanalyse", styles["Small"]))
    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=SBS_BLUE))
    story.append(Spacer(1, 5*mm))
    
    # === META-INFORMATIONEN ===
    contract_id = analysis.get("contract_id", "N/A")
    filename = analysis.get("source_filename", analysis.get("filename", "N/A"))
    contract_type = analysis.get("contract_type", "general")
    processing_time = analysis.get("processing_time_seconds", 0)
    
    type_names = {
        "employment": "Arbeitsvertrag",
        "saas": "SaaS-Vertrag",
        "nda": "Geheimhaltungsvereinbarung (NDA)",
        "vendor": "Lieferantenvertrag",
        "service": "Dienstleistungsvertrag",
        "rental": "Mietvertrag",
        "purchase": "Kaufvertrag",
        "general": "Allgemeiner Vertrag",
    }
    type_name = type_names.get(contract_type, contract_type)
    
    meta_data = [
        ["Dokument:", filename],
        ["Vertragstyp:", type_name],
        ["Analyse-ID:", contract_id[:16] + "..." if len(contract_id) > 16 else contract_id],
        ["Analysiert am:", datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")],
        ["Verarbeitungszeit:", f"{processing_time:.2f} Sekunden"],
    ]
    
    meta_table = Table(meta_data, colWidths=[4*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), SBS_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10*mm))
    
    # === RISIKO-ÜBERSICHT ===
    risk_assessment = analysis.get("risk_assessment", {})
    overall_level = risk_assessment.get("overall_risk_level", "medium")
    overall_score = risk_assessment.get("overall_risk_score", 50)
    
    story.append(Paragraph("Risiko-Bewertung", styles["Heading1"]))
    
    risk_color = get_risk_color(overall_level)
    risk_label = get_risk_label(overall_level)
    
    risk_box_data = [[
        f"Gesamtrisiko: {risk_label}",
        f"Score: {overall_score}/100"
    ]]
    
    risk_box = Table(risk_box_data, colWidths=[10*cm, 6*cm])
    risk_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), risk_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 2, risk_color),
    ]))
    story.append(risk_box)
    story.append(Spacer(1, 5*mm))
    
    # === ZUSAMMENFASSUNG ===
    summary = risk_assessment.get("executive_summary", "Keine Zusammenfassung verfügbar.")
    story.append(Paragraph("Zusammenfassung", styles["Heading2"]))
    story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 5*mm))
    
    # === EXTRAHIERTE DATEN ===
    extracted_data = analysis.get("extracted_data", {})
    if extracted_data:
        story.append(Paragraph("Extrahierte Vertragsdaten", styles["Heading1"]))
        
        field_labels = {
            # Arbeitsvertrag
            "parties": "Parteien",
            "start_date": "Startdatum",
            "end_date": "Enddatum",
            "fixed_term": "Befristet",
            "probation_period_months": "Probezeit (Monate)",
            "weekly_hours": "Wochenstunden",
            "base_salary_eur": "Grundgehalt (EUR)",
            "vacation_days_per_year": "Urlaubstage",
            "notice_period_employee": "Kündigungsfrist AN",
            "notice_period_employer": "Kündigungsfrist AG",
            # SaaS
            "customer_name": "Kunde",
            "vendor_name": "Anbieter",
            "product_name": "Produkt",
            "annual_contract_value_eur": "Jährlicher Vertragswert (EUR)",
            "auto_renew": "Auto-Renewal",
            "renewal_notice_days": "Kündigungsfrist (Tage)",
            "min_term_months": "Mindestlaufzeit (Monate)",
            "data_location": "Datenlokation",
            "uptime_sla_percent": "SLA Uptime (%)",
            "liability_cap_multiple_acv": "Haftungsgrenze (x ACV)",
            # NDA
            "disclosing_party": "Offenlegende Partei",
            "receiving_party": "Empfangende Partei",
            "nda_type": "NDA-Typ",
            "term_years": "Laufzeit (Jahre)",
            "survival_period_years": "Nachwirkung (Jahre)",
            "penalty_amount_eur": "Vertragsstrafe (EUR)",
            # Mietvertrag
            "landlord_name": "Vermieter",
            "tenant_name": "Mieter",
            "property_address": "Adresse",
            "area_sqm": "Fläche (m²)",
            "monthly_rent_eur": "Kaltmiete (EUR)",
            "monthly_utilities_eur": "Nebenkosten (EUR)",
            "deposit_months": "Kaution (Monatsmieten)",
            # Allgemein
            "contract_value_eur": "Vertragswert (EUR)",
            "payment_terms": "Zahlungsbedingungen",
            "termination_notice_days": "Kündigungsfrist (Tage)",
            "governing_law": "Anwendbares Recht",
            "jurisdiction": "Gerichtsstand",
        }
        
        data_rows = []
        for key, value in extracted_data.items():
            if value is not None and value != "" and value != []:
                label = field_labels.get(key, key.replace("_", " ").title())
                
                # Werte formatieren
                if isinstance(value, bool):
                    value = "Ja" if value else "Nein"
                elif isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        value = ", ".join([f"{p.get('name', 'N/A')} ({p.get('role', '')})" for p in value])
                    else:
                        value = ", ".join(str(v) for v in value)
                elif isinstance(value, (int, float)):
                    if "eur" in key.lower() or "salary" in key.lower() or "rent" in key.lower():
                        value = f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                    elif "percent" in key.lower():
                        value = f"{value}%"
                    else:
                        value = str(value)
                else:
                    value = str(value)
                
                data_rows.append([label, value])
        
        if data_rows:
            data_table = Table(data_rows, colWidths=[6*cm, 10*cm])
            data_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), SBS_BLUE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.lightgrey),
            ]))
            story.append(data_table)
        
        story.append(Spacer(1, 5*mm))
    
    # === RISIKEN ===
    all_risks = []
    for level in ["critical", "high", "medium", "low"]:
        risks = risk_assessment.get(f"{level}_risks", [])
        for risk in risks:
            risk["level"] = level
            all_risks.append(risk)
    
    if all_risks:
        story.append(Paragraph("Identifizierte Risiken", styles["Heading1"]))
        
        for i, risk in enumerate(all_risks, 1):
            level = risk.get("level", "medium")
            title = risk.get("title", risk.get("issü_title", "Risiko"))
            description = risk.get("description", risk.get("issü_description", ""))
            clause = risk.get("clause_snippet", risk.get("clause_text", ""))
            reference = risk.get("policy_reference", risk.get("legal_basis", ""))
            
            # Risiko-Header
            risk_color = get_risk_color(level)
            risk_label = get_risk_label(level)
            
            header_data = [[f"{i}. {title}", risk_label]]
            header_table = Table(header_data, colWidths=[13*cm, 3*cm])
            header_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (0, 0), 11),
                ("FONTSIZE", (1, 0), (1, 0), 9),
                ("TEXTCOLOR", (0, 0), (0, 0), SBS_BLUE_DARK),
                ("TEXTCOLOR", (1, 0), (1, 0), risk_color),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(header_table)
            
            # Beschreibung
            if description:
                story.append(Paragraph(description, styles["Normal"]))
            
            # Klausel-Zitat
            if clause:
                clause_style = ParagraphStyle(
                    "Clause",
                    parent=styles["Normal"],
                    fontSize=9,
                    textColor=SBS_GRAY,
                    leftIndent=10,
                    borderLeftWidth=2,
                    borderLeftColor=SBS_GRAY,
                    borderPadding=5,
                )
                story.append(Paragraph(f'„{clause}"', clause_style))
            
            # Referenz
            if reference:
                story.append(Paragraph(f"📖 {reference}", styles["Small"]))
            
            story.append(Spacer(1, 3*mm))
    else:
        story.append(Paragraph("Identifizierte Risiken", styles["Heading1"]))
        story.append(Paragraph("✅ Keine signifikanten Risiken identifiziert.", styles["Normal"]))
    
    # === FOOTER ===
    story.append(Spacer(1, 15*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=SBS_GRAY))
    story.append(Spacer(1, 3*mm))
    
    footer_text = """
    <b>SBS Deutschland GmbH & Co. KG</b><br/>
    In der Dell 19, 69469 Weinheim<br/>
    Dieser Report wurde automatisch durch KI-gestützte Analyse erstellt.<br/>
    Er ersetzt keine rechtliche Beratung.
    """
    story.append(Paragraph(footer_text, styles["Footer"]))
    
    # PDF generieren
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
