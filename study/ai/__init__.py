"""Fornecedor de IA desacoplado. Esta versão não chama nenhum modelo."""

from __future__ import annotations

from typing import Protocol


class TutorUnavailable(RuntimeError):
    pass


class TutorProvider(Protocol):
    name: str

    def available(self) -> bool: ...

    def complete(self, prompt: str, context: dict) -> str: ...


class UnconfiguredTutor:
    name = "nenhum"

    def available(self) -> bool:
        return False

    def complete(self, prompt: str, context: dict) -> str:
        raise TutorUnavailable(
            "Não há um modelo ligado a esta plataforma. "
            "Use o relatório Markdown em «Preparar análise com IA»."
        )


def get_tutor() -> TutorProvider:
    return UnconfiguredTutor()
