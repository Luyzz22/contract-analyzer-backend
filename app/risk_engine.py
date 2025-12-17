"""SBS Contract Intelligence - Risk Scoring Engine"""

from typing import List
from .models import (
    EmploymentContractData, ContractRiskAssessment, ClauseRisk,
    RiskCategory, RiskLevel, LegalValidity, ClauseCategory,
)


class RiskScoringEngine:
    def __init__(self):
        self.risks: List[ClauseRisk] = []
        self.missing_clauses: List[str] = []
        
    def assess_employment_contract(self, data: EmploymentContractData) -> ContractRiskAssessment:
        self.risks = []
        self.missing_clauses = []
        
        self._check_probation(data)
        self._check_overtime(data)
        self._check_non_compete(data)
        self._check_vacation(data)
        
        critical = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        
        score = min(len(critical) * 25 + len(high) * 15, 100)
        level = self._score_to_level(score)
        
        return ContractRiskAssessment(
            overall_risk_score=score,
            overall_risk_level=level,
            legal_compliance_score=score,
            financial_risk_score=0,
            operational_risk_score=0,
            data_protection_score=0,
            contract_management_score=0,
            critical_risks=critical,
            high_risks=high,
            medium_risks=[],
            low_risks=[],
            missing_clauses=self.missing_clauses,
            executive_summary=self._generate_summary(score, level, critical, data),
            confidence_score=0.9,
        )
    
    def _check_probation(self, data: EmploymentContractData):
        if data.probation and data.probation.duration_months and data.probation.duration_months > 6:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.PROBATION,
                clause_text=f"Probezeit: {data.probation.duration_months} Monate",
                risk_level=RiskLevel.CRITICAL,
                risk_score=95,
                legal_validity=LegalValidity.INVALID,
                issue_title="Probezeit überschreitet 6 Monate",
                issue_description="Maximum nach § 622 Abs. 3 BGB sind 6 Monate.",
                legal_basis="§ 622 Abs. 3 BGB",
                recommendation="Probezeit auf max. 6 Monate reduzieren.",
            ))
    
    def _check_overtime(self, data: EmploymentContractData):
        if data.working_conditions and data.working_conditions.overtime_included_in_salary:
            if not data.working_conditions.overtime_cap_hours:
                self.risks.append(ClauseRisk(
                    clause_category=ClauseCategory.OVERTIME,
                    clause_text=data.working_conditions.overtime_clause or "Überstunden abgegolten",
                    risk_level=RiskLevel.CRITICAL,
                    risk_score=85,
                    legal_validity=LegalValidity.POTENTIALLY_INVALID,
                    issue_title="Intransparente Überstundenabgeltung",
                    issue_description="Pauschale Abgeltung ohne Stundenbegrenzung ist nach BAG unwirksam.",
                    legal_basis="BAG 5 AZR 765/10; § 307 BGB",
                    recommendation="Klare Begrenzung festlegen (z.B. bis zu 10 Überstunden/Monat).",
                ))
    
    def _check_non_compete(self, data: EmploymentContractData):
        if data.non_compete and data.non_compete.post_employment:
            if data.non_compete.missing_compensation or not data.non_compete.has_adequate_compensation:
                self.risks.append(ClauseRisk(
                    clause_category=ClauseCategory.NON_COMPETE,
                    clause_text="Nachvertragliches Wettbewerbsverbot",
                    risk_level=RiskLevel.CRITICAL,
                    risk_score=100,
                    legal_validity=LegalValidity.INVALID,
                    issue_title="Wettbewerbsverbot ohne Karenzentschädigung",
                    issue_description="Ohne min. 50% Karenz ist das Verbot NICHTIG.",
                    legal_basis="§ 74 Abs. 2 HGB",
                    recommendation="Karenzentschädigung von min. 50% vereinbaren oder streichen.",
                ))
    
    def _check_vacation(self, data: EmploymentContractData):
        if data.vacation and data.vacation.days_per_year and data.vacation.days_per_year < 20:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.VACATION,
                clause_text=f"Urlaub: {data.vacation.days_per_year} Tage",
                risk_level=RiskLevel.CRITICAL,
                risk_score=80,
                legal_validity=LegalValidity.INVALID,
                issue_title="Urlaub unter gesetzlichem Minimum",
                issue_description="Minimum nach § 3 BUrlG sind 20 Werktage.",
                legal_basis="§ 3 BUrlG",
                recommendation="Urlaubsanspruch auf min. 20 Tage erhöhen.",
            ))
    
    def _score_to_level(self, score: int) -> RiskLevel:
        if score >= 70: return RiskLevel.CRITICAL
        if score >= 55: return RiskLevel.HIGH
        if score >= 40: return RiskLevel.MEDIUM
        if score >= 20: return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def _generate_summary(self, score, level, critical, data) -> str:
        job = data.job_title or "Arbeitnehmer"
        if level == RiskLevel.CRITICAL:
            return f"KRITISCH: Der Arbeitsvertrag für {job} weist {len(critical)} kritische Mängel auf. Vor Unterzeichnung rechtliche Prüfung empfohlen."
        elif level == RiskLevel.HIGH:
            return f"ERHÖHTES RISIKO: Vertragsanalyse zeigt Verhandlungsbedarf. Score: {score}/100."
        else:
            return f"WEITGEHEND MARKTKONFORM: Keine kritischen Mängel. Score: {score}/100."


