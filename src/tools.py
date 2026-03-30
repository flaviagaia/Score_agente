from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from .sample_data import load_customers


SCORE_BAND_LABELS = {
    "good": "bom",
    "fair": "regular",
    "poor": "baixo",
}


MAIN_DRIVER_TRANSLATIONS = {
    "Strong payment consistency and low recent delinquency.": "Boa consistência de pagamentos e baixa inadimplência recente.",
    "High utilization and late payments are pulling the score down.": "Alta utilização do crédito e atrasos recentes estão pressionando o score para baixo.",
    "Multiple recent delinquencies, very high utilization, and negative records.": "Múltiplas inadimplências recentes, utilização muito alta e registros negativos estão afetando o score.",
}


def _get_customer_row(customer_id: str) -> dict[str, Any]:
    customers = load_customers()
    row = customers.loc[customers["customer_id"] == customer_id]
    if row.empty:
        raise ValueError(f"Customer '{customer_id}' not found.")
    return row.iloc[0].to_dict()


def _localized_profile(profile: dict[str, Any]) -> dict[str, Any]:
    localized = dict(profile)
    localized["score_band"] = SCORE_BAND_LABELS.get(str(profile["score_band"]), str(profile["score_band"]))
    localized["main_drivers"] = MAIN_DRIVER_TRANSLATIONS.get(
        str(profile["main_drivers"]),
        str(profile["main_drivers"]),
    )
    return localized


@tool
def get_credit_profile(customer_id: str) -> str:
    """Return the structured credit profile for a customer_id."""
    profile = _localized_profile(_get_customer_row(customer_id))
    return json.dumps(profile, ensure_ascii=False, indent=2)


@tool
def explain_score_factors(customer_id: str) -> str:
    """Explain the main score factors for a customer_id using the internal profile."""
    profile = _localized_profile(_get_customer_row(customer_id))
    score = int(profile["score"])
    utilization = int(profile["credit_utilization_pct"])
    late_payments = int(profile["recent_late_payments"])
    negative_records = int(profile["negative_records"])
    inquiries = int(profile["hard_inquiries_6m"])

    strengths = []
    risks = []

    if profile["on_time_payment_ratio"] >= 0.95:
        strengths.append("pagamentos feitos em dia com alta consistência")
    if utilization <= 30:
        strengths.append("utilização de crédito em nível saudável")
    if late_payments == 0:
        strengths.append("ausência de atrasos recentes")

    if utilization > 50:
        risks.append("utilização de crédito acima do ideal")
    if late_payments > 0:
        risks.append(f"{late_payments} atraso(s) recente(s)")
    if negative_records > 0:
        risks.append(f"{negative_records} registro(s) negativo(s)")
    if inquiries >= 4:
        risks.append("muitas consultas recentes ao crédito")

    return (
        f"O cliente está na faixa '{profile['score_band']}' com score {score}. "
        f"Os principais pontos positivos são: {', '.join(strengths) if strengths else 'nenhum destaque relevante no momento'}. "
        f"Os principais fatores de pressão sobre o score são: {', '.join(risks) if risks else 'baixo nível de risco recente'}. "
        f"Resumo interno: {profile['main_drivers']}"
    )


@tool
def recommend_actions(customer_id: str) -> str:
    """Recommend concrete next actions that may help improve the score profile."""
    profile = _localized_profile(_get_customer_row(customer_id))
    actions = []

    if int(profile["credit_utilization_pct"]) > 50:
        actions.append("reduzir a utilização do limite para abaixo de 30%")
    if int(profile["recent_late_payments"]) > 0:
        actions.append("regularizar atrasos e manter os próximos pagamentos no prazo")
    if int(profile["hard_inquiries_6m"]) >= 3:
        actions.append("evitar novas solicitações de crédito no curto prazo")
    if int(profile["negative_records"]) > 0:
        actions.append("negociar ou quitar pendências negativadas")
    if not actions:
        actions.append("manter o padrão atual de pagamentos e utilização de crédito")

    return "Próximas ações recomendadas: " + "; ".join(actions) + "."


@tool
def simulate_score_change(customer_id: str, utilization_target_pct: int = 30, late_payment_reduction: int = 1) -> str:
    """Estimate a directional score improvement if utilization and late payments improve."""
    profile = _localized_profile(_get_customer_row(customer_id))
    current_score = int(profile["score"])
    current_utilization = int(profile["credit_utilization_pct"])
    current_lates = int(profile["recent_late_payments"])

    utilization_gain = max(current_utilization - utilization_target_pct, 0) * 0.8
    late_payment_gain = min(current_lates, late_payment_reduction) * 18
    estimated_score = min(round(current_score + utilization_gain + late_payment_gain), 850)

    return (
        f"Simulação simples: se a utilização cair de {current_utilization}% para {utilization_target_pct}% "
        f"e os atrasos recentes forem reduzidos em {min(current_lates, late_payment_reduction)}, "
        f"o score pode migrar aproximadamente de {current_score} para {estimated_score}. "
        "Essa é uma estimativa educacional, não uma previsão oficial."
    )


@tool
def compliance_guardrail(topic: str) -> str:
    """Return safe-answering guidance for regulated credit score explanations."""
    return (
        "Diretriz de compliance: explique fatores do score com linguagem educativa, "
        "evite prometer aprovação de crédito, não trate a resposta como aconselhamento financeiro personalizado "
        "e deixe claro quando qualquer estimativa for apenas ilustrativa. Tópico solicitado: "
        f"{topic}."
    )


ALL_TOOLS = [
    get_credit_profile,
    explain_score_factors,
    recommend_actions,
    simulate_score_change,
    compliance_guardrail,
]
