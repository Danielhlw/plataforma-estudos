"""Orquestra catálogo, motor e base. A interface não recalcula domínio."""

from __future__ import annotations

from datetime import datetime

from study.core.diagnosis import Diagnosis, Recommendation, build_diagnosis, recommend
from study.core.models import AnswerEvent, MasteryPolicy, QuestionRef, TopicStats, confidence, learning_state
from study.core.norms import exam_rules_snapshot, norm_warning
from study.core.selection import select_daily, select_exam
from study.courses.cnh.loader import bank_gaps, load_cnh_catalog, load_exam_config
from study.courses.english.adapter import build_english_catalog
from study.courses.model import Catalog, Question
from study.persistence.exchange import apply_import, dumps, export_course, loads, preview_import
from study.persistence.store import Store, StoreError
from study.reporting import render_markdown


class LessonRequired(StoreError):
    def __init__(self, module_id: str, title: str):
        super().__init__(f"A lição «{title}» ainda não foi concluída nem dispensada.")
        self.module_id = module_id
        self.title = title


class Platform:
    def __init__(self, store: Store):
        self.store = store

    def now(self) -> datetime:
        return datetime.now().astimezone()

    def policy(self) -> MasteryPolicy:
        return self.store.policy()

    def catalog(self, course_id: str) -> Catalog:
        if course_id == "english":
            return build_english_catalog()
        if course_id == "cnh-al":
            return load_cnh_catalog()
        raise StoreError("Curso desconhecido.")

    def active_course(self) -> str:
        return self.store.get_setting("active_course")

    def set_active_course(self, course_id: str) -> None:
        if course_id not in {"english", "cnh-al"}:
            raise StoreError("Curso desconhecido.")
        self.store.set_setting("active_course", course_id)

    def course_view(self, course_id: str) -> dict:
        catalog = self.catalog(course_id)
        stats = self.store.topic_stats(course_id)
        queue = self.store.review_queue(course_id)
        lessons = self.store.lesson_status(course_id)
        policy = self.policy()
        pending = [item for item in queue if item.active and item.reason == "error"]
        topics = []
        mastered = 0
        with_questions = 0
        for module in catalog.modules:
            for topic in module.topics:
                if not topic.questions:
                    continue
                with_questions += 1
                row = stats.get(topic.id, TopicStats(course_id, topic.id))
                pending_topic = sum(1 for item in pending if item.topic_id == topic.id)
                state = learning_state(row, pending_topic, policy)
                if state == "dominado":
                    mastered += 1
                topics.append(
                    {
                        "module_id": module.id,
                        "module_title": module.title,
                        "topic_id": topic.id,
                        "name": topic.name,
                        "state": state,
                        "attempts": row.attempts,
                        "correct": row.correct,
                        "incorrect": row.incorrect,
                        "accuracy": row.accuracy,
                        "consecutive_correct": row.consecutive_correct,
                        "last_studied_at": row.last_studied_at,
                        "next_review_at": row.next_review_at,
                        "pending": pending_topic,
                        "flagged": sum(1 for item in self.store.flagged(course_id) if item["topic_id"] == topic.id),
                        "confidence": confidence(row, pending_topic, policy),
                        "question_count": len(topic.questions),
                    }
                )
        sessions = self.store.sessions(course_id)
        last = next((session for session in sessions if session["status"] == "completed"), None)
        active = self.store.active_session(course_id)
        return {
            "catalog": catalog,
            "topics": topics,
            "mastered": mastered,
            "topic_count": with_questions,
            "mastery_ratio": (mastered / with_questions) if with_questions else None,
            "pending": pending,
            "flagged": self.store.flagged(course_id),
            "lessons": lessons,
            "seconds": self.store.study_seconds(course_id),
            "streak": self.store.streak(course_id, self.now()),
            "last_session": last,
            "active_session": active,
            "recommendation": self.recommendation(course_id),
            "exam_gaps": bank_gaps(catalog) if course_id == "cnh-al" else [],
            "norm_warnings": self.norm_warnings(catalog),
        }

    def recommendation(self, course_id: str, *, ignore_active: bool = False) -> Recommendation:
        catalog = self.catalog(course_id)
        stats = self.store.topic_stats(course_id)
        queue = self.store.review_queue(course_id, active_only=True)
        lessons = self.store.lesson_status(course_id)
        gaps = bank_gaps(catalog) if course_id == "cnh-al" else []
        ready = course_id == "cnh-al" and not gaps and self._exam_lessons_open(catalog, lessons)
        return recommend(
            course_id=course_id,
            course_title=catalog.title,
            modules=catalog.summaries(),
            stats_by_topic=stats,
            queue=queue,
            lesson_status=lessons,
            active_session=None if ignore_active else self.store.active_session(course_id),
            question_count=len([question for question in catalog.questions() if question.exercise_type == "mcq"]),
            exam_ready=ready,
            policy=self.policy(),
        )

    def norm_warnings(self, catalog: Catalog) -> list[dict]:
        found = []
        for question in catalog.questions():
            message = norm_warning(question.review_status, question.last_verified_at, today=self.now().date())
            if message:
                found.append({"question_id": question.id, "message": message})
        return found

    def set_lesson(self, course_id: str, module_id: str, status: str) -> None:
        self.store.set_lesson_status(course_id, module_id, status, self.now())

    def toggle_flag(self, course_id: str, question_id: str, topic_id: str) -> bool:
        flagged = not self.store.is_flagged(course_id, question_id)
        self.store.set_flag(course_id, question_id, topic_id, flagged, self.now())
        return flagged

    def start_daily(self, course_id: str) -> dict:
        catalog = self.catalog(course_id)
        self._abandon_other_in_progress(course_id)
        allowed = self._questions_after_lesson(catalog, course_id)
        count = int(self.store.get_setting("daily_question_count"))
        count = min(15, max(10, count))
        picked = select_daily(
            [question.ref() for question in allowed],
            self.store.topic_stats(course_id),
            self.store.review_queue(course_id, active_only=True),
            self.store.recent_question_ids(course_id),
            count=count,
            now=self.now(),
            policy=self.policy(),
            answer_counts=self.store.answer_counts(course_id),
        )
        if not picked:
            raise StoreError(self._empty_reason(catalog, course_id))
        return self.store.create_session(
            course_id,
            "diária",
            [item.question_id for item in picked],
            self.now(),
            {"reveal": True, "duration_minutes": 45},
        )

    def start_study(self, course_id: str, module_id: str | None = None, topic_id: str | None = None) -> dict:
        catalog = self.catalog(course_id)
        if module_id:
            self._require_lesson(catalog, course_id, module_id)
        self._abandon_other_in_progress(course_id)
        questions = [
            question for question in catalog.questions()
            if question.exercise_type == "mcq"
            and (module_id is None or question.module_id == module_id)
            and (topic_id is None or question.topic_id == topic_id)
        ]
        if module_id is None:
            questions = [question for question in questions if self._lesson_open(catalog, course_id, question.module_id)]
        questions.sort(key=lambda question: (question.difficulty, question.id))
        if not questions:
            raise StoreError(self._empty_reason(catalog, course_id))
        return self.store.create_session(
            course_id,
            "estudo",
            [question.id for question in questions],
            self.now(),
            {"reveal": True, "duration_minutes": 45, "module_id": module_id, "topic_id": topic_id},
        )

    def start_review(self, course_id: str, mode: str, topic_id: str | None = None) -> dict:
        catalog = self.catalog(course_id)
        self._abandon_other_in_progress(course_id)
        ids = self._review_ids(course_id, mode, topic_id)
        known = [question_id for question_id in ids if catalog.get(question_id)]
        if not known:
            raise StoreError("Não há questões nessa revisão.")
        return self.store.create_session(
            course_id,
            "revisão",
            known,
            self.now(),
            {"reveal": True, "duration_minutes": 45, "review_mode": mode, "topic_id": topic_id},
        )

    def start_exam(self, course_id: str) -> dict:
        if course_id != "cnh-al":
            raise StoreError("O simulado no formato do exame está no curso de CNH.")
        catalog = self.catalog(course_id)
        lessons = self.store.lesson_status(course_id)
        blocked = [
            module
            for module in catalog.modules
            if module.id in load_exam_config()["distribution"]["modules"]
            and lessons.get(module.id) not in {"completed", "skipped"}
        ]
        if blocked:
            raise LessonRequired(blocked[0].id, blocked[0].title)
        gaps = bank_gaps(catalog)
        if gaps:
            raise StoreError("O simulado não foi montado. " + " ".join(gaps))
        self._abandon_other_in_progress(course_id)
        config = load_exam_config()
        extended = self.store.get_setting("exam_extended_time") == "1"
        minutes = config["extendedDurationMinutes"] if extended else config["durationMinutes"]
        questions = [
            question.ref()
            for question in catalog.questions()
            if question.module_id in config["distribution"]["modules"] and question.exercise_type == "mcq"
        ]
        picked = select_exam(questions, config["distribution"]["modules"])
        return self.store.create_session(
            course_id,
            "simulado",
            [item.question_id for item in picked],
            self.now(),
            {
                "reveal": False,
                "duration_minutes": minutes,
                "extended": extended,
                "passing_score": config["passingScore"],
                "rules": exam_rules_snapshot(config),
            },
        )

    def submit(self, session_id: int, choice_index: int) -> dict:
        session = self._open_session(session_id)
        catalog = self.catalog(session["course_id"])
        question = self._current_question(session, catalog)
        if choice_index < 0 or choice_index >= len(question.choices):
            raise StoreError("Escolha uma alternativa.")
        chosen = question.choices[choice_index]
        correct = choice_index == question.correct_index
        payload = {
            "question_id": question.id,
            "topic_id": question.topic_id,
            "module_id": question.module_id,
            "question_text": question.prompt,
            "chosen_answer": chosen.text,
            "correct_answer": question.correct_text,
            "is_correct": correct,
            "recognition_key": question.recognition_key,
            "source": question.source,
            "source_url": question.source_url,
            "origin": question.origin,
            "review_status": question.review_status,
            "warning": norm_warning(question.review_status, question.last_verified_at, today=self.now().date()),
            "explanations": [{"text": choice.text, "explanation": choice.explanation, "correct": index == question.correct_index} for index, choice in enumerate(question.choices)],
        }
        answers = list(session["answers"])
        answers.append(payload)
        nxt = session["current_index"] + 1
        self.store.save_session(session_id, current_index=nxt, answers=answers)
        if session["config"].get("reveal", True):
            self.store.record_answer(
                AnswerEvent(
                    course_id=session["course_id"],
                    question_id=question.id,
                    topic_id=question.topic_id,
                    module_id=question.module_id,
                    chosen_answer=chosen.text,
                    correct_answer=question.correct_text,
                    is_correct=correct,
                    mode=session["kind"],
                    answered_at=self.now(),
                    question_text=question.prompt,
                    counts_as_evidence=question.counts_as_evidence,
                    session_id=session_id,
                )
            )
        finished = None
        if nxt >= len(session["question_ids"]) and session["config"].get("reveal", True):
            finished = self._close_revealed(session_id)
        return {"feedback": payload, "finished": finished, "awaiting_delivery": nxt >= len(session["question_ids"]) and not session["config"].get("reveal", True)}

    def save_sentence(self, session_id: int, question_id: str, sentence: str) -> None:
        session = self.store.get_session(session_id)
        if session is None:
            raise StoreError("Sessão inexistente.")
        question = self.catalog(session["course_id"]).get(question_id)
        if question is None:
            raise StoreError("Questão inexistente.")
        text = sentence.strip()
        if not text:
            raise StoreError("Escreva a frase antes de guardar.")
        self.store.record_note(
            AnswerEvent(
                course_id=session["course_id"],
                question_id=question.id,
                topic_id=question.topic_id,
                module_id=question.module_id,
                chosen_answer=text,
                correct_answer="Sem gabarito automático. A frase não foi corrigida.",
                is_correct=False,
                mode="production",
                answered_at=self.now(),
                question_text=question.prompt,
                counts_as_evidence=False,
                session_id=session_id,
            )
        )

    def deliver_exam(self, session_id: int) -> dict:
        session = self._open_session(session_id)
        if session["config"].get("reveal", True):
            raise StoreError("Esta sessão já mostra o gabarito durante a prática.")
        catalog = self.catalog(session["course_id"])
        answers = list(session["answers"])
        seen = {item["question_id"] for item in answers}
        for question_id in session["question_ids"]:
            if question_id in seen:
                continue
            question = catalog.get(question_id)
            if question is None:
                continue
            answers.append(
                {
                    "question_id": question.id,
                    "topic_id": question.topic_id,
                    "module_id": question.module_id,
                    "question_text": question.prompt,
                    "chosen_answer": "(não respondida)",
                    "correct_answer": question.correct_text,
                    "is_correct": False,
                    "recognition_key": question.recognition_key,
                    "source": question.source,
                    "source_url": question.source_url,
                    "origin": question.origin,
                    "review_status": question.review_status,
                    "warning": norm_warning(question.review_status, question.last_verified_at, today=self.now().date()),
                    "explanations": [
                        {"text": choice.text, "explanation": choice.explanation, "correct": index == question.correct_index}
                        for index, choice in enumerate(question.choices)
                    ],
                }
            )
        self.store.save_session(session_id, current_index=len(session["question_ids"]), answers=answers)
        now = self.now()
        for payload in answers:
            self.store.record_answer(
                AnswerEvent(
                    course_id=session["course_id"],
                    question_id=payload["question_id"],
                    topic_id=payload["topic_id"],
                    module_id=payload["module_id"],
                    chosen_answer=payload["chosen_answer"],
                    correct_answer=payload["correct_answer"],
                    is_correct=payload["is_correct"],
                    mode="simulado",
                    answered_at=now,
                    question_text=payload["question_text"],
                    session_id=session_id,
                )
            )
        return self._close_revealed(session_id)

    def abandon(self, session_id: int) -> None:
        self.store.abandon_session(session_id, self.now())

    def remaining_seconds(self, session: dict) -> int | None:
        if session["kind"] != "simulado":
            return None
        started = datetime.fromisoformat(session["started_at"])
        if started.tzinfo is None:
            started = started.replace(tzinfo=self.now().tzinfo)
        elapsed = (self.now() - started).total_seconds()
        total = int(session["config"].get("duration_minutes", 60)) * 60
        return max(0, int(total - elapsed))

    def export_json(self, course_id: str) -> str:
        recommendation = self.recommendation(course_id)
        payload = export_course(
            self.store,
            course_id,
            {"action": recommendation.action, "summary": recommendation.summary},
            self.now(),
        )
        return dumps(payload)

    def export_markdown(self, course_id: str) -> str:
        catalog = self.catalog(course_id)
        view = self.course_view(course_id)
        answers = self.store.answers(course_id)
        by_question = {}
        for row in answers:
            by_question[row["question_id"]] = row
        pending = []
        for item in view["pending"]:
            last = by_question.get(item.question_id, {})
            question = catalog.get(item.question_id)
            explanation = ""
            if question is not None:
                chosen = last.get("chosen_answer")
                match = next((choice for choice in question.choices if choice.text == chosen), None)
                explanation = match.explanation if match else question.recognition_key
            pending.append(
                {
                    "question_id": item.question_id,
                    "topic_id": item.topic_id,
                    "consecutive_correct": item.consecutive_correct,
                    "question_text": last.get("question_text") or (question.prompt if question else ""),
                    "chosen_answer": last.get("chosen_answer"),
                    "correct_answer": last.get("correct_answer"),
                    "explanation": explanation,
                }
            )
        modules = []
        for module in catalog.modules:
            modules.append(
                {
                    "title": module.title,
                    "question_count": module.question_count,
                    "lesson_status": view["lessons"].get(module.id, "not_started"),
                    "topics": [{"id": topic.id, "name": topic.name} for topic in module.topics],
                }
            )
        return render_markdown(
            course_title=catalog.title,
            course_id=course_id,
            exported_at=self.now().isoformat(timespec="seconds"),
            modules=modules,
            stats_by_topic=self.store.topic_stats(course_id),
            pending_errors=pending,
            flagged=view["flagged"],
            recent_answers=list(reversed(answers[-40:])),
            sessions=self.store.sessions(course_id),
            recommendation=view["recommendation"],
            policy=self.policy(),
            disclaimer=catalog.disclaimer,
        )

    def preview(self, text: str) -> dict:
        return preview_import(loads(text))

    def restore(self, text: str) -> dict:
        return apply_import(self.store, loads(text))

    def grade_card(self, course_id: str, card_id: str, grade: str):
        return self.store.grade_flashcard(course_id, card_id, grade, self.now())

    def _close_revealed(self, session_id: int) -> dict:
        session = self.store.get_session(session_id)
        if session is None:
            raise StoreError("Sessão inexistente.")
        catalog = self.catalog(session["course_id"])
        previous = self.store.previous_completed_accuracy(session["course_id"], session["kind"], session_id)
        diagnosis = build_diagnosis(
            course_id=session["course_id"],
            session_answers=session["answers"],
            previous_accuracy=previous,
            queue=self.store.review_queue(session["course_id"], active_only=True),
            recommendation=self.recommendation(session["course_id"], ignore_active=True),
            warnings=[item["warning"] for item in session["answers"] if item.get("warning")],
        )
        result = _diagnosis_dict(diagnosis, session)
        if session["kind"] == "simulado":
            passing = int(session["config"].get("passing_score", 20))
            result["passed"] = diagnosis.correct >= passing and diagnosis.total == len(session["question_ids"])
            result["passing_score"] = passing
            result["official_format"] = session["config"].get("rules")
        self.store.complete_session(session_id, result, self.now())
        result["session_id"] = session_id
        result["catalog_title"] = catalog.title
        return result

    def _review_ids(self, course_id: str, mode: str, topic_id: str | None) -> list[str]:
        if mode == "errors":
            ids = [item.question_id for item in self.store.review_queue(course_id, active_only=True) if item.reason == "error"]
        elif mode == "flagged":
            ids = [item["question_id"] for item in self.store.flagged(course_id)]
        elif mode == "topic" and topic_id:
            catalog = self.catalog(course_id)
            topic = catalog.topic(topic_id)
            ids = [] if topic is None else [question.id for question in topic.questions if question.exercise_type == "mcq"]
        else:
            ids = []
        if topic_id and mode != "topic":
            catalog = self.catalog(course_id)
            ids = [question_id for question_id in ids if catalog.get(question_id) and catalog.get(question_id).topic_id == topic_id]
        return ids

    def _questions_after_lesson(self, catalog: Catalog, course_id: str) -> list[Question]:
        return [
            question for question in catalog.questions()
            if question.exercise_type == "mcq" and self._lesson_open(catalog, course_id, question.module_id)
        ]

    def _lesson_open(self, catalog: Catalog, course_id: str, module_id: str) -> bool:
        return self.store.lesson_status(course_id).get(module_id) in {"completed", "skipped"}

    def _require_lesson(self, catalog: Catalog, course_id: str, module_id: str) -> None:
        module = catalog.module(module_id)
        if module is None:
            raise StoreError("Módulo inexistente.")
        if not self._lesson_open(catalog, course_id, module_id):
            raise LessonRequired(module_id, module.title)

    def _exam_lessons_open(self, catalog: Catalog, lessons: dict[str, str]) -> bool:
        needed = load_exam_config()["distribution"]["modules"]
        return all(lessons.get(module_id) in {"completed", "skipped"} for module_id in needed)

    def _empty_reason(self, catalog: Catalog, course_id: str) -> str:
        if not catalog.questions():
            if course_id == "english":
                return "O caderno de inglês ainda não tem registos suficientes para montar questões de quatro alternativas."
            return "Ainda não há questões neste curso."
        return "Conclua ou dispense a lição do módulo antes das questões. Avançar sem a teoria fica registado como dispensa."

    def _abandon_other_in_progress(self, course_id: str) -> None:
        active = self.store.active_session(course_id)
        if active is not None:
            raise StoreError("Já existe uma sessão inacabada neste curso. Continue ou abandone essa sessão antes de abrir outra.")

    def _open_session(self, session_id: int) -> dict:
        session = self.store.get_session(session_id)
        if session is None or session["status"] != "in_progress":
            raise StoreError("Esta sessão não está em andamento.")
        return session

    def _current_question(self, session: dict, catalog: Catalog) -> Question:
        if session["current_index"] >= len(session["question_ids"]):
            raise StoreError("Esta sessão já não tem questão pendente.")
        question = catalog.get(session["question_ids"][session["current_index"]])
        if question is None:
            raise StoreError("A questão desta sessão não está mais no conteúdo.")
        return question


def _diagnosis_dict(diagnosis: Diagnosis, session: dict) -> dict:
    return {
        "course_id": diagnosis.course_id,
        "kind": session["kind"],
        "total": diagnosis.total,
        "correct": diagnosis.correct,
        "accuracy": diagnosis.accuracy,
        "score_label": diagnosis.score_label,
        "by_module": diagnosis.by_module,
        "by_topic": diagnosis.by_topic,
        "errors": diagnosis.errors,
        "still_in_queue": diagnosis.still_in_queue,
        "comparison": diagnosis.comparison,
        "recommendation": diagnosis.recommendation.summary,
        "recommendation_action": diagnosis.recommendation.action,
        "warnings": diagnosis.warnings,
        "answers": session["answers"],
    }
