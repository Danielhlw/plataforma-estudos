from __future__ import annotations

from dataclasses import dataclass, field

from study.core.models import QuestionRef


@dataclass
class Choice:
    text: str
    explanation: str


@dataclass
class Lesson:
    blocks: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    comparisons: list[dict[str, str]] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    pitfalls: list[str] = field(default_factory=list)
    memorize: list[str] = field(default_factory=list)
    sources: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Flashcard:
    id: str
    front: str
    back: str
    source: str = ""


@dataclass
class Question:
    id: str
    course_id: str
    module_id: str
    topic_id: str
    prompt: str
    choices: list[Choice]
    correct_index: int
    recognition_key: str
    difficulty: int = 1
    source: str = ""
    source_url: str = ""
    last_verified_at: str | None = None
    review_status: str = "verificado"
    origin: str = "treino"
    exercise_type: str = "mcq"
    counts_as_evidence: bool = True
    norm_version: str = ""
    exam_importance: int = 0

    @property
    def correct_text(self) -> str:
        return self.choices[self.correct_index].text

    def ref(self) -> QuestionRef:
        return QuestionRef(
            question_id=self.id,
            topic_id=self.topic_id,
            module_id=self.module_id,
            difficulty=self.difficulty,
            exam_importance=self.exam_importance,
            exercise_type=self.exercise_type,
        )


@dataclass
class Topic:
    id: str
    name: str
    module_id: str
    lesson: Lesson
    flashcards: list[Flashcard] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)


@dataclass
class Module:
    id: str
    title: str
    summary: str
    topics: list[Topic]
    exam_importance: int = 0
    official_block: str = ""

    @property
    def questions(self) -> list[Question]:
        return [question for topic in self.topics for question in topic.questions]

    @property
    def question_count(self) -> int:
        return len(self.questions)


@dataclass
class Catalog:
    course_id: str
    title: str
    disclaimer: str
    modules: list[Module]

    def questions(self) -> list[Question]:
        return [question for module in self.modules for question in module.questions]

    def question_map(self) -> dict[str, Question]:
        return {question.id: question for question in self.questions()}

    def get(self, question_id: str) -> Question | None:
        return self.question_map().get(question_id)

    def module(self, module_id: str) -> Module | None:
        return next((module for module in self.modules if module.id == module_id), None)

    def topic(self, topic_id: str) -> Topic | None:
        for module in self.modules:
            for topic in module.topics:
                if topic.id == topic_id:
                    return topic
        return None

    def summaries(self) -> list[dict]:
        rows = []
        for module in self.modules:
            rows.append(
                {
                    "id": module.id,
                    "title": module.title,
                    "question_count": module.question_count,
                    "topics": [
                        {"id": topic.id, "name": topic.name, "question_count": len(topic.questions)}
                        for topic in module.topics
                    ],
                }
            )
        return rows
