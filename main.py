from __future__ import annotations

from src.agent import ask_credit_agent


def main() -> None:
    result = ask_credit_agent(
        customer_id="CRED-1002",
        user_question="Meu score caiu. O que mais pesou e o que posso fazer para melhorar?",
    )
    print("Score Agente")
    print("-------------------------------------")
    print(f"runtime_mode: {result['runtime_mode']}")
    print(result["answer"])


if __name__ == "__main__":
    main()
