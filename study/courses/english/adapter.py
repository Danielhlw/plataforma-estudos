"""Liga o caderno word-bank ao motor, sem alterar o schema do vocabulário."""

from __future__ import annotations

import random

from study.courses.model import Catalog, Choice, Flashcard, Lesson, Module, Question, Topic


def ensure_word_bank():
    from word_bank.config import DEFAULT_XLSX
    from word_bank.db import init_db
    from word_bank.repositories import word_bank as repo
    from word_bank.services.seed import seed_from_excel

    init_db()
    if repo.is_empty() and DEFAULT_XLSX.exists():
        seed_from_excel(DEFAULT_XLSX)
    return repo


def build_english_catalog() -> Catalog:
    repo = ensure_word_bank()
    modules = [
        _vocabulary_module(
            module_id="verbs",
            title="Verbos",
            summary="Verbos regulares e formas do verbo BE gravados no caderno.",
            topic_id="verbs-recall",
            topic_name="Recordação de verbos",
            rows=_merge(repo.list_verbs(), repo.list_be_forms()),
            term_key="base",
            meaning_key="portuguese",
            table_name="verbs",
        ),
        _vocabulary_module(
            module_id="adjectives",
            title="Adjetivos",
            summary="Adjetivos gravados no caderno, com o significado que você registou.",
            topic_id="adjectives-recall",
            topic_name="Recordação de adjetivos",
            rows=repo.list_adjectives(),
            term_key="english",
            meaning_key="portuguese",
            table_name="adjectives",
        ),
        _vocabulary_module(
            module_id="nouns",
            title="Substantivos e pronomes",
            summary="Substantivos e pronomes do caderno. Os pronomes usam pessoa e forma.",
            topic_id="nouns-recall",
            topic_name="Recordação de substantivos",
            rows=_noun_rows(repo),
            term_key="term",
            meaning_key="meaning",
            table_name="nouns",
        ),
        _tense_module(repo.list_tense_examples()),
        _yesno_module(repo.list_yesno_examples()),
        _revision_module(),
    ]
    return Catalog(
        course_id="english",
        title="Inglês",
        disclaimer=(
            "Os significados e exemplos vêm do caderno local. "
            "A plataforma não inventa pronúncia nem tradução. "
            "Texto marcado como material de revisão é o que já estava no projeto word-bank."
        ),
        modules=modules,
    )


def _merge(first: list[dict], second: list[dict]) -> list[dict]:
    rows = []
    for row in first:
        item = dict(row)
        item["id"] = f"verbs-{row['id']}"
        rows.append(item)
    for row in second:
        item = dict(row)
        item["id"] = f"be-{row['id']}"
        rows.append(item)
    return rows


def _noun_rows(repo) -> list[dict]:
    rows = []
    for row in repo.list_nouns():
        rows.append(
            {
                "id": f"nouns-{row['id']}",
                "term": row.get("singular") or "",
                "meaning": row.get("portuguese") or "",
                "extra": row.get("plural") or "",
            }
        )
    for label, listing in (
        ("subject", repo.list_subject_pronouns()),
        ("object", repo.list_object_pronouns()),
        ("possessive", repo.list_possessive_pronouns()),
    ):
        for row in listing:
            rows.append(
                {
                    "id": f"{label}-{row['id']}",
                    "term": row.get("form") or "",
                    "meaning": row.get("person") or "",
                    "extra": label,
                }
            )
    return rows


