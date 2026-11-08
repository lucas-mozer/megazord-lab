"""Verifica o formato Markdown compacto, sem modelo de IA, segredos ou conexão externa."""
import re
import unittest

HEADER = re.compile(r"\A\[MZ-MSG\]\n(?P<fields>.*?)\n\[/MZ-MSG\]\n\n(?P<body>.*)\Z", re.S)
REQUIRED = {"session", "task", "from", "to", "type", "seq", "status"}
AGENTS = {"claude", "codex", "chatgpt", "gemini", "grok"}


def parse_compact(message):
    m = HEADER.match(message)
    if not m:
        raise ValueError("Cabeçalho ausente")
    fields = {}
    for line in m["fields"].splitlines():
        key, sep, value = line.partition(":")
        if not sep or key.strip() in fields:
            raise ValueError("Campo incorreto/repetido")
        fields[key.strip()] = value.strip()
    if not REQUIRED.issubset(fields):
        raise ValueError("Faltam campos")
    if fields["from"] not in AGENTS or fields["to"] not in AGENTS:
        raise ValueError("Agente desconhecido")
    if fields["from"] == fields["to"]:
        raise ValueError("Remetente igual ao destino")
    if len(m["body"]) > 8000:
        raise ValueError("Mensagem muito longa")
    return fields, m["body"]


class CompactTest(unittest.TestCase):
    def test_handoff(self):
        msg = ("[MZ-MSG]\nsession: MZ-20261108-M1\ntask: T-073\n"
               "from: claude\nto: codex\ntype: request\nseq: 2\n"
               "status: open\n[/MZ-MSG]\n\n"
               "Mudou: 2 arquivos.\nBase: commit SHA.\nPendente: revisão.")
        fields, body = parse_compact(msg)
        self.assertEqual(fields["to"], "codex")
        self.assertLess(len(msg), 350)
        self.assertIn("Pendente: revisão.", body)

    def test_unknown_agent(self):
        msg = ("[MZ-MSG]\nsession: MZ-20261108-M1\ntask: T-073\n"
               "from: estranho\nto: codex\ntype: request\nseq: 1\n"
               "status: open\n[/MZ-MSG]\n\nTeste")
        with self.assertRaises(ValueError):
            parse_compact(msg)


if __name__ == "__main__":
    unittest.main()
