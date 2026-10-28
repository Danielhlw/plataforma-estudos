"""Armazenamento local da plataforma. O vocabulário continua no word_bank.db."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from study.core.engine import apply_answer
from study.core.flashcards import CardProgress, grade_card
from study.core.models import AnswerEvent, AppliedAnswer, MasteryPolicy, ReviewItem, TopicStats
from study.persistence.schema import SCHEMA

DEFAULTS = {
    "daily_question_count": "12",
    "mastery_threshold": "0.8",
    "min_evidence": "5",
    "consecutive_to_clear": "2",
    "active_course": "english",
    "exam_extended_time": "0",
}

COURSE_TABLES = (
    "topic_stats",
    "review_queue",
    "flagged_questions",
    "answers",
    "sessions",
    "lesson_progress",
    "flashcard_progress",
    "study_time",
)


class StoreError(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.connect() as conn:
                conn.executescript(SCHEMA)
                for key, value in DEFAULTS.items():
                    conn.execute(
                        "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                        (key, value),
                    )
        except sqlite3.Error as exc:
            raise StoreError(f"Não foi possível preparar a base local: {exc}") from exc

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def policy(self) -> MasteryPolicy:
        return MasteryPolicy(
            threshold=float(self.get_setting("mastery_threshold")),
            min_evidence=int(self.get_setting("min_evidence")),
            consecutive_to_clear=int(self.get_setting("consecutive_to_clear")),
        )

    def get_setting(self, key: str) -> str:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            if key not in DEFAULTS:
                raise StoreError(f"Configuração desconhecida: {key}")
            return DEFAULTS[key]
        return row["value"]

    def set_setting(self, key: str, value: str) -> None:
        if key not in DEFAULTS:
            raise StoreError(f"Configuração desconhecida: {key}")
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def topic_stats(self, course_id: str) -> dict[str, TopicStats]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM topic_stats WHERE course_id = ?",
                (course_id,),
            ).fetchall()
        return {row["topic_id"]: _stats(row) for row in rows}

    def review_queue(self, course_id: str, *, active_only: bool = False) -> list[ReviewItem]:
        sql = "SELECT * FROM review_queue WHERE course_id = ?"
        if active_only:
            sql += " AND active = 1"
        sql += " ORDER BY last_attempt_at DESC, entered_at DESC"
        with self.connect() as conn:
            rows = conn.execute(sql, (course_id,)).fetchall()
        return [_review(row) for row in rows]

    def flagged(self, course_id: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM flagged_questions WHERE course_id = ? ORDER BY flagged_at DESC",
                (course_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def is_flagged(self, course_id: str, question_id: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM flagged_questions WHERE course_id = ? AND question_id = ?",
                (course_id, question_id),
            ).fetchone()
        return row is not None

    def set_flag(self, course_id: str, question_id: str, topic_id: str, flagged: bool, now: datetime) -> None:
        with self.connect() as conn:
            if flagged:
                conn.execute(
                    """
                    INSERT INTO flagged_questions(course_id, question_id, topic_id, flagged_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(course_id, question_id) DO UPDATE SET
                        topic_id = excluded.topic_id,
                        flagged_at = excluded.flagged_at
                    """,
                    (course_id, question_id, topic_id, now.isoformat(timespec="seconds")),
                )
            else:
                conn.execute(
                    "DELETE FROM flagged_questions WHERE course_id = ? AND question_id = ?",
                    (course_id, question_id),
                )

    def lesson_status(self, course_id: str) -> dict[str, str]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT module_id, status FROM lesson_progress WHERE course_id = ?",
                (course_id,),
            ).fetchall()
        return {row["module_id"]: row["status"] for row in rows}

    def set_lesson_status(self, course_id: str, module_id: str, status: str, now: datetime) -> None:
        if status not in {"not_started", "completed", "skipped"}:
            raise StoreError("Estado de lição inválido.")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO lesson_progress(course_id, module_id, status, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(course_id, module_id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (course_id, module_id, status, now.isoformat(timespec="seconds")),
            )

    def record_answer(self, event: AnswerEvent) -> AppliedAnswer:
        policy = self.policy()
        try:
            with self.connect() as conn:
                stats_row = conn.execute(
                    "SELECT * FROM topic_stats WHERE course_id = ? AND topic_id = ?",
                    (event.course_id, event.topic_id),
                ).fetchone()
                review_row = conn.execute(
                    "SELECT * FROM review_queue WHERE course_id = ? AND question_id = ?",
                    (event.course_id, event.question_id),
                ).fetchone()
                stats = _stats(stats_row) if stats_row else TopicStats(event.course_id, event.topic_id)
                review = _review(review_row) if review_row else None
                applied = apply_answer(
                    stats,
                    review,
                    correct=event.is_correct,
                    question_id=event.question_id,
                    now=event.answered_at,
                    policy=policy,
                    counts_as_evidence=event.counts_as_evidence,
                )
                _save_stats(conn, applied.stats)
                if applied.review is not None:
                    _save_review(conn, applied.review)
                conn.execute(
                    """
                    INSERT INTO answers(
                        course_id, session_id, question_id, topic_id, module_id,
                        question_text, chosen_answer, correct_answer, is_correct,
                        mode, counts_as_evidence, answered_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.course_id,
                        event.session_id,
                        event.question_id,
                        event.topic_id,
                        event.module_id,
                        event.question_text,
                        event.chosen_answer,
                        event.correct_answer,
                        1 if event.is_correct else 0,
                        event.mode,
                        1 if event.counts_as_evidence else 0,
                        event.answered_at.isoformat(timespec="seconds"),
                    ),
                )
            return applied
        except sqlite3.Error as exc:
            raise StoreError(f"Não foi possível gravar a resposta: {exc}") from exc

    def record_note(self, event: AnswerEvent) -> None:
        """Guarda uma frase produzida sem alterar domínio nem fila."""
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO answers(
                        course_id, session_id, question_id, topic_id, module_id,
                        question_text, chosen_answer, correct_answer, is_correct,
                        mode, counts_as_evidence, answered_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 'production', 0, ?)
                    """,
                    (
                        event.course_id,
                        event.session_id,
                        event.question_id,
                        event.topic_id,
                        event.module_id,
                        event.question_text,
                        event.chosen_answer,
                        event.correct_answer,
                        event.answered_at.isoformat(timespec="seconds"),
                    ),
                )
        except sqlite3.Error as exc:
            raise StoreError(f"Não foi possível guardar a frase: {exc}") from exc

    def recent_question_ids(self, course_id: str, limit: int = 30) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT question_id FROM answers
                WHERE course_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (course_id, limit),
            ).fetchall()
        return [row["question_id"] for row in rows]

    def answer_counts(self, course_id: str) -> dict[str, int]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT question_id, COUNT(*) AS n FROM answers
                WHERE course_id = ?
                GROUP BY question_id
                """,
                (course_id,),
            ).fetchall()
        return {row["question_id"]: row["n"] for row in rows}

    def answers(self, course_id: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM answers WHERE course_id = ? ORDER BY id",
                (course_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_session(
        self,
        course_id: str,
        kind: str,
        question_ids: list[str],
        now: datetime,
        config: dict | None = None,
    ) -> dict:
        if not question_ids:
            raise StoreError("A sessão precisa de pelo menos uma questão.")
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions(
                    course_id, kind, status, started_at, config_json, question_ids_json
                ) VALUES (?, ?, 'in_progress', ?, ?, ?)
                """,
                (
                    course_id,
                    kind,
                    now.isoformat(timespec="seconds"),
                    json.dumps(config or {}, ensure_ascii=False),
                    json.dumps(question_ids),
                ),
            )
            session_id = cursor.lastrowid
        session = self.get_session(session_id)
        if session is None:
            raise StoreError("A sessão foi criada mas não pôde ser lida.")
        return session

    def get_session(self, session_id: int) -> dict | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return _session(row) if row else None

    def active_session(self, course_id: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM sessions
                WHERE course_id = ? AND status = 'in_progress'
                ORDER BY id DESC
                LIMIT 1
                """,
                (course_id,),
            ).fetchone()
        return _session(row) if row else None

    def save_session(self, session_id: int, *, current_index: int, answers: list[dict]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET current_index = ?, answers_json = ?
                WHERE id = ? AND status = 'in_progress'
                """,
                (current_index, json.dumps(answers, ensure_ascii=False), session_id),
            )

    def complete_session(self, session_id: int, result: dict, now: datetime) -> dict:
        session = self.get_session(session_id)
        if session is None:
            raise StoreError("Sessão inexistente.")
        started = datetime.fromisoformat(session["started_at"])
        delta = max(0, int((now - started).total_seconds()))
        cap = int(session["config"].get("duration_minutes", 45)) * 60
        credited = min(delta, cap)
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET status = 'completed', finished_at = ?, result_json = ?
                WHERE id = ?
                """,
                (now.isoformat(timespec="seconds"), json.dumps(result, ensure_ascii=False), session_id),
            )
            if credited:
                day = now.date().isoformat()
                conn.execute(
                    """
                    INSERT INTO study_time(course_id, day, seconds) VALUES (?, ?, ?)
                    ON CONFLICT(course_id, day) DO UPDATE SET seconds = seconds + excluded.seconds
                    """,
                    (session["course_id"], day, credited),
                )
        updated = self.get_session(session_id)
        if updated is None:
            raise StoreError("Não foi possível reler a sessão concluída.")
        return updated

    def abandon_session(self, session_id: int, now: datetime) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET status = 'abandoned', finished_at = ?
                WHERE id = ? AND status = 'in_progress'
                """,
                (now.isoformat(timespec="seconds"), session_id),
            )

    def sessions(self, course_id: str | None = None) -> list[dict]:
        sql = "SELECT * FROM sessions"
        params: tuple = ()
        if course_id:
            sql += " WHERE course_id = ?"
            params = (course_id,)
        sql += " ORDER BY id DESC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_session(row) for row in rows]

    def previous_completed_accuracy(self, course_id: str, kind: str, before_id: int) -> float | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT result_json FROM sessions
                WHERE course_id = ? AND kind = ? AND status = 'completed' AND id < ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (course_id, kind, before_id),
            ).fetchone()
        if row is None or not row["result_json"]:
            return None
        payload = json.loads(row["result_json"])
        return payload.get("accuracy")

    def study_seconds(self, course_id: str | None = None) -> int:
        sql = "SELECT COALESCE(SUM(seconds), 0) AS total FROM study_time"
        params: tuple = ()
        if course_id:
            sql += " WHERE course_id = ?"
            params = (course_id,)
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone()
        return int(row["total"])

    def streak(self, course_id: str, today: datetime | None = None) -> int:
        today = today or datetime.now().astimezone()
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT day FROM study_time WHERE course_id = ? AND seconds > 0",
                (course_id,),
            ).fetchall()
        days = {row["day"] for row in rows}
        if not days:
            return 0
        cursor = today.date()
        if cursor.isoformat() not in days:
            cursor = cursor - timedelta(days=1)
            if cursor.isoformat() not in days:
                return 0
        streak = 0
        while cursor.isoformat() in days:
            streak += 1
            cursor = cursor - timedelta(days=1)
        return streak

    def flashcards(self, course_id: str) -> dict[str, CardProgress]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM flashcard_progress WHERE course_id = ?",
                (course_id,),
            ).fetchall()
        found = {}
        for row in rows:
            found[row["card_id"]] = CardProgress(
                course_id=row["course_id"],
                card_id=row["card_id"],
                repetitions=row["repetitions"],
                interval_days=row["interval_days"],
                ease=row["ease"],
                due_at=row["due_at"],
                last_grade=row["last_grade"],
            )
        return found

    def grade_flashcard(self, course_id: str, card_id: str, grade: str, now: datetime) -> CardProgress:
        current = self.flashcards(course_id).get(card_id, CardProgress(course_id, card_id))
        updated = grade_card(current, grade, now)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO flashcard_progress(
                    course_id, card_id, repetitions, interval_days, ease, due_at, last_grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(course_id, card_id) DO UPDATE SET
                    repetitions = excluded.repetitions,
                    interval_days = excluded.interval_days,
                    ease = excluded.ease,
                    due_at = excluded.due_at,
                    last_grade = excluded.last_grade
                """,
                (
                    updated.course_id,
                    updated.card_id,
                    updated.repetitions,
                    updated.interval_days,
                    updated.ease,
                    updated.due_at,
                    updated.last_grade,
                ),
            )
        return updated

    def delete_course_progress(self, course_id: str) -> None:
        with self.connect() as conn:
            for table in COURSE_TABLES:
                conn.execute(f"DELETE FROM {table} WHERE course_id = ?", (course_id,))


