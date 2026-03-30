from __future__ import annotations

import streamlit as st

from src.agent import ask_credit_agent
from src.sample_data import load_customers


st.set_page_config(page_title="Agente de Explicação de Score", page_icon="💳", layout="wide")

st.title("Agente de Explicação de Score de Crédito")
st.caption(
    "MVP com LangChain Agents para interação com clientes, explicação de score, recomendação de ações e simulação educativa."
)

customers = load_customers()

with st.sidebar:
    st.subheader("Configuração")
    selected_customer = st.selectbox("Cliente", customers["customer_id"].tolist())
    default_question = st.text_area(
        "Pergunta do cliente",
        value="Meu score caiu. Você consegue me explicar os principais motivos e o que eu posso fazer para melhorar?",
        height=140,
    )
    run_button = st.button("Consultar agente")

selected_profile = customers.loc[customers["customer_id"] == selected_customer].iloc[0].to_dict()

metric_cols = st.columns(4)
metric_cols[0].metric("Cliente", selected_profile["name"])
metric_cols[1].metric("Score", int(selected_profile["score"]))
metric_cols[2].metric("Faixa", selected_profile["score_band"])
metric_cols[3].metric("Utilização", f"{int(selected_profile['credit_utilization_pct'])}%")

left, right = st.columns([1.2, 1.0])

with left:
    st.subheader("Perfil consultado")
    st.json(selected_profile)

with right:
    st.subheader("Arquitetura do agente")
    st.markdown(
        """
        - `LangChain Agent`: orquestra o fluxo de decisão e tool calling.
        - `get_credit_profile`: busca o perfil estruturado do cliente.
        - `explain_score_factors`: traduz os drivers do score.
        - `recommend_actions`: sugere próximos passos concretos.
        - `simulate_score_change`: simula melhoria educacional.
        - `compliance_guardrail`: reforça linguagem segura para contexto regulado.
        """
    )

if run_button:
    result = ask_credit_agent(selected_customer, default_question)
    st.subheader("Resposta do agente")
    st.info(f"Modo de execução: {result['runtime_mode']}")
    st.write(result["answer"])