def _vocabulary_module(
    *,
    module_id: str,
    title: str,
    summary: str,
    topic_id: str,
    topic_name: str,
    rows: list[dict],
    term_key: str,
    meaning_key: str,
    table_name: str,
) -> Module:
    usable = [row for row in rows if (row.get(term_key) or "").strip() and (row.get(meaning_key) or "").strip()]
    examples = [f"{row[term_key]} → {row[meaning_key]}" for row in usable[:8]]
    lesson = Lesson(
        blocks=[
            "Esta lição mostra apenas registos que já estão no seu caderno.",
            "Não há tradução automática. Se um significado estiver vazio, a palavra não entra na prática.",
        ],
        concepts=[f"{len(usable)} registo(s) com termo e significado em {title.lower()}."],
        examples=examples or ["Ainda não há pares termo/significado nesta secção."],
        comparisons=_comparisons(usable, term_key, meaning_key),
        relations=["Palavra no caderno → significado gravado → distração vinda de outro registo da mesma secção."],
        rules=[
            "Na prática, a resposta certa é o texto gravado, não um sinónimo sugerido.",
            "Se duas palavras se parecem, a explicação indica qual registo corresponde a cada alternativa.",
        ],
        pitfalls=["Confundir o significado de uma palavra com o de outra linha da mesma tabela."],
        memorize=examples[:5],
        sources=[{"title": "Caderno SQLite do word-bank", "url": ""}],
    )
    questions = _recall_questions(
        course_rows=usable,
        module_id=module_id,
        topic_id=topic_id,
        term_key=term_key,
        meaning_key=meaning_key,
        table_name=table_name,
    )
    cards = [
        Flashcard(
            id=f"english-card-{module_id}-{row['id']}",
            front=str(row[term_key]),
            back=str(row[meaning_key]),
            source=f"Caderno, {table_name}, id {row['id']}",
        )
        for row in usable[:40]
    ]
    return Module(
        id=module_id,
        title=title,
        summary=summary,
        exam_importance=0,
        topics=[Topic(id=topic_id, name=topic_name, module_id=module_id, lesson=lesson, flashcards=cards, questions=questions)],
    )


def _comparisons(rows: list[dict], term_key: str, meaning_key: str) -> list[dict[str, str]]:
    found = []
    for left, right in zip(rows, rows[1:]):
        if left[term_key][:4].lower() == right[term_key][:4].lower() and left[term_key] != right[term_key]:
            found.append(
                {
                    "left": f"{left[term_key]} = {left[meaning_key]}",
                    "right": f"{right[term_key]} = {right[meaning_key]}",
                    "difference": "São registos diferentes do caderno. A prática pede o par que foi gravado.",
                }
            )
        if len(found) == 4:
            break
    return found


def _recall_questions(
    *,
    course_rows: list[dict],
    module_id: str,
    topic_id: str,
    term_key: str,
    meaning_key: str,
    table_name: str,
) -> list[Question]:
    questions: list[Question] = []
    meanings = [(str(row[meaning_key]).strip(), str(row[term_key]).strip(), row["id"]) for row in course_rows]
    terms = [(str(row[term_key]).strip(), str(row[meaning_key]).strip(), row["id"]) for row in course_rows]
    for meaning, term, row_id in meanings:
        built = _build_mcq(
            question_id=f"english:{table_name}:{row_id}:to-meaning",
            module_id=module_id,
            topic_id=topic_id,
            prompt=f"Qual é o significado gravado no caderno para «{term}»?",
            correct=meaning,
            pool=[(item[0], item[1]) for item in meanings if item[2] != row_id],
            recognition=f"Palavra «{term}» → significado gravado «{meaning}».",
            source=f"Caderno word-bank, tabela {table_name}, id {row_id}",
            difficulty=1,
        )
        if built:
            questions.append(built)
        reverse = _build_mcq(
            question_id=f"english:{table_name}:{row_id}:to-term",
            module_id=module_id,
            topic_id=topic_id,
            prompt=f"Qual palavra do caderno está gravada com o significado «{meaning}»?",
            correct=term,
            pool=[(item[0], item[1]) for item in terms if item[2] != row_id],
            recognition=f"Significado «{meaning}» → palavra gravada «{term}».",
            source=f"Caderno word-bank, tabela {table_name}, id {row_id}",
            difficulty=2,
        )
        if reverse:
            questions.append(reverse)
    return questions


