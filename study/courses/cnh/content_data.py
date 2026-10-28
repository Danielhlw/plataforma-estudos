"""Dados do curso CNH. Execute para regenerar os JSON em data/modules."""

from __future__ import annotations

import json
from pathlib import Path

CTB = "https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm"
PORTARIA = "https://www.gov.br/transportes/pt-br/assuntos/transito/arquivos-senatran/portarias/2025/Portaria9232025.pdf/@@display-file/file"
RESOLUCAO = "https://www.in.gov.br/web/dou/-/resolucao-contran-n-1.020-de-1-de-dezembro-de-2025-674131330"
DETRAN = "https://www.detran.al.gov.br/conteudo/cnh-do-brasil"
WHEN = "2026-10-27"


def q(qid, module, topic, prompt, options, correct, recognition, source, url, difficulty, importance=1):
    return {
        "id": qid,
        "domain": "cnh-al",
        "module": module,
        "topic": topic,
        "question": prompt,
        "options": [{"text": text, "explanation": explanation} for text, explanation in options],
        "correctIndex": correct,
        "recognitionKey": recognition,
        "difficulty": difficulty,
        "source": source,
        "sourceUrl": url,
        "lastVerifiedAt": WHEN,
        "reviewStatus": "verificado",
        "origin": "treino",
        "normVersion": "CTB compilado e normas consultadas em 2026-10-27",
        "examImportance": importance,
    }


def lesson(blocks, concepts, examples, comparisons, relations, rules, pitfalls, memorize, sources):
    return {
        "blocks": blocks,
        "concepts": concepts,
        "examples": examples,
        "comparisons": comparisons,
        "relations": relations,
        "rules": rules,
        "pitfalls": pitfalls,
        "memorize": memorize,
        "sources": sources,
    }


def card(cid, front, back, source):
    return {"id": cid, "front": front, "back": back, "source": source}


def topic(tid, name, module, body, cards, questions):
    return {"id": tid, "name": name, "module": module, "lesson": body, "flashcards": cards, "questions": questions}


def module(mid, title, summary, importance, official, topics):
    return {
        "id": mid,
        "title": title,
        "summary": summary,
        "examImportance": importance,
        "officialBlock": official,
        "topics": topics,
    }


