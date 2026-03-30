from __future__ import annotations

import unittest

from src.agent import ask_credit_agent
from src.tools import explain_score_factors, recommend_actions, simulate_score_change


class CreditAgentTest(unittest.TestCase):
    def test_fallback_agent_returns_answer(self) -> None:
        result = ask_credit_agent(
            customer_id="CRED-1002",
            user_question="Explique meu score e diga o que fazer.",
        )
        self.assertIn("runtime_mode", result)
        self.assertIn("answer", result)
        self.assertGreater(len(result["answer"]), 20)

    def test_explanation_tool_mentions_score(self) -> None:
        output = explain_score_factors.invoke({"customer_id": "CRED-1002"})
        self.assertIn("score", output.lower())

    def test_recommend_actions_tool_returns_actions(self) -> None:
        output = recommend_actions.invoke({"customer_id": "CRED-1003"})
        self.assertIn("ações", output.lower())

    def test_simulation_tool_returns_estimate(self) -> None:
        output = simulate_score_change.invoke({"customer_id": "CRED-1003"})
        self.assertIn("estimativa", output.lower())


if __name__ == "__main__":
    unittest.main()