def _tense_module(rows: list[dict]) -> Module:
    complete = [
        row for row in rows
        if all(row.get(column) for column in ("simple_present", "present_continuous", "simple_past", "simple_future"))
    ]
    examples = []
    questions: list[Question] = []
    for row in complete:
        number = row.get("number") or row["id"]
        examples.append(f"#{number}: {row['simple_past']}")
        options = [
            ("simple_present", row["simple_present"]),
            ("present_continuous", row["present_continuous"]),
            ("simple_past", row["simple_past"]),
            ("simple_future", row["simple_future"]),
        ]
        correct = row["simple_past"]
        choice_rows = []
        ordered = _order_texts([text for _, text in options], f"tense-{row['id']}")
        labels = {text: name for name, text in options}
        for text in ordered:
            column = labels[text]
            if text == correct:
                explanation = "Esta frase está na coluna Simple Past deste exemplo do caderno."
            else:
                explanation = (
                    f"Esta frase está na coluna {column} do mesmo exemplo, não em Simple Past. "
                    "O tempo pedido no enunciado é outro."
                )
            choice_rows.append(Choice(text=text, explanation=explanation))
        questions.append(
            Question(
                id=f"english:tense:{row['id']}:simple-past",
                course_id="english",
                module_id="tense",
                topic_id="tense-forms",
                prompt=f"No exemplo nº {number} do caderno, qual frase está gravada como Simple Past?",
                choices=choice_rows,
                correct_index=ordered.index(correct),
                recognition_key="O enunciado pede a coluna Simple Past deste conjunto, não uma frase parecida de outro tempo.",
                difficulty=2,
                source=f"Caderno word-bank, tense_examples, id {row['id']}",
                review_status="caderno",
                origin="caderno",
            )
        )
    lesson = Lesson(
        blocks=["Cada linha do caderno guarda a mesma ideia em tempos diferentes.", "A prática pede a coluna nomeada, usando só o texto gravado."],
        concepts=["Simple Present, Present Continuous, Simple Past e Simple Future, quando os quatro campos existem."],
        examples=examples[:6] or ["Ainda não há exemplos com os quatro tempos preenchidos."],
        rules=["Leia o nome do tempo no enunciado antes de escolher a frase."],
        pitfalls=["Escolher uma frase correta em inglês, mas do tempo errado."],
        memorize=["O rótulo do tempo é o critério, não só o vocabulário da frase."],
        sources=[{"title": "Caderno SQLite, tabela tense_examples", "url": ""}],
    )
    return Module(
        id="tense",
        title="Tempos verbais",
        summary="Frases já gravadas nos tempos do caderno.",
        topics=[
            Topic(
                id="tense-forms",
                name="Identificar o tempo gravado",
                module_id="tense",
                lesson=lesson,
                flashcards=[
                    Flashcard(
                        id=f"english-card-tense-{row['id']}",
                        front=f"Simple Past do exemplo {row.get('number') or row['id']}",
                        back=row["simple_past"],
                        source="tense_examples",
                    )
                    for row in complete[:20]
                ],
                questions=questions,
            )
        ],
    )


def _yesno_module(rows: list[dict]) -> Module:
    usable = [row for row in rows if row.get("situation") and row.get("yesno_question")]
    pool = [(row["yesno_question"], row["situation"], row["id"]) for row in usable]
    questions = []
    for question_text, situation, row_id in pool:
        built = _build_mcq(
            question_id=f"english:yesno:{row_id}:question",
            module_id="yesno",
            topic_id="yesno-match",
            prompt=f"Qual pergunta Yes/No está gravada para a situação «{situation}»?",
            correct=question_text,
            pool=[(item[0], item[1]) for item in pool if item[2] != row_id],
            recognition=f"Situação «{situation}» → pergunta gravada «{question_text}».",
            source=f"Caderno word-bank, yesno_examples, id {row_id}",
            difficulty=2,
        )
        if built:
            questions.append(built)
    lesson = Lesson(
        blocks=["A situação e a pergunta Yes/No vêm da mesma linha do caderno."],
        concepts=[f"{len(usable)} situação(ões) com pergunta Yes/No."],
        examples=[f"{row['situation']} → {row['yesno_question']}" for row in usable[:6]] or ["Ainda não há situações gravadas."],
        rules=["A resposta certa é a pergunta da mesma linha, não uma pergunta gramaticalmente possível de outra situação."],
        pitfalls=["Associar a situação a uma pergunta de outro exemplo."],
        memorize=["Situação e pergunta precisam ser o par gravado."],
        sources=[{"title": "Caderno SQLite, tabela yesno_examples", "url": ""}],
    )
    return Module(
        id="yesno",
        title="Yes/No",
        summary="Situações e perguntas já registadas.",
        topics=[
            Topic(
                id="yesno-match",
                name="Situação e pergunta",
                module_id="yesno",
                lesson=lesson,
                questions=questions,
                flashcards=[
                    Flashcard(id=f"english-card-yesno-{row['id']}", front=row["situation"], back=row["yesno_question"], source="yesno_examples")
                    for row in usable[:20]
                ],
            )
        ],
    )