MODULES = [
    module(
        "sinalizacao",
        "Sinalização viária",
        "Primeiro bloco do curso teórico na Portaria SENATRAN 923/2025.",
        2,
        "Sinalização viária de trânsito",
        [
            topic(
                "hierarquia",
                "Hierarquia da sinalização",
                "sinalizacao",
                lesson(
                    blocks=[
                        "Quando dois sinais parecem dizer coisas diferentes, a ordem legal decide qual deles manda.",
                        "O Código não trata placa, semáforo e agente como equivalentes.",
                    ],
                    concepts=[
                        "Art. 89 do CTB: prevalece, nesta ordem, a ordem do agente, a indicação do semáforo e, depois, os demais sinais sobre as outras normas de trânsito.",
                    ],
                    examples=[
                        "O semáforo está verde e o agente está de frente para o fluxo, com o braço levantado determinando parada. Vale a ordem do agente.",
                        "Não há agente. O semáforo está vermelho e uma placa de indicação parece liberar o caminho. Vale o semáforo.",
                    ],
                    comparisons=[
                        {"left": "Ordem do agente", "right": "Semáforo e placas", "difference": "A ordem do agente prevalece sobre os outros sinais."},
                        {"left": "Semáforo", "right": "Placas e marcas", "difference": "Sem agente, o semáforo prevalece sobre os demais sinais."},
                    ],
                    relations=["Conflito no enunciado → identificar quem está presente → aplicar a ordem do art. 89."],
                    rules=[
                        "Se o enunciado cita um agente dando uma ordem, essa ordem vem primeiro.",
                        "Se não há agente e há semáforo, o semáforo vem antes da placa.",
                        "Placa e marca prevalecem sobre uma regra genérica de circulação quando o art. 89, III, é o ponto da questão.",
                    ],
                    pitfalls=[
                        "Achar que a placa, por ser permanente, vence o semáforo.",
                        "Tratar o gesto do agente como um simples conselho.",
                    ],
                    memorize=["Agente, depois semáforo, depois os demais sinais."],
                    sources=[{"title": "CTB, art. 89", "url": CTB}, {"title": "Portaria SENATRAN 923/2025, Anexo I, hierarquia da sinalização", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-hierarquia-1", "Quem prevalece: agente ou semáforo?", "A ordem do agente de trânsito prevalece sobre o semáforo e os outros sinais (CTB, art. 89, I).", CTB),
                    card("cnh-card-hierarquia-2", "Sem agente, quem prevalece: semáforo ou placa?", "O semáforo prevalece sobre os demais sinais (CTB, art. 89, II).", CTB),
                ],
                [
                    q(
                        "cnh-sinal-hierarquia-01",
                        "sinalizacao",
                        "hierarquia",
                        "Num cruzamento, o semáforo está verde para você e o agente de trânsito, de frente para o seu fluxo, determina a parada. O que prevalece?",
                        [
                            ("A ordem do agente de trânsito.", "O art. 89, I, do CTB põe as ordens do agente acima das normas de circulação e dos outros sinais. O verde do semáforo não anula essa ordem."),
                            ("O semáforo verde, porque é um sinal luminoso automático.", "O semáforo prevalece sobre placas e marcas, não sobre a ordem do agente. O enunciado traz os dois, então o critério é o inciso I."),
                            ("A placa existente no local, por ser sinalização permanente.", "Placa está abaixo do agente e do semáforo na ordem do art. 89. Permanência física não muda a hierarquia."),
                            ("A regra geral de que o verde autoriza a passagem, mesmo contra o agente.", "A regra geral cede quando há ordem do agente. Seguir só pelo verde ignora o sinal que o Código coloca em primeiro lugar."),
                        ],
                        0,
                        "Agente dando ordem e semáforo ao mesmo tempo → prevalece o agente → art. 89, I.",
                        "CTB, art. 89, I",
                        CTB,
                        1,
                        2,
                    ),
                    q(
                        "cnh-sinal-hierarquia-02",
                        "sinalizacao",
                        "hierarquia",
                        "Não há agente no local. O semáforo está vermelho e uma placa de indicação aponta o caminho à frente. O que o condutor deve obedecer primeiro?",
                        [
                            ("O semáforo vermelho.", "Sem ordem de agente, o art. 89, II, faz a indicação do semáforo prevalecer sobre os demais sinais."),
                            ("A placa de indicação, porque informa o destino.", "Placa de indicação orienta. Não vence o semáforo. O enunciado não tem agente, então o conflito é semáforo contra placa."),
                            ("Os dois ao mesmo tempo: seguir a placa e atravessar no vermelho.", "Obedecer aos dois neste caso é impossível. A hierarquia existe justamente para o conflito."),
                            ("A preferência de quem vem pela direita, porque o cruzamento fica sem regra.", "O cruzamento não está sem sinal. Há semáforo. A regra da direita do art. 29, III, c, é para fluxo não sinalizado."),
                        ],
                        0,
                        "Sem agente, semáforo contra placa → semáforo → art. 89, II. A direita só entra se não houver sinalização.",
                        "CTB, art. 89, II e III",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-sinal-hierarquia-03",
                        "sinalizacao",
                        "hierarquia",
                        "Uma via sem agente e sem semáforo tem placa de regulamentação que fixa uma conduta. Essa placa se relaciona como com as normas gerais de circulação?",
                        [
                            ("A indicação daquele sinal prevalece sobre as demais normas de trânsito.", "É o art. 89, III: as indicações dos sinais prevalecem sobre as demais normas. A placa regulamenta aquela via."),
                            ("A norma geral do Código sempre vence a placa, porque a lei é superior a um sinal.", "O próprio Código, no art. 89, III, manda o sinal prevalecer sobre as demais normas de trânsito. Não é um conflito entre lei e placa fora do CTB."),
                            ("A placa só vale se um agente a repetir.", "O agente está no topo quando está presente. A ausência dele não apaga a placa."),
                            ("A placa de regulamentação apenas sugere, e o condutor escolhe a norma geral se for mais conveniente.", "Regulamentar não é sugerir. Conveniência do condutor não é critério do art. 89."),
                        ],
                        0,
                        "Sem agente e sem semáforo, o enunciado entrega uma placa de regulamentação → o sinal prevalece sobre a norma geral → art. 89, III.",
                        "CTB, art. 89, III",
                        CTB,
                        2,
                        2,
                    ),
                ],
            ),
            topic(
                "classificacao",
                "Classificação e uso da sinalização",
                "sinalizacao",
                lesson(
                    blocks=[
                        "O art. 87 do CTB classifica os sinais. A Portaria 923 pede leitura desses grupos, não decorar um simulado antigo.",
                        "Sinalização insuficiente ou incorreta não gera sanção ao condutor, e o órgão da via responde por essa falha.",
                    ],
                    concepts=[
                        "Sinais verticais, horizontais, dispositivos auxiliares, luminosos, sonoros e gestos do agente e do condutor (art. 87).",
                        "Faixa de pedestre é marca no pavimento: o art. 85 exige faixas pintadas ou demarcadas nos locais destinados à travessia.",
                        "Via em obra não pode ser reaberta sem sinalização vertical e horizontal adequada (art. 88).",
                    ],
                    examples=[
                        "Placa ao lado da via: sinal vertical. Faixa pintada no chão: sinal horizontal.",
                        "Gesto do agente e gesto regulamentar de braço do condutor também são sinais, no art. 87, VI.",
                    ],
                    comparisons=[
                        {"left": "Sinal vertical", "right": "Sinal horizontal", "difference": "Vertical é posto na via, como placa. Horizontal é marca no pavimento."},
                        {"left": "Sanção por desobedecer sinal regular", "right": "Sinal insuficiente ou incorreto", "difference": "O art. 90 afasta a sanção quando a sinalização é insuficiente ou incorreta."},
                    ],
                    relations=["O enunciado descreve onde o sinal está → classificar o grupo do art. 87 → só então decidir a conduta."],
                    rules=[
                        "É proibido colocar publicidade sobre a sinalização ou junto dela de modo a não se relacionar com a mensagem (art. 82).",
                        "Se o enunciado disser que a sinalização estava insuficiente ou incorreta, a sanção do Código não se aplica (art. 90).",
                    ],
                    pitfalls=[
                        "Chamar faixa pintada de placa.",
                        "Punir o condutor por um sinal que o próprio enunciado descreve como incorreto ou insuficiente.",
                    ],
                    memorize=[
                        "Seis grupos do art. 87: vertical, horizontal, auxiliar, luminoso, sonoro e gestos.",
                        "Sinalização ruim não autoriza multa por desobedecê-la.",
                    ],
                    sources=[{"title": "CTB, arts. 82, 85, 87, 88 e 90", "url": CTB}, {"title": "Portaria SENATRAN 923/2025, bloco de sinalização", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-class-1", "Quais são os grupos de sinais do art. 87?", "Verticais, horizontais, dispositivos auxiliares, luminosos, sonoros e gestos do agente e do condutor.", CTB),
                    card("cnh-card-class-2", "Sinalização insuficiente gera multa por desobediência?", "Não. O art. 90 afasta a sanção quando a sinalização é insuficiente ou incorreta.", CTB),
                ],
                [
                    q(
                        "cnh-sinal-class-01",
                        "sinalizacao",
                        "classificacao",
                        "Pelo art. 87 do CTB, os sinais de trânsito classificam-se em verticais, horizontais, dispositivos auxiliares, luminosos, sonoros e mais um grupo. Qual é?",
                        [
                            ("Gestos do agente de trânsito e do condutor.", "O inciso VI do art. 87 inclui esses gestos entre os sinais. Não são um adorno à parte da sinalização."),
                            ("Apenas mensagens enviadas por aplicativo do DETRAN.", "O art. 87 não cria essa categoria. Aplicativo não substitui o grupo dos gestos."),
                            ("Somente placas de indicação turística.", "Indicação turística, quando existe como placa, cabe na sinalização vertical, não num sétimo grupo. O grupo que faltava na lista do enunciado é o dos gestos."),
                            ("Exclusivamente as campanhas educativas de rádio.", "Campanha educativa não é um dos incisos do art. 87. Sinal sonoro de trânsito também não se confunde com publicidade."),
                        ],
                        0,
                        "A lista do enunciado para no art. 87, V. O que falta é o inciso VI: gestos.",
                        "CTB, art. 87",
                        CTB,
                        1,
                        2,
                    ),
                    q(
                        "cnh-sinal-class-02",
                        "sinalizacao",
                        "classificacao",
                        "O órgão destina um local à travessia de pedestres. Que sinalização o art. 85 exige nesse local?",
                        [
                            ("Faixas pintadas ou demarcadas no leito da via.", "O art. 85 obriga sinalizar esses locais com faixas pintadas ou demarcadas. É sinal horizontal, no pavimento."),
                            ("Apenas uma placa de indicação de destino, sem marca no pavimento.", "Placa de destino não cumpre o art. 85. O artigo fala em faixas no leito da via."),
                            ("Somente o gesto eventual de um pedestre.", "Gesto pode ser sinal do art. 87, mas o local destinado à travessia precisa da faixa do art. 85."),
                            ("Uma mensagem no aplicativo CNH do Brasil.", "O aplicativo não substitui a marca no pavimento exigida para aquele local."),
                        ],
                        0,
                        "Enunciado diz «local destinado à travessia» → art. 85 → faixa no pavimento, não placa de destino.",
                        "CTB, art. 85",
                        CTB,
                        1,
                        1,
                    ),
                    q(
                        "cnh-sinal-class-03",
                        "sinalizacao",
                        "classificacao",
                        "O condutor deixou de seguir uma indicação porque a sinalização da via estava incorreta. O que diz o art. 90 do CTB?",
                        [
                            ("Não se aplicam as sanções do Código por inobservância a sinalização insuficiente ou incorreta.", "O caput do art. 90 é direto. A falha da sinalização não vira infração do condutor por tê-la desobedecido."),
                            ("A sanção permanece, e o condutor discute só o valor da multa.", "O artigo afasta a sanção. Não reduz a discussão ao preço."),
                            ("A sanção só cai se um agente confirmar no local, no momento da passagem.", "O art. 90 não condiciona o afastamento a essa confirmação presencial do agente."),
                            ("A sinalização incorreta agrava a infração, porque o condutor deveria parar sempre.", "O Código faz o contrário: não pune a inobservância quando o sinal é insuficiente ou incorreto. Quem responde pela falha é o órgão da via, no § 1º."),
                        ],
                        0,
                        "O enunciado qualifica a sinalização como incorreta → art. 90 → não há sanção por desobedecer esse sinal.",
                        "CTB, art. 90",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-sinal-class-04",
                        "sinalizacao",
                        "classificacao",
                        "Uma via pavimentada vai ser reaberta depois de uma obra. O que o art. 88 exige antes de devolvê-la ao trânsito?",
                        [
                            ("Sinalização vertical e horizontal que garanta condições adequadas de segurança.", "O art. 88 proíbe entregar ou reabrir via pavimentada sem essa sinalização. O parágrafo único pede sinalização específica no trecho em obra."),
                            ("Apenas a retirada dos cones, mesmo sem faixa ou placa.", "Retirar o obstáculo sem sinalizar não cumpre o artigo. A via precisa estar sinalizada vertical e horizontalmente."),
                            ("Somente um anúncio de rádio avisando os moradores.", "Aviso não substitui a sinalização na via."),
                            ("A pintura pode esperar o mês seguinte, desde que a pista esteja limpa.", "O artigo não autoriza esse prazo. A reabertura depende da sinalização já estar feita."),
                        ],
                        0,
                        "Obra ou reabertura de via pavimentada → art. 88 → sinal vertical e horizontal antes de circular.",
                        "CTB, art. 88",
                        CTB,
                        1,
                        1,
                    ),
                    q(
                        "cnh-sinal-class-05",
                        "sinalizacao",
                        "classificacao",
                        "Alguém fixa um cartaz de publicidade sobre uma placa de trânsito, com texto que não tem relação com a mensagem da placa. O que o art. 82 determina?",
                        [
                            ("É proibido afixar publicidade, inscrição ou símbolo que não se relacione com a mensagem da sinalização.", "O art. 82 veda isso sobre a sinalização, nos suportes ou junto a eles. O cartaz do enunciado é exatamente esse caso."),
                            ("A publicidade é livre se não tampar mais da metade da placa.", "O artigo não abre essa exceção de tamanho."),
                            ("O cartaz vale como sinalização complementar.", "Publicidade alheia à mensagem não vira sinal. O art. 80 ainda veda sinalização que não seja a prevista."),
                            ("Só é proibido se o cartaz for luminoso.", "O art. 82 não limita a proibição ao anúncio luminoso."),
                        ],
                        0,
                        "Cartaz estranho à mensagem, pregado na placa → art. 82 → proibido. Não é sinal novo.",
                        "CTB, art. 82",
                        CTB,
                        1,
                        1,
                    ),
                ],
            ),
        ],
    ),
]


def infracoes():
    src = "CTB, arts. 256, 259, 261 e 269"
    return module(
        "infracoes",
        "Infrações de trânsito",
        "Segundo bloco da Portaria SENATRAN 923/2025: natureza, pontos, penalidades e medidas.",
        3,
        "Infrações de trânsito",
        [
            topic(
                "pontos",
                "Natureza e pontuação",
                "infracoes",
                lesson(
                    blocks=[
                        "O art. 259 fixa os pontos. Grave e gravíssima não têm o mesmo número.",
                        "A suspensão por contagem, no art. 261, muda conforme existam infrações gravíssimas. Quem exerce atividade remunerada ao veículo tem regra própria no § 5º.",
                    ],
                    concepts=[
                        "Gravíssima: 7 pontos. Grave: 5. Média: 4. Leve: 3.",
                        "Em 12 meses: 20 pontos se houver duas ou mais gravíssimas; 30 se houver uma; 40 se não houver gravíssima.",
                        "Condutor em atividade remunerada ao veículo: a suspensão por pontos usa o limite de 40, qualquer que seja a natureza, com curso preventivo facultado aos 30 pontos.",
                    ],
                    examples=[
                        "Duas gravíssimas no prontuário: o limite da alínea a é 20 pontos, não 40.",
                        "Nenhuma gravíssima: o limite da alínea c é 40 pontos.",
                    ],
                    comparisons=[
                        {"left": "Grave, 5 pontos", "right": "Gravíssima, 7 pontos", "difference": "Não são a mesma natureza. O enunciado que diz só «grave» não autoriza contar 7."},
                        {"left": "Limite de 20", "right": "Limite de 40", "difference": "20 quando há duas ou mais gravíssimas. 40 quando não há gravíssima, ou no caso do § 5º da atividade remunerada."},
                    ],
                    relations=["Natureza nomeada no enunciado → pontos do art. 259. Quantidade de gravíssimas → alínea do art. 261."],
                    rules=[
                        "Não troque 5 e 7. O erro clássico é chamar a grave de 7 pontos.",
                        "Antes de escolher 20, 30 ou 40, conte as gravíssimas que o enunciado informa.",
                    ],
                    pitfalls=[
                        "Aplicar 40 pontos a qualquer condutor, mesmo com duas gravíssimas.",
                        "Aplicar 20 pontos a quem não tem gravíssima.",
                        "Esquecer que a atividade remunerada ao veículo segue o § 5º.",
                    ],
                    memorize=["7, 5, 4 e 3.", "20, 30 ou 40 conforme as gravíssimas.", "Atividade remunerada: limite de 40 pontos."],
                    sources=[{"title": "CTB, arts. 259 e 261", "url": CTB}],
                ),
                [
                    card("cnh-card-pontos-1", "Pontos: gravíssima, grave, média e leve", "7, 5, 4 e 3 (CTB, art. 259).", CTB),
                    card("cnh-card-pontos-2", "Suspensão por pontos em 12 meses", "20 com duas ou mais gravíssimas; 30 com uma; 40 sem gravíssima (art. 261, I).", CTB),
                ],
                [
                    q(
                        "cnh-inf-pontos-01",
                        "infracoes",
                        "pontos",
                        "Quantos pontos o art. 259 atribui, respectivamente, às infrações gravíssima, grave, média e leve?",
                        [
                            ("7, 5, 4 e 3.", "É a escala do art. 259: gravíssima sete, grave cinco, média quatro, leve três."),
                            ("7, 7, 5 e 4.", "Grave não tem sete pontos. Sete é só a gravíssima. Essa alternativa cola as duas naturezas mais pesadas."),
                            ("5, 4, 3 e 1.", "A gravíssima fica de fora. Cinco já é a grave. Não existe, nesse artigo, infração de um ponto."),
                            ("10, 7, 5 e 3.", "Dez não é pontuação do art. 259. O fator dez aparece em multa do art. 165, que é outra conta."),
                        ],
                        0,
                        "A pergunta nomeia as quatro naturezas na ordem do art. 259 → 7, 5, 4, 3. Não misturar com o multiplicador da multa.",
                        "CTB, art. 259",
                        CTB,
                        1,
                        3,
                    ),
                    q(
                        "cnh-inf-pontos-02",
                        "infracoes",
                        "pontos",
                        "Um condutor que não exerce atividade remunerada ao veículo soma, em 12 meses, pontos de duas infrações gravíssimas. Qual limite da suspensão por contagem se aplica?",
                        [
                            ("20 pontos.", "Art. 261, I, a: 20 pontos quando constem duas ou mais infrações gravíssimas."),
                            ("40 pontos, porque esse é o teto único do Código.", "40 é a alínea c, para quem não tem gravíssima, e também o § 5º da atividade remunerada. O enunciado tem duas gravíssimas e não fala em atividade remunerada."),
                            ("30 pontos, porque há gravíssima.", "30 é a alínea b, quando consta uma gravíssima. Duas ou mais caem na alínea a."),
                            ("Não há suspensão por pontos se a infração já é gravíssima.", "A natureza gravíssima não apaga a contagem do inciso I. Há ainda suspensão específica em algumas infrações, que é outro inciso."),
                        ],
                        0,
                        "Duas gravíssimas e sem atividade remunerada → alínea a → 20 pontos. Uma seria 30. Nenhuma seria 40.",
                        "CTB, art. 261, I, a",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-pontos-03",
                        "infracoes",
                        "pontos",
                        "O condutor exerce atividade remunerada ao veículo. Pelo art. 261, § 5º, a suspensão por pontos é imposta quando ele atinge qual limite?",
                        [
                            ("40 pontos, independentemente da natureza das infrações.", "O § 5º usa o limite da alínea c, 40 pontos, qualquer que seja a natureza, e faculta o curso preventivo ao chegar a 30."),
                            ("20 pontos, mesmo sem gravíssima, por ser motorista profissional.", "20 não é a regra do § 5º. Profissional remunerado não é automaticamente o limite mais baixo."),
                            ("30 pontos, como limite único de suspensão.", "30 pontos, nesse parágrafo, é o momento em que o curso preventivo é facultado, não o gatilho da suspensão."),
                            ("7 pontos, correspondentes a uma gravíssima.", "7 é a pontuação de uma infração, não o limite de suspensão do § 5º."),
                        ],
                        0,
                        "Enunciado diz atividade remunerada ao veículo → § 5º → suspensão aos 40. Trinta é o curso preventivo facultativo.",
                        "CTB, art. 261, § 5º",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-pontos-04",
                        "infracoes",
                        "pontos",
                        "No período de 12 meses há exatamente uma infração gravíssima na pontuação de quem não exerce atividade remunerada ao veículo. Qual é o limite de pontos para a suspensão?",
                        [
                            ("30 pontos.", "Art. 261, I, b: 30 pontos quando consta uma infração gravíssima."),
                            ("20 pontos.", "20 exige duas ou mais gravíssimas. Aqui há uma só."),
                            ("40 pontos.", "40 é o caso sem nenhuma gravíssima, ou o § 5º. O enunciado informa uma gravíssima e afasta a atividade remunerada."),
                            ("5 pontos, que é o valor de uma infração grave.", "O limite não é a pontuação de uma natureza. Cinco pontos nem esgotam uma gravíssima, que vale sete."),
                        ],
                        0,
                        "Uma gravíssima, condutor não remunerado → alínea b → 30. Não saltar para 20 nem para 40.",
                        "CTB, art. 261, I, b",
                        CTB,
                        2,
                        3,
                    ),
                ],
            ),
            topic(
                "medidas",
                "Penalidade e medida administrativa",
                "infracoes",
                lesson(
                    blocks=[
                        "Penalidade e medida administrativa andam juntas com frequência, mas não são a mesma coisa.",
                        "O art. 256 lista penalidades. O art. 269 lista medidas. O § 2º do art. 269 diz que a medida não substitui a penalidade.",
                    ],
                    concepts=[
                        "Penalidades do art. 256 incluem advertência por escrito, multa, suspensão do direito de dirigir, cassação da CNH, cassação da Permissão para Dirigir e frequência obrigatória em curso de reciclagem.",
                        "Medidas do art. 269 incluem retenção e remoção do veículo, recolhimento dos documentos de habilitação e de registro, transbordo do excesso de carga e teste de alcoolemia.",
                    ],
                    examples=[
                        "Recolher a CNH no ato é medida administrativa. Suspender o direito de dirigir é penalidade.",
                        "Reter o veículo não apaga a multa prevista para a infração.",
                    ],
                    comparisons=[
                        {"left": "Multa", "right": "Remoção do veículo", "difference": "Multa está no art. 256. Remoção está no art. 269."},
                        {"left": "Suspensão do direito de dirigir", "right": "Recolhimento da CNH", "difference": "Suspensão é penalidade. Recolher o documento é medida, de caráter complementar."},
                    ],
                    relations=["O enunciado pergunta se a consequência é punição ou providência imediata → art. 256 ou art. 269."],
                    rules=["Se a alternativa chama remoção ou retenção de penalidade, ela troca os artigos.", "Medida complementar não elide a penalidade."],
                    pitfalls=["Achar que, recolhido o veículo, não cabe mais multa.", "Listar advertência por escrito como medida do art. 269."],
                    memorize=["256 pune. 269 adota providência complementar.", "A medida não substitui a penalidade."],
                    sources=[{"title": src, "url": CTB}],
                ),
                [
                    card("cnh-card-medida-1", "Remoção do veículo é penalidade ou medida?", "Medida administrativa, art. 269, II. Não substitui a penalidade.", CTB),
                    card("cnh-card-medida-2", "A medida administrativa apaga a multa?", "Não. Art. 269, § 2º: a medida não elide a penalidade e tem caráter complementar.", CTB),
                ],
                [
                    q(
                        "cnh-inf-medida-01",
                        "infracoes",
                        "medidas",
                        "A autoridade remove o veículo do local. Essa remoção, no CTB, é o quê?",
                        [
                            ("Medida administrativa, que não substitui a penalidade da infração.", "Remoção está no art. 269, II. O § 2º diz que as medidas não elidem as penalidades e são complementares."),
                            ("Penalidade principal, no lugar da multa.", "Multa e as outras punições estão no art. 256. Remoção não é uma delas, e não ocupa o lugar da multa."),
                            ("Crime de trânsito, automaticamente.", "Remover o veículo é providência administrativa. Crime depende de tipo penal, que o enunciado não descreve."),
                            ("Advertência por escrito.", "Advertência é penalidade do art. 256, I. Não descreve a retirada do veículo."),
                        ],
                        0,
                        "O verbo do enunciado é remover o veículo → art. 269 → medida complementar, não substituto da multa.",
                        "CTB, art. 269, II e § 2º",
                        CTB,
                        1,
                        3,
                    ),
                    q(
                        "cnh-inf-medida-02",
                        "infracoes",
                        "medidas",
                        "Qual destes efeitos está listado como penalidade no art. 256, e não como medida do art. 269?",
                        [
                            ("Suspensão do direito de dirigir.", "É penalidade, art. 256, III. Recolher a CNH, que às vezes ocorre junto, é outra coisa: medida do art. 269, III."),
                            ("Retenção do veículo.", "Retenção é medida, art. 269, I."),
                            ("Transbordo do excesso de carga.", "Transbordo é medida, art. 269, VIII."),
                            ("Realização de teste de alcoolemia.", "O teste está no art. 269, IX, como medida administrativa."),
                        ],
                        0,
                        "Separe punição de providência. Suspensão pune. Reter, transbordar e testar são medidas.",
                        "CTB, arts. 256 e 269",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-medida-03",
                        "infracoes",
                        "medidas",
                        "O veículo foi retido. O condutor afirma que, por isso, a multa da infração não pode mais ser aplicada. O que diz o art. 269, § 2º?",
                        [
                            ("A medida não elide a penalidade e tem caráter complementar.", "Retenção não apaga multa, suspensão nem outra penalidade prevista no artigo da infração."),
                            ("A retenção substitui todas as penalidades do artigo.", "O parágrafo diz o contrário: não elide."),
                            ("A multa só cabe se não houver medida administrativa possível.", "As duas podem coexistir. A medida não é plano B da multa."),
                            ("A retenção converte a infração em advertência por escrito.", "Advertência é penalidade específica, não o efeito automático da retenção."),
                        ],
                        0,
                        "Retenção já feita e alguém conclui que a multa morreu → § 2º do art. 269 → a medida é complementar.",
                        "CTB, art. 269, § 2º",
                        CTB,
                        1,
                        2,
                    ),
                ],
            ),
            topic(
                "condutas",
                "Condutas frequentes no enunciado",
                "infracoes",
                lesson(
                    blocks=[
                        "Estas condutas estão nomeadas na Portaria 923 e têm artigo próprio no CTB. O enunciado quase sempre entrega o verbo: segurar o telefone, exceder um percentual, recusar o teste, não ceder a faixa.",
                        "Não use o valor em reais da multa. Ele é atualizado fora do artigo e não é necessário para classificar a natureza.",
                    ],
                    concepts=[
                        "Velocidade acima da máxima: até 20%, média; mais de 20% até 50%, grave; mais de 50%, gravíssima, com multa em três vezes e suspensão (art. 218).",
                        "Segurar ou manusear o celular é o parágrafo único do art. 252: a hipótese do inciso V passa a gravíssima. Fone de ouvido ligado a aparelho sonoro ou celular, no inciso VI, é infração média.",
                        "Álcool ou substância psicoativa, art. 165: gravíssima, multa dez vezes e suspensão por 12 meses. Recusar o teste do art. 277 é o art. 165-A, com a mesma estrutura de penalidade.",
                        "Avançar o sinal vermelho ou a parada obrigatória é gravíssima, art. 208, com a exceção do art. 44-A onde houver sinal que permita a conversão à direita.",
                    ],
                    examples=[
                        "Limite de 60 km/h e o veículo a 70: o excesso é de cerca de 16%, dentro de até 20%. Natureza média.",
                        "Limite de 40 e o veículo a 70: o excesso passa de 50%. Natureza gravíssima, com suspensão.",
                        "Mão no telefone: parágrafo único do art. 252. Fone no ouvido: inciso VI, média.",
                    ],
                    comparisons=[
                        {"left": "Fone no ouvido", "right": "Segurar o celular", "difference": "Inciso VI é média. O parágrafo único torna gravíssima a conduta de segurar ou manusear o telefone."},
                        {"left": "Dirigir sob influência", "right": "Recusar o teste", "difference": "Art. 165 e art. 165-A são tipos diferentes, ambos gravíssimos, com multa de dez vezes e suspensão de 12 meses."},
                    ],
                    relations=["Percentual acima do limite → faixa do art. 218. O que a mão faz com o telefone → inciso VI ou parágrafo único."],
                    rules=[
                        "Calcule o excesso em relação à máxima da via, não uma velocidade solta.",
                        "Até 20% inclui o valor exato de 20%. Mais de 20% já é a faixa grave.",
                        "Mais de 50% não é só multa mais cara: o inciso III acrescenta suspensão.",
                    ],
                    pitfalls=[
                        "Tratar 20% exatos como grave. A grave começa acima de 20%.",
                        "Chamar o fone de ouvido de gravíssima só porque envolve telefone.",
                        "Esquecer a exceção do art. 44-A no sinal vermelho, quando o enunciado diz que existe a sinalização permitindo a conversão à direita.",
                    ],
                    memorize=[
                        "218: até 20% média; acima de 20% até 50% grave; acima de 50% gravíssima com suspensão.",
                        "Celular na mão: gravíssima. Fone: média.",
                        "165 e 165-A: gravíssima, multa ×10, suspensão de 12 meses.",
                    ],
                    sources=[{"title": "CTB, arts. 165, 165-A, 208, 218 e 252", "url": CTB}, {"title": "Portaria 923/2025, infrações mais cometidas", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-vel-1", "Excesso de velocidade até 20%", "Infração média (art. 218, I).", CTB),
                    card("cnh-card-vel-2", "Excesso acima de 50%", "Gravíssima, multa três vezes e suspensão (art. 218, III).", CTB),
                    card("cnh-card-cel", "Segurar o celular e usar fone", "Segurar ou manusear: gravíssima (art. 252, parágrafo único). Fone conectado: média (inciso VI).", CTB),
                ],
                [
                    q(
                        "cnh-inf-conduta-01",
                        "infracoes",
                        "condutas",
                        "A máxima da via é 50 km/h. O veículo foi medido a 60 km/h, exatamente 20% acima. Qual é a infração do art. 218?",
                        [
                            ("Média, porque o excesso é de até 20%.", "O inciso I alcança o excesso de até 20%. Vinte por cento ainda está nessa faixa, não na grave."),
                            ("Grave, porque 20% já é excesso relevante.", "A grave é mais de 20% até 50%. O percentual exato de 20% não entra nela."),
                            ("Gravíssima, com suspensão, porque passou de 50 km/h.", "Passar do número da placa não escolhe a natureza. A natureza sai do percentual. Suspensão está no inciso III, acima de 50% de excesso."),
                            ("Leve, porque o art. 259 reserva 3 pontos a excessos pequenos.", "O art. 218, I, classifica essa faixa como média, não como leve. O art. 259 só converte a natureza em pontos."),
                        ],
                        0,
                        "Excesso de 20% cravados → «até 20%» → média. Grave só depois que passa de 20%.",
                        "CTB, art. 218, I",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-conduta-02",
                        "infracoes",
                        "condutas",
                        "A máxima é 80 km/h e o veículo foi medido a 100 km/h. O excesso é de 25%. Como o art. 218 classifica?",
                        [
                            ("Grave: mais de 20% e até 50%.", "25% está na faixa do inciso II. Não chega ao inciso III e já passou do inciso I."),
                            ("Média, porque não dobrou a velocidade.", "Dobrar não é o critério. O corte da média é 20%, e 25% está acima dele."),
                            ("Gravíssima com suspensão.", "Suspensão do inciso III exige excesso de mais de 50%. 25% não chega lá."),
                            ("Não há infração se a via for arterial, porque 80 km/h é um limite urbano comum.", "O limite considerado é o da via, 80. O tipo da via não apaga o art. 218 quando a máxima foi excedida."),
                        ],
                        0,
                        "Calcule (medida − máxima) / máxima. 20 km/h sobre 80 é 25% → entre 20% e 50% → grave.",
                        "CTB, art. 218, II",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-conduta-03",
                        "infracoes",
                        "condutas",
                        "A máxima é 40 km/h e o veículo segue a 70 km/h. Além da natureza gravíssima, que penalidade específica o art. 218, III, acrescenta?",
                        [
                            ("Multa em três vezes e suspensão do direito de dirigir.", "70 é 75% acima de 40, logo mais de 50%. O inciso III, na redação da Lei 14.071/2020, prevê multa tríplice e suspensão."),
                            ("Apenas multa simples, porque suspensão só existe para álcool.", "Álcool tem suspensão própria. O inciso III também prevê suspensão para esse excesso de velocidade."),
                            ("Advertência por escrito, por ser o primeiro excesso do mês.", "O artigo não troca essa faixa por advertência. A penalidade escrita no inciso III é outra."),
                            ("Somente remoção do veículo.", "Remoção é medida administrativa genérica, não a penalidade que o inciso III escreve."),
                        ],
                        0,
                        "Excesso maior que 50% → inciso III → gravíssima, multa ×3 e suspensão. Não parar na palavra gravíssima.",
                        "CTB, art. 218, III",
                        CTB,
                        3,
                        3,
                    ),
                    q(
                        "cnh-inf-conduta-04",
                        "infracoes",
                        "condutas",
                        "O condutor dirige segurando e manuseando o telefone celular. Como o art. 252 trata essa conduta?",
                        [
                            ("Infração gravíssima, pelo parágrafo único.", "O parágrafo único diz que a hipótese do inciso V é gravíssima quando o condutor segura ou manuseia o telefone."),
                            ("Infração média, a mesma do fone de ouvido.", "O inciso VI, média, é usar fone conectado a aparelho sonoro ou de telefone. Segurar o aparelho é o parágrafo único."),
                            ("Infração leve, se o veículo estiver devagar.", "A velocidade não reclassifica o parágrafo único."),
                            ("Não há infração se a chamada for no viva-voz e o aparelho continuar na mão.", "O tipo é segurar ou manusear. O enunciado diz que o telefone está na mão. Viva-voz não aparece como exceção nesse parágrafo."),
                        ],
                        0,
                        "Mão no telefone → parágrafo único do art. 252 → gravíssima. Fone no ouvido seria o inciso VI, média.",
                        "CTB, art. 252, parágrafo único",
                        CTB,
                        2,
                        3,
                    ),
                    q(
                        "cnh-inf-conduta-05",
                        "infracoes",
                        "condutas",
                        "Qual é a penalidade do art. 165 para dirigir sob a influência de álcool ou de outra substância psicoativa que determine dependência?",
                        [
                            ("Multa de dez vezes e suspensão do direito de dirigir por 12 meses.", "Essa é a redação da Lei 12.760/2012 no caput. A infração é gravíssima. A reincidência em 12 meses dobra a multa, no parágrafo único."),
                            ("Multa simples e 7 pontos, sem suspensão.", "Sete pontos seria só a conta genérica da gravíssima. O art. 165 escreve suspensão de 12 meses e o fator dez. O art. 259, § 4º, III, ainda exclui da pontuação ordinária as infrações punidas de forma específica com suspensão."),
                            ("Advertência por escrito na primeira ocorrência.", "O artigo não oferece advertência no lugar da multa de dez vezes."),
                            ("Apenas retenção do veículo, sem penalidade.", "Há medida administrativa de recolhimento do documento e retenção do veículo, mas ela não substitui a penalidade escrita no caput."),
                        ],
                        0,
                        "Influência de álcool no enunciado → art. 165, não o 165-A da recusa → multa ×10 e suspensão de 12 meses.",
                        "CTB, art. 165",
                        CTB,
                        2,
                        3,
                    ),
                ],
            ),
        ],
    )


def circulacao():
    return module(
        "circulacao",
        "Circulação, conduta e direção defensiva",
        "Terceiro bloco da Portaria SENATRAN 923/2025.",
        2,
        "Normas de circulação, conduta e direção defensiva",
        [
            topic(
                "preferencia",
                "Preferência e ultrapassagem",
                "circulacao",
                lesson(
                    blocks=[
                        "Cruzamento sem sinalização não é convite para o veículo maior ou mais rápido. O art. 29, III, escolhe quem passa.",
                        "Ultrapassagem tem lado, momento e trechos proibidos. O art. 29, § 2º, é outra regra: responsabilidade pela segurança, não preferência de passagem.",
                    ],
                    concepts=[
                        "Fluxos que se cruzam sem sinal: quem vem de rodovia, quem já circula na rotatória, e, nos demais casos, quem vem pela direita do condutor.",
                        "Ultrapassagem pela esquerda, salvo quando o veículo da frente sinaliza que vai entrar à esquerda.",
                        "Proibida em curva ou aclive sem visibilidade, passagem de nível, ponte, viaduto e travessia de pedestres, se não houver sinal permitindo, e nas interseções e proximidades.",
                    ],
                    examples=[
                        "Dois carros chegam juntos a um cruzamento sem placa e sem semáforo. Passa quem vem pela direita.",
                        "Na rotatória sem semáforo, passa quem já está circulando por ela, não quem vai entrar.",
                    ],
                    comparisons=[
                        {"left": "Preferência pela direita", "right": "Responsabilidade do maior", "difference": "A direita decide quem passa no cruzamento sem sinal. O § 2º diz que o maior responde pela segurança do menor; não lhe dá a vez."},
                        {"left": "Ultrapassar pela esquerda", "right": "Transpor faixa", "difference": "Ultrapassagem de veículo em movimento é pela esquerda, com a exceção do art. 29, IX. Transposição de faixa, pelo § 1º, pode ser pela esquerda ou pela direita."},
                    ],
                    relations=["O enunciado diz se há sinal. Sem sinal, procure rodovia, rotatória ou direita. Com curva, ponte ou cruzamento, pare na ultrapassagem."],
                    rules=[
                        "Antes da manobra, o art. 34 manda verificar se ela cabe sem perigo para quem segue, precede ou cruza.",
                        "Durante a conversão, o art. 38, parágrafo único, manda ceder aos pedestres, ciclistas e aos veículos do sentido contrário.",
                    ],
                    pitfalls=[
                        "Dar a vez a quem está mais rápido.",
                        "Usar o porte do veículo como regra de preferência.",
                        "Ultrapassar no cruzamento porque a faixa da esquerda está livre.",
                    ],
                    memorize=["Sem sinal: rodovia, rotatória, direita.", "Ultrapassagem pela esquerda.", "Interseção não é lugar de ultrapassar."],
                    sources=[{"title": "CTB, arts. 29, 32, 33, 34 e 38", "url": CTB}],
                ),
                [
                    card("cnh-card-pref-1", "Cruzamento sem sinal, caso comum", "Tem preferência quem vem pela direita (art. 29, III, c).", CTB),
                    card("cnh-card-pref-2", "Rotatória sem outra sinalização", "Tem preferência quem já circula por ela (art. 29, III, b).", CTB),
                ],
                [
                    q(
                        "cnh-circ-pref-01",
                        "circulacao",
                        "preferencia",
                        "Dois veículos aproximam-se de um cruzamento sem agente, semáforo ou placa. Nenhum vem de rodovia nem já está numa rotatória. Quem tem preferência?",
                        [
                            ("O que vem pela direita do condutor.", "É o art. 29, III, c, o critério residual quando não há sinal, rodovia nem rotatória."),
                            ("O de maior porte, porque o art. 29, § 2º, lhe dá a passagem.", "O § 2º distribui responsabilidade pela segurança: o maior cuida do menor. Não entrega a preferência de passagem."),
                            ("O que estiver em velocidade mais alta.", "Velocidade não é critério do inciso III. O art. 44 ainda pede prudência ao chegar no cruzamento."),
                            ("Quem piscar o farol primeiro.", "O art. 40, III, limita o lampejo a situações de advertência. Não cria preferência."),
                        ],
                        0,
                        "Sem sinal, sem rodovia e sem rotatória → direita. Porte e farol não escolhem quem passa.",
                        "CTB, art. 29, III, c",
                        CTB,
                        1,
                        2,
                    ),
                    q(
                        "cnh-circ-pref-02",
                        "circulacao",
                        "preferencia",
                        "Um veículo vai entrar numa rotatória sem semáforo. Outro já circula por ela. Quem tem preferência de passagem?",
                        [
                            ("Quem já está circulando pela rotatória.", "Art. 29, III, b. Entrar não dá a vez sobre quem já está no anel."),
                            ("Quem vem pela direita, mesmo para entrar.", "A direita é o critério dos demais casos. Rotatória tem alínea própria."),
                            ("Quem chega em maior velocidade, para não parar no anel.", "Velocidade não é a alínea b. Parar, se preciso, é compatível com ceder a passagem."),
                            ("O veículo de maior porte que se aproxima da entrada.", "Porte não define preferência. No § 2º ele responde pela segurança dos menores."),
                        ],
                        0,
                        "A palavra rotatória no enunciado aciona a alínea b, antes da regra geral da direita.",
                        "CTB, art. 29, III, b",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-circ-pref-03",
                        "circulacao",
                        "preferencia",
                        "O condutor quer ultrapassar um veículo em movimento. Pelo art. 29, IX, por qual lado faz a manobra?",
                        [
                            ("Pela esquerda, salvo se o veículo da frente estiver sinalizando que vai entrar à esquerda.", "A regra é a esquerda. A exceção do inciso IX é essa sinalização de entrada à esquerda, não a pressa de quem vem atrás."),
                            ("Pela direita, porque as faixas da direita são as rápidas.", "O inciso IV destina a direita aos mais lentos e de maior porte, quando não há faixa especial. A esquerda é que serve à ultrapassagem."),
                            ("Por qualquer lado, desde que haja espaço.", "Transposição de faixa pode ser pelos dois lados, no § 1º. Ultrapassagem de veículo em movimento não. O enunciado fala em ultrapassar."),
                            ("Pela esquerda apenas em rodovia. Na cidade, pela direita.", "O inciso IX não divide cidade e rodovia."),
                        ],
                        0,
                        "Verbo ultrapassar veículo em movimento → esquerda, com a exceção de quem à frente sinaliza entrada à esquerda.",
                        "CTB, art. 29, IV e IX",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-circ-pref-04",
                        "circulacao",
                        "preferencia",
                        "Em via de mão dupla e pista única, o condutor pensa em ultrapassar numa curva sem visibilidade suficiente. Não há sinal permitindo a manobra. O que diz o art. 32?",
                        [
                            ("Não pode ultrapassar nesse trecho.", "O art. 32 veda a ultrapassagem em curva e aclive sem visibilidade, além de passagem de nível, ponte, viaduto e travessia de pedestres, salvo sinalização que permita."),
                            ("Pode, se buzinar e acelerar antes da curva.", "Buzina do art. 41 não autoriza a manobra proibida. Acelerar não cria visibilidade."),
                            ("Pode pela direita, porque a proibição é só pela esquerda.", "A proibição é de ultrapassar, não de um lado só."),
                            ("Pode, porque curva sem visibilidade transfere a preferência a quem está atrás.", "Quem está atrás não ganha preferência por não enxergar. A falta de visibilidade é o motivo da proibição."),
                        ],
                        0,
                        "Curva sem visibilidade e sem placa permitindo → art. 32 → não ultrapassar.",
                        "CTB, art. 32",
                        CTB,
                        1,
                        2,
                    ),
                    q(
                        "cnh-circ-pref-05",
                        "circulacao",
                        "preferencia",
                        "O condutor inicia uma conversão à esquerda. Há pedestres na travessia e veículos vindo no sentido contrário. O que o art. 38, parágrafo único, exige durante a manobra?",
                        [
                            ("Ceder passagem aos pedestres, aos ciclistas e aos veículos do sentido contrário.", "A mudança de direção não tem prioridade automática sobre esses usuários. O parágrafo único impõe ceder."),
                            ("Seguir, porque quem já começou a conversão trava o cruzamento.", "Ter começado não está no artigo como título de preferência. O art. 45 ainda proíbe entrar na interseção se for parar no meio."),
                            ("Ceder só aos veículos. Pedestre espera a conversão terminar.", "O parágrafo nomeia pedestres e ciclistas antes dos veículos contrários."),
                            ("Buzinar para os pedestres concluírem a travessia fora da faixa.", "O art. 41 limita a buzina a advertência breve para evitar sinistro, não a abrir caminho."),
                        ],
                        0,
                        "Conversão com pedestre e fluxo contrário → art. 38, parágrafo único → ceder aos três, não só aos carros.",
                        "CTB, art. 38, parágrafo único",
                        CTB,
                        2,
                        2,
                    ),
                ],
            ),
            topic(
                "velocidade-luzes",
                "Velocidade da via e luzes",
                "circulacao",
                lesson(
                    blocks=[
                        "Onde não há placa, o art. 61, § 1º, ainda tem número. A placa, quando existe, é a máxima daquela via, e pode ser maior ou menor que a tabela.",
                        "Luz baixa, luz alta e pisca-alerta não são intercambiáveis. O art. 40 separa noite, túnel, chuva, via sem iluminação e imobilização.",
                    ],
                    concepts=[
                        "Via urbana sem placa: 80 km/h na de trânsito rápido, 60 na arterial, 40 na coletora, 30 na local.",
                        "Luz baixa à noite e, de dia, em túnel, chuva, neblina ou cerração.",
                        "Luz alta em via não iluminada, exceto ao cruzar com outro veículo ou ao segui-lo.",
                        "Pisca-alerta em imobilização ou emergência, e quando a regulamentação da via exigir.",
                    ],
                    examples=[
                        "Via local sem placa: 30 km/h, não 40. Quarenta é a coletora.",
                        "Chuva de dia: luz baixa acesa, mesmo fora da noite.",
                        "Estrada escura, carro em sentido contrário: baixar o farol alto.",
                    ],
                    comparisons=[
                        {"left": "Via local", "right": "Via coletora", "difference": "Sem placa, 30 km/h e 40 km/h. Arterial é 60. Trânsito rápido urbano é 80."},
                        {"left": "Luz alta", "right": "Pisca-alerta", "difference": "Alta é para via escura, com a exceção de cruzar ou seguir. Pisca-alerta é imobilização, emergência ou ordem da via."},
                    ],
                    relations=["O enunciado diz a classe da via e se há placa. Sem placa, use a tabela. Com chuva ou túnel, não espere anoitecer para a luz baixa."],
                    rules=[
                        "Placa de velocidade vence a tabela do § 1º, para cima ou para baixo, nos termos do § 2º.",
                        "Motocicleta em qualquer horário usa luz baixa, no § 1º do art. 40, junto com o coletivo em faixa própria.",
                    ],
                    pitfalls=[
                        "Decorar 40 km/h para toda rua sem placa.",
                        "Usar farol alto ao cruzar com outro veículo.",
                        "Ligar o pisca-alerta para justificar estacionamento em local proibido. O artigo não diz isso.",
                    ],
                    memorize=["30 local, 40 coletora, 60 arterial, 80 trânsito rápido.", "Baixa: noite, túnel e chuva. Alta: via escura, exceto ao cruzar ou seguir."],
                    sources=[{"title": "CTB, arts. 40 e 61", "url": CTB}],
                ),
                [
                    card("cnh-card-via-1", "Máximas urbanas sem placa", "Trânsito rápido 80, arterial 60, coletora 40, local 30 (art. 61, § 1º, I).", CTB),
                    card("cnh-card-luz-1", "Quando a luz baixa fica acesa", "À noite e, de dia, em túnel, chuva, neblina ou cerração (art. 40, I).", CTB),
                ],
                [
                    q(
                        "cnh-circ-vel-01",
                        "circulacao",
                        "velocidade-luzes",
                        "Não há placa de velocidade numa via urbana local. Qual é a máxima do art. 61, § 1º?",
                        [
                            ("30 km/h.", "O inciso I, d, fixa trinta quilômetros por hora nas vias locais sem sinalização regulamentadora."),
                            ("40 km/h.", "40 é a coletora, alínea c. O enunciado diz via local."),
                            ("60 km/h.", "60 é a arterial."),
                            ("80 km/h.", "80, na área urbana sem placa, é a via de trânsito rápido, não a local."),
                        ],
                        0,
                        "Sem placa e o nome da via é local → 30. Coletora 40, arterial 60, trânsito rápido 80.",
                        "CTB, art. 61, § 1º, I, d",
                        CTB,
                        1,
                        2,
                    ),
                    q(
                        "cnh-circ-vel-02",
                        "circulacao",
                        "velocidade-luzes",
                        "É dia e o veículo entra num túnel. Não chove. O que o art. 40, I, exige dos faróis?",
                        [
                            ("Luz baixa acesa.", "O inciso I manda luz baixa à noite e, mesmo de dia, em túneis e sob chuva, neblina ou cerração. Túnel basta."),
                            ("Luz alta, porque o túnel é escuro.", "Via não iluminada pode pedir luz alta, mas ao cruzar ou seguir outro veículo ela sai. O túnel está nomeado na luz baixa, não como autorização permanente de alta."),
                            ("Nenhuma luz, porque ainda é dia.", "A alínea b existe para o dia. Dia não dispensa o túnel."),
                            ("Somente o pisca-alerta enquanto estiver no túnel.", "Pisca-alerta não substitui a luz baixa de circulação. Ele é para imobilização, emergência ou regulamentação da via."),
                        ],
                        0,
                        "Túnel no enunciado, mesmo de dia e sem chuva → art. 40, I, b → luz baixa.",
                        "CTB, art. 40, I",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-circ-vel-03",
                        "circulacao",
                        "velocidade-luzes",
                        "Em via não iluminada o condutor usa luz alta e percebe outro veículo no sentido contrário. O que faz o art. 40, II?",
                        [
                            ("Não manter a luz alta ao cruzar com o outro veículo.", "O inciso II manda luz alta na via não iluminada, exceto ao cruzar ou ao seguir outro veículo."),
                            ("Manter a luz alta para ser visto mais cedo.", "Ser visto não autoriza ofuscar quem vem de frente. A exceção está escrita no inciso."),
                            ("Trocar para o pisca-alerta até o cruzamento acabar.", "Pisca-alerta não é o substituto da luz baixa nesse cruzamento."),
                            ("Apagar todos os faróis para não incomodar.", "A exceção troca a alta, não apaga a iluminação. A luz baixa continua devida à noite, no inciso I."),
                        ],
                        0,
                        "Via escura mais veículo em sentido contrário → sai a luz alta. Seguir outro veículo produz a mesma exceção.",
                        "CTB, art. 40, II",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-circ-vel-04",
                        "circulacao",
                        "velocidade-luzes",
                        "O veículo imobiliza por uma emergência. Em que situação o art. 40, V, manda usar o pisca-alerta?",
                        [
                            ("Em imobilizações ou situações de emergência, e quando a via assim regulamentar.", "São as duas hipóteses do inciso V. Não é luz de circulação normal."),
                            ("Sempre que a velocidade estiver abaixo da máxima.", "Velocidade baixa não está no inciso. O art. 219 trata de velocidade excessivamente reduzida, que é outra infração."),
                            ("Apenas à noite, em substituição à luz baixa.", "O pisca-alerta não substitui a luz baixa da noite. São comandos diferentes."),
                            ("Para avisar que o condutor vai ultrapassar.", "Avisar ultrapassagem pode usar a troca breve de luz baixa e alta, no inciso III, ou o indicador de direção. Não o pisca-alerta."),
                        ],
                        0,
                        "Imobilização ou emergência no enunciado → pisca-alerta. Ultrapassagem e noite usam outros incisos.",
                        "CTB, art. 40, V",
                        CTB,
                        1,
                        1,
                    ),
                ],
            ),
            topic(
                "defensiva",
                "Direção defensiva",
                "circulacao",
                lesson(
                    blocks=[
                        "A Portaria 923 trata direção defensiva como conduta, não como um slogan. O bloco junta norma, atenção, previsão, decisão, habilidade e autocontrole.",
                        "Pedestre na faixa tem prioridade, com a ressalva do semáforo. Quem já começou a travessia não perde a vez só porque o foco do veículo mudou.",
                    ],
                    concepts=[
                        "Pilares escritos na portaria: conhecimento das normas, atenção, previsão, decisão segura, habilidade e autocontrole.",
                        "Art. 70: pedestre na faixa tem prioridade, exceto onde o semáforo manda outra coisa. Quem não concluiu a travessia segue com preferência quando o sinal muda.",
                        "Art. 29, § 2º: o maior porte cuida do menor, o motorizado cuida do não motorizado, e todos cuidam do pedestre.",
                    ],
                    examples=[
                        "O foco abre para o carro e a pessoa ainda está na faixa. O carro espera. É o parágrafo único do art. 70.",
                        "Cansaço e pressa não são detalhes. A portaria lista fadiga, sonolência, estresse e distração entre os fatores humanos.",
                    ],
                    comparisons=[
                        {"left": "Faixa sem semáforo", "right": "Faixa com semáforo", "difference": "Sem semáforo, a prioridade de quem está na faixa é a regra. Com semáforo, vale o foco, mas quem não terminou a travessia continua tendo preferência."},
                        {"left": "Prever o risco", "right": "Reagir só depois do susto", "difference": "A portaria chama previsão de leitura do ambiente, antes da manobra. Reação tardia não é o pilar."},
                    ],
                    relations=["Pessoa na faixa → art. 70. Porte diferente no mesmo espaço → § 2º do art. 29, responsabilidade, não preferência."],
                    rules=[
                        "Não confunda o pilar com uma infração. A portaria descreve a conduta. O artigo do CTB é que classifica a omissão, quando existe tipo.",
                        "Celular, discussão e sono aparecem na portaria como fator humano, ao lado do álcool e dos medicamentos.",
                    ],
                    pitfalls=[
                        "Achar que o verde autoriza avançar sobre quem ainda atravessa.",
                        "Ler o § 2º como se o carro grande tivesse preferência sobre a moto ou o pedestre.",
                    ],
                    memorize=["Faixa: prioridade de quem atravessa. Semáforo não apaga quem já está no meio.", "Seis pilares da portaria: norma, atenção, previsão, decisão, habilidade, autocontrole."],
                    sources=[{"title": "CTB, arts. 29, § 2º, e 70", "url": CTB}, {"title": "Portaria SENATRAN 923/2025, bloco de direção defensiva", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-def-1", "Pedestre que não terminou a faixa quando o sinal muda", "Mantém a preferência (art. 70, parágrafo único).", CTB),
                    card("cnh-card-def-2", "Pilares da direção defensiva na Portaria 923", "Conhecimento das normas, atenção, previsão, decisão segura, habilidade e autocontrole.", PORTARIA),
                ],
                [
                    q(
                        "cnh-circ-def-01",
                        "circulacao",
                        "defensiva",
                        "O pedestre começou a atravessar na faixa. O semáforo abre para os veículos antes de ele concluir a travessia. O que faz o art. 70, parágrafo único?",
                        [
                            ("Mantém a preferência do pedestre que não concluiu a travessia.", "A mudança do foco não corta a travessia já iniciada. Os veículos esperam."),
                            ("Passa a valer só o verde, e o pedestre volta para a calçada.", "Voltar não está no parágrafo. A preferência continua com quem não terminou."),
                            ("O pedestre só tem prioridade se não existir semáforo.", "Sem semáforo, o caput já dá prioridade a quem está na faixa. O parágrafo existe justamente para o local com semáforo."),
                            ("A preferência fica com o veículo maior, pelo art. 29, § 2º.", "O § 2º aumenta o dever de cuidado de quem é maior. Não tira o pedestre da faixa."),
                        ],
                        0,
                        "Travessia já começada e o sinal muda → parágrafo único do art. 70 → o pedestre termina.",
                        "CTB, art. 70, parágrafo único",
                        CTB,
                        2,
                        2,
                    ),
                    q(
                        "cnh-circ-def-02",
                        "circulacao",
                        "defensiva",
                        "A Portaria SENATRAN 923/2025 lista pilares da direção defensiva aplicados à prática. Qual conjunto está nesse bloco?",
                        [
                            ("Conhecimento das normas, atenção, previsão, decisão segura, habilidade e autocontrole.", "São os itens 2.1 a 2.6 do bloco de circulação, conduta e direção defensiva da portaria. Não é uma lista inventada de slogans."),
                            ("Somente velocidade abaixo da máxima e buzina preventiva.", "Velocidade segura é outro item do mesmo bloco. Buzina preventiva não é pilar, e o art. 41 restringe a buzina."),
                            ("Preferência do veículo maior e uso contínuo da luz alta.", "As duas ideias contrariam regras do CTB já vistas: § 2º do art. 29 e art. 40, II."),
                            ("Decorar o valor em reais de cada multa.", "A portaria não transforma a tabela de preços em pilar. O bloco fala de conduta e de leitura do risco."),
                        ],
                        0,
                        "Se o enunciado pedir o pilar da portaria, não responda com uma infração nem com o preço da multa.",
                        "Portaria SENATRAN nº 923/2025, Anexo I, normas de circulação e direção defensiva, item 2",
                        PORTARIA,
                        1,
                        1,
                    ),
                ],
            ),
        ],
    )


def meio():
    return module(
        "meio-ambiente",
        "Meio ambiente e primeiros socorros",
        "Quarto bloco da Portaria SENATRAN 923/2025, incluindo manutenção preventiva.",
        1,
        "Meio ambiente e primeiros socorros",
        [
            topic(
                "socorros",
                "Socorro e local do sinistro",
                "meio-ambiente",
                lesson(
                    blocks=[
                        "O art. 176 descreve omissões graves de quem se envolveu em sinistro com vítima. A Portaria 923 acrescenta o que não fazer enquanto o socorro especializado não chega.",
                        "Esta lição não ensina procedimento médico. Ensina o limite do condutor.",
                    ],
                    concepts=[
                        "Quem se envolve em sinistro com vítima deve, podendo fazê-lo, prestar ou providenciar socorro, evitar perigo no local, preservar o local para polícia e perícia, remover o veículo se a autoridade determinar e identificar-se.",
                        "A portaria destaca o que não fazer: movimentar a vítima de forma incorreta e remover o capacete.",
                        "A infração do art. 176 é gravíssima, com multa de cinco vezes, suspensão e recolhimento do documento de habilitação.",
                    ],
                    examples=[
                        "Há vítima e o condutor pode chamar o socorro. Ir embora sem providenciar esse socorro é o inciso I.",
                        "Sair arrastando a moto do meio da via, antes de qualquer autoridade, pode atrapalhar a perícia. Preservar o local é o inciso III. Remover só quando policial ou agente determinar, inciso IV.",
                    ],
                    comparisons=[
                        {"left": "Prestar ou providenciar socorro", "right": "Tratar a lesão por conta própria", "difference": "O Código exige socorro possível. A portaria manda não fazer manobra para a qual não há capacitação, como tirar o capacete."},
                        {"left": "Preservar o local", "right": "Remover o veículo", "difference": "Preservar é a regra para a perícia. Remover entra quando a autoridade determina."},
                    ],
                    relations=["Sinistro com vítima no enunciado → art. 176. Alguém mexe no capacete ou arrasta a pessoa → limite da portaria, não um gesto de ajuda."],
                    rules=[
                        "Poder fazê-lo faz parte do tipo. O artigo não ignora quem está fisicamente impedido.",
                        "Não transforme esta lição num manual de reanimação. Isso não está na portaria nem no art. 176.",
                    ],
                    pitfalls=[
                        "Achar que ajudar é tirar o capacete ou colocar a vítima no banco de trás.",
                        "Confundir preservar o local com abandonar a vítima sem chamar socorro.",
                    ],
                    memorize=["176: socorro, segurança do local, preservação, remoção só se determinada, identificação.", "Não remover o capacete. Não movimentar a vítima de qualquer jeito."],
                    sources=[{"title": "CTB, art. 176", "url": CTB}, {"title": "Portaria 923/2025, o que não fazer em primeiros socorros", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-socorro-1", "Art. 176, em uma frase", "No sinistro com vítima, quem pode deve socorrer ou providenciar socorro, proteger o tráfego, preservar o local, identificar-se e só remover o veículo se a autoridade determinar.", CTB),
                    card("cnh-card-socorro-2", "O que a portaria manda não fazer", "Não movimentar a vítima de forma incorreta e não remover o capacete.", PORTARIA),
                ],
                [
                    q(
                        "cnh-meio-socorro-01",
                        "meio-ambiente",
                        "socorros",
                        "O condutor envolveu-se em sinistro com vítima, está em condições de agir e deixa o local sem prestar nem providenciar socorro. Qual é a infração do art. 176?",
                        [
                            ("Gravíssima, com multa de cinco vezes e suspensão do direito de dirigir.", "Os incisos I a V compartilham essa penalidade. O enunciado cobre o inciso I. Há ainda recolhimento do documento como medida administrativa."),
                            ("Média, porque ele não causou outra infração de velocidade.", "A natureza não depende de haver excesso de velocidade junto. O caput do art. 176 já classifica a omissão."),
                            ("Não há infração se outra pessoa no local puder telefonar depois.", "O tipo exige que ele preste ou providencie, podendo fazê-lo. A possibilidade de um terceiro qualquer não está escrita como excludente."),
                            ("Advertência por escrito, por ser a primeira parada.", "O artigo não oferece advertência. A penalidade é multa quíntupla e suspensão."),
                        ],
                        0,
                        "Sinistro com vítima e o condutor que podia agir vai embora → art. 176, I → gravíssima, multa ×5 e suspensão.",
                        "CTB, art. 176",
                        CTB,
                        2,
                        1,
                    ),
                    q(
                        "cnh-meio-socorro-02",
                        "meio-ambiente",
                        "socorros",
                        "Há um motociclista caído, de capacete, à espera do socorro. A Portaria SENATRAN 923/2025 aponta uma conduta que o condutor não deve ter. Qual é?",
                        [
                            ("Remover o capacete.", "O item de primeiros socorros da portaria lista a remoção do capacete entre o que não fazer, ao lado da movimentação incorreta da vítima."),
                            ("Sinalizar o local e acionar o atendimento.", "Isso está na atuação segura em emergência da mesma portaria. É o que fazer, não o que evitar."),
                            ("Preservar o local para a perícia, se for possível.", "Preservar é dever do art. 176, III, e combina com a portaria. Não é a conduta proibida."),
                            ("Manter-se em segurança antes de se aproximar da via.", "Autoproteção é o começo do bloco. A portaria não a trata como erro."),
                        ],
                        0,
                        "Vítima de capacete e a pergunta pelo que não fazer → portaria → não tirar o capacete. Sinalizar e preservar são o outro lado.",
                        "Portaria SENATRAN nº 923/2025, Anexo I, o que não fazer em primeiros socorros",
                        PORTARIA,
                        1,
                        1,
                    ),
                    q(
                        "cnh-meio-socorro-03",
                        "meio-ambiente",
                        "socorros",
                        "Depois de um sinistro com vítima, o condutor quer tirar o veículo do meio da pista imediatamente, sem determinação de policial ou agente. O que o art. 176, IV, indica?",
                        [
                            ("A remoção entra quando policial ou agente da autoridade de trânsito a determina.", "O inciso IV pune quem deixa de remover quando essa determinação existe. Sem a ordem, o inciso III pede preservar o local para polícia e perícia."),
                            ("O veículo deve ser retirado sempre, antes de qualquer autoridade, para não gerar multa de estacionamento.", "Estacionamento não é o artigo do enunciado. A pressa de liberar a faixa pode comprometer a perícia."),
                            ("A preservação do local substitui o socorro à vítima.", "São incisos diferentes. Preservar não dispensa prestar ou providenciar socorro, quando isso for possível."),
                            ("Só a vítima pode autorizar a remoção do veículo.", "O inciso IV fala em policial ou agente, não na vítima."),
                        ],
                        0,
                        "Remover o carro sem ordem, com vítima no local → não é o inciso IV. Preservar é o III. Remover é quando a autoridade manda.",
                        "CTB, art. 176, III e IV",
                        CTB,
                        3,
                        1,
                    ),
                ],
            ),
            topic(
                "ambiente",
                "Ambiente, cidadania e manutenção",
                "meio-ambiente",
                lesson(
                    blocks=[
                        "Na Portaria 923, manutenção do veículo, emissão e condução econômica estão no mesmo bloco dos primeiros socorros. Não são um curso separado de mecânica.",
                        "Cidadania no CTB também é concreta: o art. 72 dá a qualquer pessoa o direito de pedir sinalização e fiscalização por escrito.",
                    ],
                    concepts=[
                        "Manutenção preventiva reduz risco, custo e emissão. A portaria liga conservação do veículo a esse resultado.",
                        "Direção sustentável, no mesmo anexo, inclui poluição atmosférica e sonora, condução ecológica e planejamento do trajeto.",
                        "O art. 65 torna obrigatório o cinto para condutor e passageiros em todas as vias, salvo situação regulamentada pelo CONTRAN.",
                    ],
                    examples=[
                        "Pneu gasto e luz de freio apagada não são só um prejuízo. A portaria trata a falta de manutenção como risco e como emissão.",
                        "Um morador pode pedir, por escrito, sinalização numa esquina. O órgão tem de analisar e responder, art. 73.",
                    ],
                    comparisons=[
                        {"left": "Manutenção preventiva", "right": "Condução econômica", "difference": "Uma cuida do estado do veículo. A outra cuida do modo de usar o motor e o trajeto. As duas estão no bloco de meio ambiente da portaria."},
                        {"left": "Cinto obrigatório", "right": "Cinto só em rodovia", "difference": "O art. 65 fala em todas as vias do território nacional, com ressalva só do que o CONTRAN regulamentar."},
                    ],
                    relations=["Enunciado sobre emissão ou conservação → bloco da portaria. Enunciado sobre pedir uma faixa na rua → arts. 72 e 73. Enunciado sobre cinto em via local → art. 65."],
                    rules=[
                        "Não crie percentual oficial de emissão. A portaria não fixa um número para a prova.",
                        "O cinto não depende de a via ser urbana ou rural.",
                    ],
                    pitfalls=[
                        "Tratar mecânica básica como matéria fora do quarto bloco oficial.",
                        "Limitar o cinto à estrada.",
                    ],
                    memorize=["Cinto em todas as vias, art. 65.", "Manutenção e emissão estão no mesmo bloco da portaria.", "Pedir sinalização por escrito é direito, art. 72."],
                    sources=[{"title": "CTB, arts. 65, 72 e 73", "url": CTB}, {"title": "Portaria 923/2025, meio ambiente e primeiros socorros", "url": PORTARIA}],
                ),
                [
                    card("cnh-card-cinto", "Onde o cinto é obrigatório?", "Em todas as vias do território nacional, salvo situação regulamentada pelo CONTRAN (art. 65).", CTB),
                    card("cnh-card-cidadao", "Quem pode pedir sinalização?", "Qualquer cidadão ou entidade civil, por escrito (art. 72). O órgão responde por escrito (art. 73).", CTB),
                ],
                [
                    q(
                        "cnh-meio-amb-01",
                        "meio-ambiente",
                        "ambiente",
                        "O art. 65 torna o cinto de segurança obrigatório para condutor e passageiros em que vias?",
                        [
                            ("Em todas as vias do território nacional, salvo situação regulamentada pelo CONTRAN.", "O artigo não restringe a obrigação à rodovia. A exceção é a que o CONTRAN regulamentar, não o juízo do condutor."),
                            ("Somente em rodovias federais.", "Via urbana também entra. O texto diz todas as vias."),
                            ("Somente para o condutor. O passageiro de trás escolhe.", "O artigo nomeia condutor e passageiros."),
                            ("Somente à noite ou sob chuva.", "Clima e hora não estão no art. 65. Essas condições aparecem na regra de luz baixa."),
                        ],
                        0,
                        "Cinto no enunciado → art. 65 → todas as vias, condutor e passageiros. Não importe a regra do farol.",
                        "CTB, art. 65",
                        CTB,
                        1,
                        1,
                    ),
                    q(
                        "cnh-meio-amb-02",
                        "meio-ambiente",
                        "ambiente",
                        "Pelo Anexo I da Portaria 923/2025, a manutenção preventiva do veículo aparece em que parte do curso teórico de primeira habilitação?",
                        [
                            ("No bloco de meio ambiente e primeiros socorros, ligada a risco, custo e emissão.", "O item 6 desse bloco fala em conservação, prevenção de riscos e redução de custos e emissões. Não há, na portaria, um quinto bloco chamado mecânica."),
                            ("Num bloco autônomo de mecânica, com carga horária própria para a primeira habilitação.", "A portaria não cria esse bloco nem carga horária mínima para o curso teórico de primeira habilitação. A carga horária mínima desse curso é inexistente."),
                            ("Apenas no curso especializado de produtos perigosos.", "Produtos perigosos têm conteúdo próprio. A manutenção preventiva da primeira habilitação está no bloco citado."),
                            ("Fora do exame, porque o DETRAN/AL só avalia legislação e direção.", "A página do DETRAN/AL resume temas, mas o programa do curso é o anexo da portaria. Manutenção está nele."),
                        ],
                        0,
                        "Pergunta sobre onde a manutenção entra no curso novo → quarto bloco da Portaria 923, não a grade antiga de cinco matérias.",
                        "Portaria SENATRAN nº 923/2025, Anexo I, meio ambiente e primeiros socorros, item 6",
                        PORTARIA,
                        2,
                        1,
                    ),
                    q(
                        "cnh-meio-amb-03",
                        "meio-ambiente",
                        "ambiente",
                        "Um morador quer que o órgão de trânsito avalie uma faixa de pedestres numa esquina. O que o art. 72 garante?",
                        [
                            ("O direito de solicitar isso por escrito, inclusive sinalização e fiscalização.", "O artigo alcança qualquer cidadão ou entidade civil. O art. 73 obriga o órgão a analisar e responder por escrito."),
                            ("O direito de instalar a faixa por conta própria se o órgão demorar.", "Pedir não é autorizar a obra. Sinalização da via é do órgão com circunscrição, como nos arts. 80 e 90."),
                            ("O pedido só pode ser feito por condutor já habilitado.", "O artigo diz todo cidadão ou entidade civil. Habilitação não é requisito."),
                            ("O pedido substitui o semáforo enquanto não houver resposta.", "Não há essa substituição. A hierarquia do art. 89 continua valendo para o sinal que existir."),
                        ],
                        0,
                        "Cidadão pede faixa → art. 72 → pedido escrito. Não é licença para pintar a rua.",
                        "CTB, arts. 72 e 73",
                        CTB,
                        1,
                        1,
                    ),
                ],
            ),
        ],
    )


def procedimentos():
    return module(
        "procedimentos-al",
        "Exame em Alagoas",
        "Regras nacionais do exame e o que a página do DETRAN/AL informa sobre o procedimento. Este módulo não entra na distribuição do simulado.",
        0,
        "Procedimento estadual, fora dos quatro blocos de conteúdo",
        [
            topic(
                "formato-exame",
                "Formato do exame teórico",
                "procedimentos-al",
                lesson(
                    blocks=[
                        "A Resolução CONTRAN 1.020/2025, em vigor desde a publicação em 09/12/2025, fixa o formato nacional do exame.",
                        "Em Alagoas, a página da CNH do Brasil no DETRAN, lida em 27/10/2026, diz que o curso teórico é gratuito no aplicativo e que a prova é em local definido pelo DETRAN, com um reteste gratuito.",
                        "Esta plataforma prepara. Não marca o exame, não certifica e não garante aprovação.",
                    ],
                    concepts=[
                        "30 questões, quatro alternativas, uma correta.",
                        "Aprovação com 20 acertos. A regra antiga de 21 não está na resolução vigente.",
                        "Duração mínima de uma hora, dobrada para dislexia, TDAH ou TEA.",
                        "A distribuição das 30 questões por tema não foi publicada. O simulado desta plataforma avisa que a mistura dele é estimativa pedagógica.",
                    ],
                    examples=[
                        "19 acertos não aprovam. 20 aprovam.",
                        "A segunda tentativa pode ser feita sem taxa adicional, art. 34, § 1º. A página do DETRAN/AL confirma um reteste gratuito na prova teórica e na prática.",
                    ],
                    comparisons=[
                        {"left": "Curso teórico", "right": "Prova teórica", "difference": "O curso pode ser feito no aplicativo. A página do DETRAN/AL descreve a prova em local definido pelo órgão, com agendamento no portal."},
                        {"left": "20 acertos", "right": "21 acertos", "difference": "21 era referência de norma anterior. A Resolução 1.020, art. 34, exige vinte."},
                    ],
                    relations=["Número de questões, nota ou tempo → resolução. Onde fazer e como agendar em Alagoas → página do DETRAN/AL."],
                    rules=[
                        "Não use simulados da internet como fonte do número de questões.",
                        "Valor de taxa muda. A página consultada traz números, mas as questões deste curso não cobram decoreba de preço.",
                    ],
                    pitfalls=[
                        "Estudar pela regra revogada de 21 acertos.",
                        "Achar que o curso gratuito no aplicativo dispensa o exame.",
                    ],
                    memorize=["30 questões, 20 acertos, mínimo de 1 hora.", "Reteste gratuito na segunda tentativa.", "Curso no aplicativo não é o exame."],
                    sources=[
                        {"title": "Resolução CONTRAN nº 1.020/2025, arts. 31, 33 e 34", "url": RESOLUCAO},
                        {"title": "DETRAN/AL, CNH do Brasil", "url": DETRAN},
                    ],
                ),
                [
                    card("cnh-card-exame-1", "Formato nacional vigente", "30 questões, 4 alternativas, 20 acertos, duração mínima de 1 hora (Resolução 1.020/2025).", RESOLUCAO),
                    card("cnh-card-exame-2", "O que a página do DETRAN/AL confirma", "Curso teórico gratuito no aplicativo, prova em local definido pelo DETRAN e um reteste gratuito.", DETRAN),
                ],
                [
                    q(
                        "cnh-proc-exame-01",
                        "procedimentos-al",
                        "formato-exame",
                        "Pela Resolução CONTRAN nº 1.020/2025, o que é exigido para aprovação no exame teórico?",
                        [
                            ("20 acertos numa prova de 30 questões, com quatro alternativas e uma correta.", "O art. 31 fixa quatro alternativas e uma correta. O art. 33, § 1º, fixa trinta questões. O art. 34 fixa vinte acertos."),
                            ("21 acertos em 30 questões.", "Vinte e um não é o art. 34 da resolução vigente. Era referência de regra anterior, revogada no conjunto da Resolução 789/2020 pelo art. 140."),
                            ("70% de uma prova de 40 questões.", "Nem o tamanho nem a conta batem com os artigos 33 e 34."),
                            ("15 acertos, desde que o curso no aplicativo esteja completo.", "Concluir o curso não reduz a nota. O art. 23 da mesma resolução diz que o certificado do curso não prova domínio."),
                        ],
                        0,
                        "Formato do exame → arts. 31, 33 e 34 da Resolução 1.020. Não voltar para 21 acertos.",
                        "Resolução CONTRAN nº 1.020/2025, arts. 31, 33 e 34",
                        RESOLUCAO,
                        1,
                        0,
                    ),
                    q(
                        "cnh-proc-exame-02",
                        "procedimentos-al",
                        "formato-exame",
                        "Segundo a página da CNH do Brasil no DETRAN/AL, consultada em 27/10/2026, o que acontece depois da reprovação na prova teórica?",
                        [
                            ("Há um reteste gratuito dessa prova.", "A página informa um reteste gratuito para a prova teórica e outro para a prática. O art. 34, § 1º, da resolução também permite a segunda tentativa sem taxa adicional."),
                            ("O candidato reinicia o curso teórico pago no CFC, porque o gratuito não serve para reteste.", "A mesma página diz que o curso teórico é gratuito no aplicativo. Não condiciona o reteste a um curso pago."),
                            ("A reprovação encerra o processo de habilitação no estado.", "A resolução permite novas avaliações, sem limite de tentativas. A gratuidade citada é a da segunda."),
                            ("A prova seguinte passa a ter 21 acertos como nota mínima.", "A nota não muda por causa da reprovação. Continua o art. 34."),
                        ],
                        0,
                        "Reprovação em Alagoas, na página oficial → um reteste gratuito. A nota continua sendo 20.",
                        "DETRAN/AL, página CNH do Brasil, consultada em 2026-10-27; Resolução CONTRAN 1.020/2025, art. 34, § 1º",
                        DETRAN,
                        1,
                        0,
                    ),
                ],
            )
        ],
    )


MODULES.extend([infracoes(), circulacao(), meio(), procedimentos()])


def main() -> None:
    out = Path(__file__).resolve().parent / "data" / "modules"
    out.mkdir(parents=True, exist_ok=True)
    for item in MODULES:
        target = out / f"{item['id']}.json"
        target.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        print(target.name, "questões", sum(len(topic["questions"]) for topic in item["topics"]))


if __name__ == "__main__":
    main()

