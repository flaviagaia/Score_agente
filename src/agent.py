from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from .tools import ALL_TOOLS, compliance_guardrail, explain_score_factors, get_credit_profile, recommend_actions, simulate_score_change


SYSTEM_PROMPT = """
You are a customer-facing credit score explanation agent.

Your responsibilities:
- explain score drivers in plain language;
- stay grounded in the customer profile and tool outputs;
- suggest practical next steps without promising credit approval;
- clearly label simulations as educational estimates;
- keep a calm, transparent, non-judgmental tone.

Always use tools before giving a final answer when a customer_id is available.
Never invent credit data that is not returned by the tools.
"""


def build_langchain_agent(model_name: str = "gpt-4.1-mini"):
    return create_agent(
        model=model_name,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="credit_score_explainer_agent",
    )


def run_fallback_agent(customer_id: str, user_question: str) -> str:
    profile = get_credit_profile.invoke({"customer_id": customer_id})
    explanation = explain_score_factors.invoke({"customer_id": customer_id})
    actions = recommend_actions.invoke({"customer_id": customer_id})
    simulation = simulate_score_change.invoke({"customer_id": customer_id})
    guardrail = compliance_guardrail.invoke({"topic": user_question})

    return (
        f"Pergunta do cliente: {user_question}\n\n"
        f"Perfil consultado:\n{profile}\n\n"
        f"Explicação:\n{explanation}\n\n"
        f"Ações recomendadas:\n{actions}\n\n"
        f"Simulação educativa:\n{simulation}\n\n"
        f"{guardrail}"
    )


def ask_credit_agent(customer_id: str, user_question: str, model_name: str = "gpt-4.1-mini") -> dict[str, Any]:
    if os.getenv("OPENAI_API_KEY"):
        agent = build_langchain_agent(model_name=model_name)
        response = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"customer_id={customer_id}. "
                            f"Customer question: {user_question}"
                        )
                    )
                ]
            }
        )
        final_message = response["messages"][-1]
        content = final_message.content if isinstance(final_message, AIMessage) else str(final_message)
        return {
            "runtime_mode": "langchain_agent",
            "answer": content,
        }

    return {
        "runtime_mode": "deterministic_fallback",
        "answer": run_fallback_agent(customer_id=customer_id, user_question=user_question),
    }
