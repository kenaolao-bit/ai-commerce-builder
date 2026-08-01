"""Appel structure a l'API Claude, partage par tous les modules IA.

Section 6 de la specification : chaque module IA utilise soit des regles
deterministes, soit un appel a l'API Claude avec un prompt structure
retournant du JSON. Ce module centralise cet appel ; si aucune cle API n'est
configuree ou si l'appel echoue, l'appelant doit retomber sur ses regles
deterministes (le MVP ne doit jamais bloquer faute de cle API).
"""

import json
import re

from backend.security.secrets import get_settings


class ClaudeUnavailableError(Exception):
    pass


def ask_claude_json(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-5") -> dict:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise ClaudeUnavailableError("ANTHROPIC_API_KEY non configuree.")

    try:
        import anthropic
    except ImportError as exc:
        raise ClaudeUnavailableError("Le package 'anthropic' n'est pas installe.") from exc

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")

    match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
    if not match:
        raise ClaudeUnavailableError("Reponse Claude non exploitable (pas de JSON detecte).")

    return json.loads(match.group(0))
