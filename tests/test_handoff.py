"""Teste sintético de contrato de mensagens; nenhum agente/API é chamado."""
import unittest

AGENTS = {"claude", "codex", "chatgpt", "gemini", "grok"}
REQUIRED = {"task", "seq", "from", "to", "status"}


def validate(message, seen):
    if not isinstance(message, dict) or not REQUIRED.issubset(message):
        return False
    if message["from"] not in AGENTS or message["to"] not in AGENTS:
        return False
    if message["from"] == message["to"] or message["status"] != "open":
        return False
    if not isinstance(message["seq"], int) or isinstance(message["seq"], bool):
        return False
    if message["seq"] != seen + 1:
        return False
    if message.get("sender_type") == "Bot":
        return False
    return True


class HandoffContractTest(unittest.TestCase):
    def test_message(self):
        self.assertTrue(validate(
            dict(task="T-DEMO", seq=2, **{"from": "claude", "to": "codex"}, status="open"),
            seen=1))

    def test_replay_is_blocked(self):
        msg = dict(task="T-DEMO", seq=2, **{"from": "claude", "to": "codex"}, status="open")
        self.assertFalse(validate(msg, seen=2))

    def test_bot_is_blocked(self):
        msg = dict(task="T-DEMO", seq=2, **{"from": "claude", "to": "codex"},
                   status="open", sender_type="Bot")
        self.assertFalse(validate(msg, seen=1))

    def test_unregistered_agent_blocked(self):
        msg = dict(task="T-DEMO", seq=2, **{"from": "other", "to": "codex"}, status="open")
        self.assertFalse(validate(msg, seen=1))


if __name__ == "__main__":
    unittest.main()