def _revision_module() -> Module:
    from word_bank.content import revision_data as data

    pairs = list(data.CONTRACTIONS)
    questions: list[Question] = []
    for full, short in pairs:
        built = _build_mcq(
            question_id=f"english:revision:{full}:contraction",
            module_id="revision",
            topic_id="revision-be",
            prompt=f"No material de revisão do caderno, qual é a forma contraída de «{full}»?",
            correct=short,
            pool=[(other_short, other_full) for other_full, other_short in pairs if other_full != full],
            recognition=f"Forma inteira «{full}» → contração do material «{short}».",
            source="word_bank/content/revision_data.py, CONTRACTIONS",
            difficulty=1,
        )
        if built:
            questions.append(built)
    forms = data.BE_FORMS["forms"]
    am = next(item["form"] for item in forms if item["form"] == "Am")
    other_forms = [item["form"] for item in forms if item["form"] != "Am"]
    contraction_i = next(short for full, short in pairs if full == "I am")
    pool = [(form, "forma do BE") for form in other_forms] + [(contraction_i, "contração")]
    be_question = _build_mcq(
        question_id="english:revision:be:am",
        module_id="revision",
        topic_id="revision-be",
        prompt="No material de revisão, qual forma do verbo BE é usada somente com o subject I?",
        correct=am,
        pool=pool,
        recognition="Subject I → forma Am. I'm é a contração, não uma das três formas listadas.",
        source="word_bank/content/revision_data.py, BE_FORMS",
        difficulty=1,
    )
    if be_question:
        questions.append(be_question)
    lesson = Lesson(
        blocks=[
            "O guia de revisão já existia no word-bank: formas Am/Is/Are, contrações, Yes/No, WH e statements.",
            "Abra também a secção Caderno para ver o guia completo com as tabelas originais.",
        ],
        concepts=[item["detail"] for item in forms],
        examples=[f"{full} → {short}" for full, short in pairs],
        comparisons=[
            {"left": "Am", "right": "Is / Are", "difference": "Am só com I. Is nas outras situações singulares. Are com you, we, they e plurais."}
        ],
        relations=["Subject no enunciado → forma do BE → contração, se o material a listar."],
        rules=[data.YESNO["formula"], data.WH_QUESTIONS["formula"]],
        pitfalls=["Tratar I'm como uma quarta forma do presente do BE. No material, I'm é contração de I am."],
        memorize=[f"{item['form']}: {item['detail']}" for item in forms],
        sources=[{"title": "Revisão estática do word-bank", "url": ""}],
    )
    return Module(
        id="revision",
        title="Revisão do BE",
        summary="Conteúdo estático que já vinha no projeto de inglês.",
        topics=[
            Topic(
                id="revision-be",
                name="BE, contrações e fórmulas",
                module_id="revision",
                lesson=lesson,
                questions=questions,
                flashcards=[
                    Flashcard(id=f"english-card-revision-{index}", front=full, back=short, source="revision_data.CONTRACTIONS")
                    for index, (full, short) in enumerate(pairs)
                ],
            )
        ],
    )


def _build_mcq(
    *,
    question_id: str,
    module_id: str,
    topic_id: str,
    prompt: str,
    correct: str,
    pool: list[tuple[str, str]],
    recognition: str,
    source: str,
    difficulty: int,
) -> Question | None:
    unique: list[tuple[str, str]] = []
    seen = {correct}
    for text, owner in pool:
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append((text, owner))
    if len(unique) < 3:
        return None
    rng = random.Random(question_id)
    rng.shuffle(unique)
    picked = unique[:3]
    texts = [correct, *[text for text, _owner in picked]]
    rng.shuffle(texts)
    owners = {correct: None, **{text: owner for text, owner in picked}}
    choices = []
    for text in texts:
        if text == correct:
            explanation = "Este é o texto gravado para o item pedido."
        else:
            owner = owners.get(text)
            explanation = (
                f"«{text}» pertence a outro registo"
                + (f" ({owner})" if owner else "")
                + ". Não responde ao item pedido no enunciado."
            )
        choices.append(Choice(text=text, explanation=explanation))
    return Question(
        id=question_id,
        course_id="english",
        module_id=module_id,
        topic_id=topic_id,
        prompt=prompt,
        choices=choices,
        correct_index=texts.index(correct),
        recognition_key=recognition,
        difficulty=difficulty,
        source=source,
        review_status="caderno",
        origin="caderno",
    )


def _order_texts(texts: list[str], seed: str) -> list[str]:
    rng = random.Random(seed)
    ordered = texts[:]
    rng.shuffle(ordered)
    return ordered