def _stats(row: sqlite3.Row) -> TopicStats:
    return TopicStats(
        course_id=row["course_id"],
        topic_id=row["topic_id"],
        attempts=row["attempts"],
        correct=row["correct"],
        incorrect=row["incorrect"],
        consecutive_correct=row["consecutive_correct"],
        last_studied_at=row["last_studied_at"],
        next_review_at=row["next_review_at"],
    )


def _review(row: sqlite3.Row) -> ReviewItem:
    return ReviewItem(
        course_id=row["course_id"],
        question_id=row["question_id"],
        topic_id=row["topic_id"],
        consecutive_correct=row["consecutive_correct"],
        reason=row["reason"],
        active=bool(row["active"]),
        entered_at=row["entered_at"],
        last_attempt_at=row["last_attempt_at"],
    )


def _save_stats(conn: sqlite3.Connection, stats: TopicStats) -> None:
    conn.execute(
        """
        INSERT INTO topic_stats(
            course_id, topic_id, attempts, correct, incorrect,
            consecutive_correct, last_studied_at, next_review_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id, topic_id) DO UPDATE SET
            attempts = excluded.attempts,
            correct = excluded.correct,
            incorrect = excluded.incorrect,
            consecutive_correct = excluded.consecutive_correct,
            last_studied_at = excluded.last_studied_at,
            next_review_at = excluded.next_review_at
        """,
        (
            stats.course_id,
            stats.topic_id,
            stats.attempts,
            stats.correct,
            stats.incorrect,
            stats.consecutive_correct,
            stats.last_studied_at,
            stats.next_review_at,
        ),
    )


def _save_review(conn: sqlite3.Connection, item: ReviewItem) -> None:
    conn.execute(
        """
        INSERT INTO review_queue(
            course_id, question_id, topic_id, consecutive_correct,
            reason, active, entered_at, last_attempt_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id, question_id) DO UPDATE SET
            topic_id = excluded.topic_id,
            consecutive_correct = excluded.consecutive_correct,
            reason = excluded.reason,
            active = excluded.active,
            last_attempt_at = excluded.last_attempt_at
        """,
        (
            item.course_id,
            item.question_id,
            item.topic_id,
            item.consecutive_correct,
            item.reason,
            1 if item.active else 0,
            item.entered_at,
            item.last_attempt_at,
        ),
    )


def _session(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "course_id": row["course_id"],
        "kind": row["kind"],
        "status": row["status"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "config": json.loads(row["config_json"] or "{}"),
        "question_ids": json.loads(row["question_ids_json"] or "[]"),
        "current_index": row["current_index"],
        "answers": json.loads(row["answers_json"] or "[]"),
        "result": json.loads(row["result_json"]) if row["result_json"] else None,
    }
