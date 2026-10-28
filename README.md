# Plataforma de estudos adaptativos

Aplicação local para estudar dois cursos com o mesmo motor e progressos separados: inglês e a prova teórica da CNH para Alagoas. O painel mostra só o que já foi respondido. Não há recomendação genérica.

O inglês continua a ser o caderno [word-bank](https://github.com/Danielhlw/word-bank), incluído aqui como submódulo em `vendor/word-bank`. O vocabulário fica em `vendor/word-bank/data/word_bank.db`. O progresso da plataforma fica em `data/platform.db`. Os dois bancos não se misturam, e o progresso de um curso não altera o do outro.

## Estratégia

O ciclo é fechado: lição, prática comentada, medição, revisão do que falhou e nova tentativa.

1. A lição vem antes das questões. Dá para dispensá-la, e essa dispensa fica gravada. Prática, sessão do dia e simulado de um módulo só abrem depois da lição concluída ou dispensada.
2. Cada questão de treino tem quatro alternativas, a explicação de cada uma e o bloco «Como reconhecer este padrão». O histórico guarda o texto da alternativa, a fonte e o identificador estável do tópico.
3. Um erro entra na fila. A questão só sai depois de dois acertos consecutivos. Um acerto isolado não prova domínio, e um erro seguinte zera a sequência. A linha da fila permanece no histórico mesmo depois de sair.
4. Um tópico fica dominado com acerto de pelo menos 80%, no mínimo cinco tentativas com evidência e nenhuma questão desse tópico ainda ativa na fila. Esses três números podem ser ajustados na aplicação. A exigência de dois acertos consecutivos para limpar a fila não desce disso.
5. A sessão do dia tem de 10 a 15 questões (12 por omissão). A escolha privilegia, nesta ordem, o que ainda não foi visto, erros recentes, tópicos abaixo de 80%, revisões vencidas, o que pesa no exame e, por último, uma manutenção do que já está dominado. Se o tópico tiver outra questão ainda não usada, a sessão evita repetir a mesma.
6. O modo estudo mostra a correção na hora. O simulado esconde as respostas até a entrega. Questão em branco, na entrega, conta como erro.
7. O diagnóstico da sessão sai das estatísticas gravadas. A comparação usa a sessão anterior do mesmo tipo.

## Inglês

O adaptador lê o caderno que já existe. Não inventa pronúncia, tradução nem frase. As questões de múltipla escolha só nascem quando há distrações reais no banco, ou a partir das contrações já escritas na revisão. Produzir uma frase fica registado como nota e não entra na fila nem conta como evidência de domínio.

Se `~/Downloads/WORD BANK.xlsx` existir e o banco de vocabulário estiver vazio, a importação original do caderno continua a acontecer. Um banco que já tenha dados não é apagado.

## CNH

As regras do exame vêm da Resolução CONTRAN nº 1.020/2025 e o programa, da Portaria SENATRAN nº 923/2025, Anexo I, com leitura em 27/10/2026. O curso teórico está nos quatro blocos dessa portaria, mais um módulo só de estudo sobre o procedimento em Alagoas. Esse módulo não entra nas 30 questões.

O simulado de treino usa 30 questões, 20 acertos e 60 minutos, ou 120 se o tempo ampliado estiver ligado. A mistura por bloco (sinalização 5, infrações 12, circulação 9, meio ambiente 4) é estimativa pedagógica e está marcada como tal. A distribuição oficial das 30 questões não foi publicada. As questões são originais de treino, com fonte e data em cada item. Isto não é prova oficial e não promete aprovação.

Para mudar o formato, edite `study/courses/cnh/data/exam_config.json`. Para corrigir uma lição ou uma questão, edite o JSON do módulo em `study/courses/cnh/data/modules/`.

## Uso da IA

Não há modelo ligado. A plataforma não pede chave, não chama API e não simula uma resposta de tutor.

O que existe é uma fronteira estreita:

- `study/ai` define um fornecedor (`TutorProvider`). A implementação atual, `UnconfiguredTutor`, está sempre indisponível e devolve a pessoa ao relatório.
- Em Exportar, «Preparar análise com IA» gera um Markdown com o estado real do curso: política de domínio, módulos, fila, sinalizadas, respostas recentes, sessões e a recomendação já calculada pelo motor.
- O ficheiro termina sempre com esta instrução, para colar noutro chat:

> Analisa os dados apresentados. Identifica os padrões de erro, separa dificuldades conceituais de erros ocasionais, propõe uma estratégia de estudo e gera uma lista de ações concretas. Prioriza os tópicos que ainda não estão dominados. Não recomendes repetir conteúdos que já estão estáveis sem uma justificação. Para o ambiente CNH, fundamenta as correções nas fontes normativas verificadas. Devolve um plano estruturado que possa ser aplicado à próxima sessão.

- A exportação JSON e Markdown remove campos cujo nome indique segredo (`api_key`, `token`, `password`, `secret` e equivalentes).
- A importação valida o `schemaVersion` e só substitui o curso que está no ficheiro, depois de uma confirmação explícita.

Para usar a IA, exporte o Markdown do curso e cole-o num chat externo. O plano que voltar fica fora da plataforma até você decidir o que estudar na sessão seguinte. O motor continua a decidir fila, domínio e a próxima sessão a partir das respostas gravadas, não a partir de um texto gerado.

## O que fica gravado

`data/platform.db` guarda respostas, sessões, progresso por tópico, fila de erros, acertos consecutivos, sinalizações, cartões, histórico de simulados, tempo e a versão do conteúdo. Esses bancos locais não entram no Git. JSON e Markdown exportam o curso sem credenciais.

## Instalar

```bash
git clone --recurse-submodules https://github.com/Danielhlw/plataforma-estudos.git
cd plataforma-estudos
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Abre em http://localhost:8501.

Se o clone ficou sem a pasta `vendor/word-bank`:

```bash
git submodule update --init --recursive
```

O caderno também pode ser aberto sozinho, a partir de `vendor/word-bank`:

```bash
streamlit run main.py
```

## Testes

```bash
pytest
```

Cobrem o motor, a fila, a seleção da sessão, o simulado, o isolamento entre cursos, a importação e a exportação, a pontuação e as regras de norma.
