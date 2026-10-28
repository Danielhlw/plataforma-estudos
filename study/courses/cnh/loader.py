from __future__ import annotations

import json
import random

from study.core.norms import validate_exam_config
from study.courses.model import Catalog, Choice, Flashcard, Lesson, Module, Question, Topic
from study.paths import CNH_DATA


def load_exam_config() -> dict:
    path = CNH_DATA / "exam_config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    problems = validate_exam_config(config)
    if problems:
        raise ValueError(" ".join(problems))
    return config


def load_cnh_catalog() -> Catalog:
    order = ["sinalizacao", "infracoes", "circulacao", "meio-ambiente", "procedimentos-al"]
    folder = CNH_DATA / "modules"
    modules = []
    for module_id in order:
        path = folder / f"{module_id}.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        modules.append(_module(raw))
    return Catalog(
        course_id="cnh-al",
        title="CNH — Alagoas",
        disclaimer=(
            "Preparação pessoal, não é prova oficial nem garantia de aprovação. "
            "As questões são de treino, escritas a partir do CTB, da Resolução CONTRAN 1.020/2025 "
            "e da Portaria SENATRAN 923/2025, com leitura em 27/10/2026. "
            "A distribuição do simulado por bloco é estimativa pedagógica, não peso publicado pela Senatran."
        ),
        modules=modules,
    )


def bank_gaps(catalog: Catalog, config: dict | None = None) -> list[str]:
    config = config or load_exam_config()
    gaps = []
    for module_id, needed in config["distribution"]["modules"].items():
        module = catalog.module(module_id)
        have = 0 if module is None else sum(1 for question in module.questions if question.exercise_type == "mcq" and len(question.choices) == 4)
        if have < needed:
            gaps.append(f"{module_id}: há {have} questões e o simulado pede {needed}.")
    return gaps


def _module(raw: dict) -> Module:
    topics = [_topic(item, raw["id"], raw.get("examImportance", 0)) for item in raw["topics"]]
    return Module(
        id=raw["id"],
        title=raw["title"],
        summary=raw["summary"],
        topics=topics,
        exam_importance=raw.get("examImportance", 0),
        official_block=raw.get("officialBlock", ""),
    )


def _topic(raw: dict, module_id: str, importance: int) -> Topic:
    body = raw["lesson"]
    return Topic(
        id=raw["id"],
        name=raw["name"],
        module_id=module_id,
        lesson=Lesson(
            blocks=body.get("blocks", []),
            concepts=body.get("concepts", []),
            examples=body.get("examples", []),
            comparisons=body.get("comparisons", []),
            relations=body.get("relations", []),
            rules=body.get("rules", []),
            pitfalls=body.get("pitfalls", []),
            memorize=body.get("memorize", []),
            sources=body.get("sources", []),
        ),
        flashcards=[
            Flashcard(id=card["id"], front=card["front"], back=card["back"], source=card.get("source", ""))
            for card in raw.get("flashcards", [])
        ],
        questions=[_question(item, importance) for item in raw.get("questions", [])],
    )


def _question(raw: dict, importance: int) -> Question:
    choices = [Choice(text=option["text"], explanation=option["explanation"]) for option in raw["options"]]
    correct = choices[raw["correctIndex"]]
    rng = random.Random(raw["id"])
    rng.shuffle(choices)
    return Question(
        id=raw["id"],
        course_id="cnh-al",
        module_id=raw["module"],
        topic_id=raw["topic"],
        prompt=raw["question"],
        choices=choices,
        correct_index=choices.index(correct),
        recognition_key=raw["recognitionKey"],
        difficulty=raw.get("difficulty", 1),
        source=raw.get("source", ""),
        source_url=raw.get("sourceUrl", ""),
        last_verified_at=raw.get("lastVerifiedAt"),
        review_status=raw.get("reviewStatus", "pendente"),
        origin=raw.get("origin", "treino"),
        norm_version=raw.get("normVersion", ""),
        exam_importance=raw.get("examImportance", importance),
    )
