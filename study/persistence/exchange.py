from __future__ import annotations

import json
from datetime import datetime

from study.persistence.store import COURSE_TABLES, Store, StoreError

SCHEMA_VERSION = 1
SECRET_FRAGMENTS = ("api_key", "apikey", "token", "password", "secret", "authorization", "credential")


class ImportError(StoreError):
    pass


def export_course(store: Store, course_id: str, recommendation: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now().astimezone()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "course": course_id,
        "exportedAt": now.isoformat(timespec="seconds"),
        "sessions": store.sessions(course_id),
        "answers": store.answers(course_id),
        "topicStats": [
            {
                "topicId": stats.topic_id,
                "attempts": stats.attempts,
                "correct": stats.correct,
                "incorrect": stats.incorrect,
                "consecutiveCorrect": stats.consecutive_correct,
                "lastStudiedAt": stats.last_studied_at,
                "nextReviewAt": stats.next_review_at,
                "accuracy": stats.accuracy,
            }
            for stats in store.topic_stats(course_id).values()
        ],
        "reviewQueue": [
            {
                "questionId": item.question_id,
                "topicId": item.topic_id,
                "consecutiveCorrect": item.consecutive_correct,
                "reason": item.reason,
                "active": item.active,
                "enteredAt": item.entered_at,
                "lastAttemptAt": item.last_attempt_at,
            }
            for item in store.review_queue(course_id)
        ],
        "flaggedQuestions": store.flagged(course_id),
        "lessonProgress": store.lesson_status(course_id),
        "flashcards": [
            {
                "cardId": card.card_id,
                "repetitions": card.repetitions,
                "intervalDays": card.interval_days,
                "ease": card.ease,
                "dueAt": card.due_at,
                "lastGrade": card.last_grade,
            }
            for card in store.flashcards(course_id).values()
        ],
        "studyTime": _study_time(store, course_id),
        "recommendationsContext": recommendation,
    }
    return strip_secrets(payload)