class SaaSRiskScoringEngine:
    """Risk Scoring Engine für SaaS-Verträge"""
    
    def __init__(self):
        self.risks: List[ClauseRisk] = []
        self.missing_clauses: List[str] = []
    
    def assess_saas_contract(self, data: dict) -> ContractRiskAssessment:
        """Risikobewertung eines SaaS-Vertrags"""
        self.risks = []
        self.missing_clauses = []
        
        self._check_auto_renewal(data)
        self._check_data_protection(data)
        self._check_data_location(data)
        self._check_sla(data)
        self._check_liability(data)
        self._check_data_export(data)
        self._check_price_escalation(data)
        
        critical = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        medium = [r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]
        low = [r for r in self.risks if r.risk_level == RiskLevel.LOW]
        
        score = min(len(critical) * 25 + len(high) * 15 + len(medium) * 8, 100)
        level = self._score_to_level(score)
        
        return ContractRiskAssessment(
            overall_risk_score=score,
            overall_risk_level=level,
            legal_compliance_score=score,
            financial_risk_score=0,
            operational_risk_score=0,
            data_protection_score=0,
            contract_management_score=0,
            critical_risks=critical,
            high_risks=high,
            medium_risks=medium,
            low_risks=low,
            missing_clauses=self.missing_clauses,
            executive_summary=self._generate_summary(score, level, critical, data),
            confidence_score=0.9,
        )
    
    def _check_auto_renewal(self, data: dict):
        """Auto-Renewal ohne ausreichende Kündigungsfrist"""
        term = data.get("contract_term", {})
        if term.get("auto_renewal"):
            notice = term.get("notice_period_days", 0)
            if notice and notice < 30:
                self.risks.append(ClauseRisk(
                    clause_category=ClauseCategory.AUTO_RENEWAL,
                    clause_text=f"Auto-Renewal mit {notice} Tagen Kündigungsfrist",
                    risk_level=RiskLevel.CRITICAL,
                    risk_score=90,
                    legal_validity=LegalValidity.VALID,
                    issue_title="Kurze Kündigungsfrist bei Auto-Renewal",
                    issue_description=f"Die Kündigungsfrist von {notice} Tagen vor automatischer Verlängerung ist sehr kurz. Risiko einer ungewollten Vertragsverlängerung.",
                    legal_basis="§ 309 Nr. 9 BGB (AGB-Kontrolle)",
                    recommendation="Kündigungsfrist auf mindestens 30, besser 90 Tage erhöhen oder automatische Verlängerung streichen.",
                ))
    
    def _check_data_protection(self, data: dict):
        """DSGVO-Compliance prüfen"""
        dp = data.get("data_protection", {})
        if not dp.get("dpa_included"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.DATA_PROTECTION,
                clause_text="Kein AVV/DPA vorhanden",
                risk_level=RiskLevel.CRITICAL,
                risk_score=95,
                legal_validity=LegalValidity.INVALID,
                issue_title="Fehlender Auftragsverarbeitungsvertrag",
                issue_description="Kein AVV (Auftragsverarbeitungsvertrag) nach Art. 28 DSGVO vorhanden. Dies ist bei Verarbeitung personenbezogener Daten gesetzlich vorgeschrieben.",
                legal_basis="Art. 28 DSGVO",
                recommendation="AVV nach Art. 28 DSGVO abschließen. Ohne AVV ist die Nutzung des Services für personenbezogene Daten rechtswidrig.",
            ))
    
    def _check_data_location(self, data: dict):
        """Datenspeicherort prüfen"""
        dp = data.get("data_protection", {})
        location = dp.get("data_location", "").upper()
        if location and "EU" not in location and not dp.get("data_location_guaranteed_eu"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.DATA_PROTECTION,
                clause_text=f"Datenspeicherung: {dp.get('data_location')}",
                risk_level=RiskLevel.HIGH,
                risk_score=75,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Datenspeicherung außerhalb EU",
                issue_description=f"Daten werden in {dp.get('data_location')} gespeichert. Für Übermittlung außerhalb der EU sind zusätzliche Garantien (Standardvertragsklauseln) erforderlich.",
                legal_basis="Art. 44-49 DSGVO (Drittlandübermittlung)",
                recommendation="Standardvertragsklauseln (SCC) vereinbaren oder EU-Datenspeicherung vertraglich garantieren lassen.",
            ))
    
    def _check_sla(self, data: dict):
        """SLA prüfen"""
        sla = data.get("sla", {})
        uptime = sla.get("uptime_percentage")
        if uptime and uptime < 99.5:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.SLA,
                clause_text=f"SLA: {uptime}% Verfügbarkeit",
                risk_level=RiskLevel.MEDIUM,
                risk_score=50,
                legal_validity=LegalValidity.VALID,
                issue_title="Niedrige SLA-Garantie",
                issue_description=f"Die garantierte Verfügbarkeit von {uptime}% liegt unter dem Marktstandard von 99.9%. Dies entspricht bis zu {round((100-uptime)*365*24/100, 1)} Stunden Ausfall pro Jahr.",
                legal_basis="Vertragsrecht",
                recommendation="SLA auf mindestens 99.9% Verfügbarkeit verhandeln, inklusive Service Credits bei Nichteinhaltung.",
            ))
        
        if not sla.get("credit_mechanism"):
            self.missing_clauses.append("Service Credits bei SLA-Verletzung")
    
    def _check_liability(self, data: dict):
        """Haftungsbegrenzung prüfen"""
        liability = data.get("liability", {})
        cap_multiple = liability.get("cap_multiple_annual_fee")
        if cap_multiple and cap_multiple < 12:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.LIABILITY_CAP,
                clause_text=f"Haftung begrenzt auf {cap_multiple}x Jahresgebühr",
                risk_level=RiskLevel.HIGH,
                risk_score=65,
                legal_validity=LegalValidity.VALID,
                issue_title="Niedrige Haftungsobergrenze",
                issue_description=f"Die Haftung ist auf {cap_multiple}x die Jahresgebühr begrenzt. Bei kritischen Systemen kann der Schaden deutlich höher sein.",
                legal_basis="§ 309 Nr. 7 BGB",
                recommendation="Haftungscap auf mindestens 12x Jahresgebühr erhöhen oder Versicherungsnachweis verlangen.",
            ))
    
    def _check_data_export(self, data: dict):
        """Datenexport bei Vertragsende prüfen"""
        dp = data.get("data_protection", {})
        if not dp.get("data_export_format"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.DATA_PROTECTION,
                clause_text="Kein Datenexport-Format definiert",
                risk_level=RiskLevel.HIGH,
                risk_score=70,
                legal_validity=LegalValidity.VALID,
                issue_title="Vendor Lock-in durch fehlenden Datenexport",
                issue_description="Kein Format für Datenexport bei Vertragsende vereinbart. Dies erschwert einen Anbieterwechsel erheblich.",
                legal_basis="Art. 20 DSGVO (Datenportabilität)",
                recommendation="Datenexport in standardisiertem Format (CSV, JSON, XML) vertraglich vereinbaren.",
            ))
    
    def _check_price_escalation(self, data: dict):
        """Preisanpassungsklauseln prüfen"""
        pricing = data.get("pricing", {})
        if pricing.get("price_escalation_clause") and not pricing.get("price_escalation_cap"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.PRICE_ADJUSTMENT,
                clause_text=pricing.get("price_escalation_clause", "Preisanpassung möglich"),
                risk_level=RiskLevel.HIGH,
                risk_score=65,
                legal_validity=LegalValidity.VALID,
                issue_title="Unbegrenzte Preisanpassung",
                issue_description="Der Anbieter kann Preise anpassen ohne festgelegte Obergrenze. Risiko erheblicher Kostensteigerungen.",
                legal_basis="§ 307 BGB (Transparenzgebot)",
                recommendation="Preisanpassung auf max. 5% p.a. oder Inflationsindex begrenzen. Sonderkündigungsrecht bei Preiserhöhung vereinbaren.",
            ))
    
    def _score_to_level(self, score: int) -> RiskLevel:
        if score >= 70: return RiskLevel.CRITICAL
        if score >= 55: return RiskLevel.HIGH
        if score >= 40: return RiskLevel.MEDIUM
        if score >= 20: return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def _generate_summary(self, score, level, critical, data) -> str:
        service = data.get("service_name", "SaaS-Service")
        provider = data.get("provider", {}).get("name", "Anbieter")
        
        if level == RiskLevel.CRITICAL:
            return f"KRITISCH: Der SaaS-Vertrag für {service} von {provider} weist {len(critical)} kritische Mängel auf, insbesondere bei Datenschutz und Compliance. Nachverhandlung dringend empfohlen."
        elif level == RiskLevel.HIGH:
            return f"ERHÖHTES RISIKO: Der Vertrag für {service} zeigt Verbesserungsbedarf bei Datenschutz, SLA oder Haftung. Score: {score}/100."
        else:
            return f"WEITGEHEND AKZEPTABEL: Der SaaS-Vertrag für {service} entspricht im Wesentlichen dem Marktstandard. Score: {score}/100."


