SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topic_stats (
    course_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    correct INTEGER NOT NULL DEFAULT 0,
    incorrect INTEGER NOT NULL DEFAULT 0,
    consecutive_correct INTEGER NOT NULL DEFAULT 0,
    last_studied_at TEXT,
    next_review_at TEXT,
    PRIMARY KEY (course_id, topic_id)
);

CREATE TABLE IF NOT EXISTS review_queue (
    course_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    consecutive_correct INTEGER NOT NULL DEFAULT 0,
    reason TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    entered_at TEXT NOT NULL,
    last_attempt_at TEXT,
    PRIMARY KEY (course_id, question_id)
);

CREATE TABLE IF NOT EXISTS flagged_questions (
    course_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    flagged_at TEXT NOT NULL,
    PRIMARY KEY (course_id, question_id)
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    session_id INTEGER,
    question_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    question_text TEXT,
    chosen_answer TEXT,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    mode TEXT NOT NULL,
    counts_as_evidence INTEGER NOT NULL DEFAULT 1,
    answered_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_answers_course ON answers(course_id, answered_at);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    config_json TEXT NOT NULL DEFAULT '{}',
    question_ids_json TEXT NOT NULL,
    current_index INTEGER NOT NULL DEFAULT 0,
    answers_json TEXT NOT NULL DEFAULT '[]',
    result_json TEXT
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    course_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (course_id, module_id)
);

CREATE TABLE IF NOT EXISTS flashcard_progress (
    course_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    repetitions INTEGER NOT NULL DEFAULT 0,
    interval_days REAL NOT NULL DEFAULT 0,
    ease REAL NOT NULL DEFAULT 2.5,
    due_at TEXT,
    last_grade TEXT,
    PRIMARY KEY (course_id, card_id)
);

CREATE TABLE IF NOT EXISTS study_time (
    course_id TEXT NOT NULL,
    day TEXT NOT NULL,
    seconds INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (course_id, day)
);
"""