def strip_secrets(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if any(fragment in key.lower() for fragment in SECRET_FRAGMENTS):
                continue
            cleaned[key] = strip_secrets(item)
        return cleaned
    if isinstance(value, list):
        return [strip_secrets(item) for item in value]
    return value


def validate_payload(payload: dict) -> list[str]:
    problems = []
    if not isinstance(payload, dict):
        return ["O ficheiro não é um objeto JSON."]
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        problems.append(f"schemaVersion tem de ser {SCHEMA_VERSION}.")
    if payload.get("course") not in {"english", "cnh-al"}:
        problems.append("O curso do ficheiro não é english nem cnh-al.")
    if not payload.get("exportedAt"):
        problems.append("exportedAt é obrigatório.")
    for key in ("sessions", "answers", "topicStats", "reviewQueue", "flaggedQuestions"):
        if key not in payload or not isinstance(payload[key], list):
            problems.append(f"O campo {key} tem de ser uma lista.")
    for answer in payload.get("answers") or []:
        if not isinstance(answer, dict):
            problems.append("Há uma resposta que não é um objeto.")
            break
        for field in ("question_id", "topic_id", "module_id", "correct_answer", "answered_at"):
            if field not in answer and _camel(field) not in answer:
                problems.append(f"Resposta sem {field}.")
                break
    return problems


def preview_import(payload: dict) -> dict:
    problems = validate_payload(payload)
    if problems:
        raise ImportError(" ".join(problems))
    return {
        "course": payload["course"],
        "exportedAt": payload["exportedAt"],
        "sessions": len(payload["sessions"]),
        "answers": len(payload["answers"]),
        "topicStats": len(payload["topicStats"]),
        "reviewQueue": len(payload["reviewQueue"]),
        "flaggedQuestions": len(payload["flaggedQuestions"]),
        "secretsRemoved": _contained_secret(payload),
    }


def apply_import(store: Store, payload: dict) -> dict:
    summary = preview_import(payload)
    course_id = payload["course"]
    store.delete_course_progress(course_id)
    with store.connect() as conn:
        for row in payload["topicStats"]:
            conn.execute(
                """
                INSERT INTO topic_stats(
                    course_id, topic_id, attempts, correct, incorrect,
                    consecutive_correct, last_studied_at, next_review_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("topicId") or row.get("topic_id"),
                    row.get("attempts", 0),
                    row.get("correct", 0),
                    row.get("incorrect", 0),
                    row.get("consecutiveCorrect", row.get("consecutive_correct", 0)),
                    row.get("lastStudiedAt", row.get("last_studied_at")),
                    row.get("nextReviewAt", row.get("next_review_at")),
                ),
            )
        for row in payload["reviewQueue"]:
            conn.execute(
                """
                INSERT INTO review_queue(
                    course_id, question_id, topic_id, consecutive_correct,
                    reason, active, entered_at, last_attempt_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("questionId") or row.get("question_id"),
                    row.get("topicId") or row.get("topic_id"),
                    row.get("consecutiveCorrect", row.get("consecutive_correct", 0)),
                    row.get("reason", "error"),
                    1 if row.get("active", True) else 0,
                    row.get("enteredAt") or row.get("entered_at") or payload["exportedAt"],
                    row.get("lastAttemptAt", row.get("last_attempt_at")),
                ),
            )
        for row in payload["flaggedQuestions"]:
            conn.execute(
                """
                INSERT INTO flagged_questions(course_id, question_id, topic_id, flagged_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("question_id") or row.get("questionId"),
                    row.get("topic_id") or row.get("topicId") or "",
                    row.get("flagged_at") or row.get("flaggedAt") or payload["exportedAt"],
                ),
            )
        for row in payload["answers"]:
            conn.execute(
                """
                INSERT INTO answers(
                    course_id, session_id, question_id, topic_id, module_id,
                    question_text, chosen_answer, correct_answer, is_correct,
                    mode, counts_as_evidence, answered_at
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("question_id") or row.get("questionId"),
                    row.get("topic_id") or row.get("topicId"),
                    row.get("module_id") or row.get("moduleId"),
                    row.get("question_text") or row.get("questionText"),
                    row.get("chosen_answer") if "chosen_answer" in row else row.get("chosenAnswer"),
                    row.get("correct_answer") or row.get("correctAnswer"),
                    1 if row.get("is_correct", row.get("isCorrect")) else 0,
                    row.get("mode") or "import",
                    1 if row.get("counts_as_evidence", row.get("countsAsEvidence", 1)) else 0,
                    row.get("answered_at") or row.get("answeredAt"),
                ),
            )
        for row in payload["sessions"]:
            conn.execute(
                """
                INSERT INTO sessions(
                    course_id, kind, status, started_at, finished_at, config_json,
                    question_ids_json, current_index, answers_json, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("kind") or "study",
                    row.get("status") or "completed",
                    row.get("started_at") or row.get("startedAt") or payload["exportedAt"],
                    row.get("finished_at") or row.get("finishedAt"),
                    json.dumps(row.get("config") or {}, ensure_ascii=False),
                    json.dumps(row.get("question_ids") or row.get("questionIds") or []),
                    row.get("current_index") or row.get("currentIndex") or 0,
                    json.dumps(row.get("answers") or [], ensure_ascii=False),
                    json.dumps(row.get("result"), ensure_ascii=False) if row.get("result") else None,
                ),
            )
        lessons = payload.get("lessonProgress") or {}
        if isinstance(lessons, dict):
            for module_id, status in lessons.items():
                conn.execute(
                    """
                    INSERT INTO lesson_progress(course_id, module_id, status, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (course_id, module_id, status, payload["exportedAt"]),
                )
        for row in payload.get("flashcards") or []:
            conn.execute(
                """
                INSERT INTO flashcard_progress(
                    course_id, card_id, repetitions, interval_days, ease, due_at, last_grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row.get("cardId") or row.get("card_id"),
                    row.get("repetitions", 0),
                    row.get("intervalDays", row.get("interval_days", 0)),
                    row.get("ease", 2.5),
                    row.get("dueAt", row.get("due_at")),
                    row.get("lastGrade", row.get("last_grade")),
                ),
            )
        for row in payload.get("studyTime") or []:
            conn.execute(
                """
                INSERT INTO study_time(course_id, day, seconds) VALUES (?, ?, ?)
                """,
                (course_id, row["day"], row["seconds"]),
            )
    summary["replaced"] = True
    summary["untouchedTables"] = [table for table in COURSE_TABLES if table]
    return summary


def dumps(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def loads(text: str) -> dict:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ImportError(f"JSON inválido: {exc}") from exc
    if not isinstance(payload, dict):
        raise ImportError("O ficheiro JSON tem de ser um objeto.")
    return payload


def _study_time(store: Store, course_id: str) -> list[dict]:
    with store.connect() as conn:
        rows = conn.execute(
            "SELECT day, seconds FROM study_time WHERE course_id = ? ORDER BY day",
            (course_id,),
        ).fetchall()
    return [{"day": row["day"], "seconds": row["seconds"]} for row in rows]


def _camel(field: str) -> str:
    parts = field.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def _contained_secret(payload: dict) -> bool:
    raw = json.dumps(payload).lower()
    return any(fragment in raw for fragment in SECRET_FRAGMENTS)