class NDARiskScoringEngine:
    """Risk Scoring Engine für NDAs"""
    
    def __init__(self):
        self.risks: List[ClauseRisk] = []
        self.missing_clauses: List[str] = []
    
    def assess_nda_contract(self, data: dict) -> ContractRiskAssessment:
        """Risikobewertung eines NDA"""
        self.risks = []
        self.missing_clauses = []
        
        self._check_duration(data)
        self._check_scope(data)
        self._check_penalty(data)
        self._check_exclusions(data)
        self._check_return_obligation(data)
        
        critical = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        medium = [r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]
        low = [r for r in self.risks if r.risk_level == RiskLevel.LOW]
        
        score = min(len(critical) * 25 + len(high) * 15 + len(medium) * 8, 100)
        level = self._score_to_level(score)
        
        return ContractRiskAssessment(
            overall_risk_score=score,
            overall_risk_level=level,
            legal_compliance_score=score,
            financial_risk_score=0,
            operational_risk_score=0,
            data_protection_score=0,
            contract_management_score=0,
            critical_risks=critical,
            high_risks=high,
            medium_risks=medium,
            low_risks=low,
            missing_clauses=self.missing_clauses,
            executive_summary=self._generate_summary(score, level, critical, data),
            confidence_score=0.9,
        )
    
    def _check_duration(self, data: dict):
        """Unbefristete Geheimhaltung prüfen"""
        if data.get("duration_indefinite"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.TERMINATION,
                clause_text="Unbefristete Geheimhaltungspflicht",
                risk_level=RiskLevel.CRITICAL,
                risk_score=85,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Unbefristete Geheimhaltung",
                issue_description="Die Geheimhaltungspflicht ist zeitlich unbegrenzt. Dies ist unüblich und kann unverhältnismäßig sein. Marktstandard sind 3-5 Jahre.",
                legal_basis="§ 307 BGB (Angemessenheit)",
                recommendation="Geheimhaltungspflicht auf 3-5 Jahre nach Vertragsende begrenzen.",
            ))
        
        duration = data.get("duration_years")
        if duration and duration > 10:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.TERMINATION,
                clause_text=f"Laufzeit: {duration} Jahre",
                risk_level=RiskLevel.HIGH,
                risk_score=65,
                legal_validity=LegalValidity.VALID,
                issue_title="Überlange Geheimhaltungsfrist",
                issue_description=f"Die Geheimhaltungspflicht von {duration} Jahren ist ungewöhnlich lang. Marktstandard sind 3-5 Jahre.",
                legal_basis="Marktüblichkeit",
                recommendation="Kürzere Laufzeit von max. 5 Jahren verhandeln.",
            ))
    
    def _check_scope(self, data: dict):
        """Zu weite Definition prüfen"""
        definition = data.get("definition_confidential", "").lower()
        if "alle" in definition and "informationen" in definition:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.NON_COMPETE,
                clause_text=data.get("definition_confidential", ""),
                risk_level=RiskLevel.HIGH,
                risk_score=60,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Zu weite Definition vertraulicher Informationen",
                issue_description="Die Definition 'alle Informationen' ist sehr weit gefasst und könnte auch triviale Informationen umfassen.",
                legal_basis="§ 307 BGB (Transparenzgebot)",
                recommendation="Definition präzisieren: nur markierte oder ausdrücklich als vertraulich bezeichnete Informationen.",
            ))
    
    def _check_penalty(self, data: dict):
        """Vertragsstrafe prüfen"""
        penalty = data.get("penalty_amount")
        if penalty and float(penalty) > 100000:
            per_violation = data.get("penalty_per_violation", False)
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.SALARY,
                clause_text=data.get("penalty_clause", f"Vertragsstrafe: {penalty} EUR"),
                risk_level=RiskLevel.HIGH if per_violation else RiskLevel.MEDIUM,
                risk_score=70 if per_violation else 50,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Hohe Vertragsstrafe",
                issue_description=f"Die Vertragsstrafe von {penalty:,.0f} EUR ist erheblich{' und gilt pro Verstoß' if per_violation else ''}.",
                legal_basis="§ 343 BGB (Herabsetzung)",
                recommendation="Vertragsstrafe auf angemessenes Maß reduzieren oder Obergrenze vereinbaren.",
            ))
    
    def _check_exclusions(self, data: dict):
        """Ausnahmen prüfen"""
        exclusions = data.get("exclusions", [])
        required_exclusions = ["öffentlich bekannt", "rechtmäßig erhalten", "eigenständig entwickelt"]
        
        if not exclusions:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.NON_COMPETE,
                clause_text="Keine Ausnahmen definiert",
                risk_level=RiskLevel.MEDIUM,
                risk_score=45,
                legal_validity=LegalValidity.VALID,
                issue_title="Fehlende Standardausnahmen",
                issue_description="Das NDA enthält keine üblichen Ausnahmen für öffentlich bekannte oder rechtmäßig erhaltene Informationen.",
                legal_basis="Marktüblichkeit",
                recommendation="Standardausnahmen aufnehmen: öffentlich bekannt, rechtmäßig von Dritten, eigenständig entwickelt, behördliche Offenlegung.",
            ))
    
    def _check_return_obligation(self, data: dict):
        """Rückgabepflicht prüfen"""
        if not data.get("return_of_information") and not data.get("destruction_of_information"):
            self.missing_clauses.append("Rückgabe- oder Vernichtungspflicht nach Vertragsende")
    
    def _score_to_level(self, score: int) -> RiskLevel:
        if score >= 70: return RiskLevel.CRITICAL
        if score >= 55: return RiskLevel.HIGH
        if score >= 40: return RiskLevel.MEDIUM
        if score >= 20: return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def _generate_summary(self, score, level, critical, data) -> str:
        nda_type = data.get("nda_type", "unbekannt")
        type_label = {"unilateral": "einseitiges", "mutual": "gegenseitiges", "multilateral": "Mehrparteien-"}.get(nda_type, "")
        
        if level == RiskLevel.CRITICAL:
            return f"KRITISCH: Das {type_label}NDA weist {len(critical)} kritische Mängel auf. Nachverhandlung empfohlen. Score: {score}/100."
        elif level == RiskLevel.HIGH:
            return f"ERHÖHTES RISIKO: Das {type_label}NDA zeigt Verbesserungsbedarf. Score: {score}/100."
        else:
            return f"AKZEPTABEL: Das {type_label}NDA entspricht weitgehend dem Marktstandard. Score: {score}/100."


class VendorRiskScoringEngine:
    """Risk Scoring Engine fuer Lieferantenvertraege"""
    
    def __init__(self):
        self.risks: List[ClauseRisk] = []
        self.missing_clauses: List[str] = []
    
    def assess_vendor_contract(self, data: dict) -> ContractRiskAssessment:
        """Risikobewertung eines Lieferantenvertrags"""
        self.risks = []
        self.missing_clauses = []
        
        self._check_warranty(data)
        self._check_liability(data)
        self._check_payment(data)
        self._check_audit_rights(data)
        self._check_price_adjustment(data)
        
        critical = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        medium = [r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]
        low = [r for r in self.risks if r.risk_level == RiskLevel.LOW]
        
        score = min(len(critical) * 25 + len(high) * 15 + len(medium) * 8, 100)
        level = self._score_to_level(score)
        
        return ContractRiskAssessment(
            overall_risk_score=score,
            overall_risk_level=level,
            legal_compliance_score=score,
            financial_risk_score=0,
            operational_risk_score=0,
            data_protection_score=0,
            contract_management_score=0,
            critical_risks=critical,
            high_risks=high,
            medium_risks=medium,
            low_risks=low,
            missing_clauses=self.missing_clauses,
            executive_summary=self._generate_summary(score, level, critical, data),
            confidence_score=0.9,
        )
    
    def _check_warranty(self, data: dict):
        """Gewaehrleistung pruefen"""
        warranty = data.get("warranty", {})
        months = warranty.get("duration_months")
        
        if months is None:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.OTHER,
                clause_text="Keine Gewaehrleistungsregelung gefunden",
                risk_level=RiskLevel.CRITICAL,
                risk_score=90,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Fehlende Gewaehrleistung",
                issue_description="Der Vertrag enthaelt keine explizite Gewaehrleistungsregelung. Es gelten die gesetzlichen Regelungen (24 Monate), aber dies sollte vertraglich klargestellt werden.",
                legal_basis="§§ 434 ff. BGB",
                recommendation="Gewaehrleistungsfrist von mindestens 24 Monaten vertraglich vereinbaren.",
            ))
        elif months < 12:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.OTHER,
                clause_text=f"Gewaehrleistung: {months} Monate",
                risk_level=RiskLevel.CRITICAL,
                risk_score=85,
                legal_validity=LegalValidity.REQUIRES_REVIEW,
                issue_title="Zu kurze Gewaehrleistungsfrist",
                issue_description=f"Die Gewaehrleistungsfrist von {months} Monaten ist sehr kurz. Gesetzlich sind 24 Monate vorgesehen.",
                legal_basis="§ 438 BGB",
                recommendation="Gewaehrleistungsfrist auf mindestens 24 Monate erhoehen.",
            ))
    
    def _check_liability(self, data: dict):
        """Haftung pruefen"""
        liability = data.get("liability", {})
        cap_type = liability.get("cap_type", "").lower()
        
        if cap_type == "excluded":
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.LIABILITY_CAP,
                clause_text="Haftung ausgeschlossen",
                risk_level=RiskLevel.CRITICAL,
                risk_score=95,
                legal_validity=LegalValidity.INVALID,
                issue_title="Vollstaendiger Haftungsausschluss",
                issue_description="Ein vollstaendiger Haftungsausschluss ist in AGB unwirksam und auch individualvertraglich problematisch.",
                legal_basis="§ 309 Nr. 7 BGB",
                recommendation="Angemessene Haftungsregelung mit verhaeltnismaessigem Cap vereinbaren.",
            ))
    
    def _check_payment(self, data: dict):
        """Zahlungsbedingungen pruefen"""
        payment = data.get("payment", {})
        days = payment.get("payment_days")
        
        if days and days < 14:
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.OTHER,
                clause_text=f"Zahlungsziel: {days} Tage",
                risk_level=RiskLevel.MEDIUM,
                risk_score=45,
                legal_validity=LegalValidity.VALID,
                issue_title="Kurzes Zahlungsziel",
                issue_description=f"Das Zahlungsziel von {days} Tagen ist kurz und kann Liquiditaetsdruck erzeugen.",
                legal_basis="Marktstandard",
                recommendation="Zahlungsziel von mindestens 30 Tagen verhandeln.",
            ))
    
    def _check_audit_rights(self, data: dict):
        """Auditrechte pruefen"""
        quality = data.get("quality", {})
        if not quality.get("audit_rights"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.OTHER,
                clause_text="Keine Auditrechte vereinbart",
                risk_level=RiskLevel.HIGH,
                risk_score=60,
                legal_validity=LegalValidity.VALID,
                issue_title="Fehlende Auditrechte",
                issue_description="Ohne Auditrechte kann die Qualitaet und Compliance des Lieferanten nicht ueberprueft werden.",
                legal_basis="Lieferkettensorgfaltspflichtengesetz (LkSG)",
                recommendation="Auditrechte fuer Qualitaet und Compliance vereinbaren.",
            ))
    
    def _check_price_adjustment(self, data: dict):
        """Preisanpassung pruefen"""
        pricing = data.get("pricing", {})
        if pricing.get("price_adjustment_clause") and not pricing.get("price_adjustment_index"):
            self.risks.append(ClauseRisk(
                clause_category=ClauseCategory.PRICE_ADJUSTMENT,
                clause_text=pricing.get("price_adjustment_clause", "Preisanpassung moeglich"),
                risk_level=RiskLevel.HIGH,
                risk_score=65,
                legal_validity=LegalValidity.VALID,
                issue_title="Unbestimmte Preisanpassung",
                issue_description="Die Preisanpassungsklausel ist nicht an einen objektiven Index gebunden.",
                legal_basis="§ 307 BGB",
                recommendation="Preisanpassung an einen objektiven Index (z.B. Erzeugerpreisindex) binden.",
            ))
    
    def _score_to_level(self, score: int) -> RiskLevel:
        if score >= 70: return RiskLevel.CRITICAL
        if score >= 55: return RiskLevel.HIGH
        if score >= 40: return RiskLevel.MEDIUM
        if score >= 20: return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def _generate_summary(self, score, level, critical, data) -> str:
        supplier = data.get("supplier", {}).get("name", "Lieferant")
        subject = data.get("contract_subject", "Lieferung")
        
        if level == RiskLevel.CRITICAL:
            return f"KRITISCH: Der Lieferantenvertrag mit {supplier} fuer {subject} weist {len(critical)} kritische Maengel auf. Nachverhandlung dringend empfohlen."
        elif level == RiskLevel.HIGH:
            return f"ERHOEHTES RISIKO: Der Vertrag mit {supplier} zeigt Verbesserungsbedarf bei Gewaehrleistung oder Haftung. Score: {score}/100."
        else:
            return f"AKZEPTABEL: Der Lieferantenvertrag mit {supplier} entspricht weitgehend dem Marktstandard. Score: {score}/100."
