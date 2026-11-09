# Roadmap

Próximos passos para o perfil e para os repositórios que ele mostra. Cada item tem um plano próprio, para ser retomado sem depender de contexto anterior.

Escrito em novembro de 2026, depois dos PRs #20 a #35, que refizeram a parte do README abaixo do ouriço. Esses PRs deixaram a faixa de números coerente, os cards com a mesma estrutura, a Toolbox em SVG com logos, o contato com botões e LinkedIn, o ouriço no rodapé, o tamanho correto no celular e as checagens semanais de links e números.

## Como usar este documento

- **Um item, um ou mais PRs pequenos.** Cada PR integrado conta para o Pull Shark, e PRs pequenos são mais fáceis de revisar.
- **Empilhar PRs** (um com base na branch de outro): integre o de baixo e espere o de cima mostrar `main` como base antes de integrá-lo. Se for integrado segundos antes, o de cima cai na branch apagada e nunca chega ao `main` (foi o que aconteceu com o #25, depois reenviado como #28).
- **Depois de cada mudança visível**, confira o perfil publicado (desktop e celular, claro e escuro). O GitHub guarda as imagens em cache e alguns erros só aparecem lá.
- Ao concluir um item, marque-o na tabela abaixo e apague o plano dele (o histórico fica no git).

## Prioridades

| # | Item | Onde | Esforço | Depende de |
|---|------|------|---------|------------|
| A1 | Dashboard roda a partir de um clone | Dashboard | pequeno | arquivo `.kml` |
| A2 | README do Dashboard | Dashboard | médio | A1 |
| A3 | Limpeza do Dashboard (notebook alheio, versões) | Dashboard | pequeno | sua decisão |
| A4 | Publicar o Dashboard online | Dashboard + perfil | médio | A1, A3 |
| A5 | README da pesquisa com resultados | Pesquisa | médio | — |
| A6 | Dados e reprodutibilidade da pesquisa | Pesquisa | pequeno | sua decisão |
| A7 | Resumo em inglês do monitor | Monitor | pequeno | — |
| A8 | Descrição, tópicos e imagem de prévia dos repositórios | os três | pequeno | sua permissão |
| A9 | Fixar os três projetos no perfil | GitHub (você) | mínimo | — |
| B1 | Ouriço do rodapé se despedindo | perfil | médio | arte aprovada |
| B2 | Novos comportamentos na faixa do ouriço | perfil | médio cada | arte, para poses novas |
| B3 | Ouriço reagindo ao tema escuro | perfil | médio | B2 |
| B4 | Variantes sazonais do ouriço | perfil | médio | decisão sobre a build |
| C1 | Card do projeto de ECG | perfil | médio | projeto público |
| C2 | Rotina para atualizar "Agora / Explorando" | perfil | pequeno | — |
| C3 | Seção de publicações e apresentações | perfil | pequeno | conteúdo |
| C4 | Células da faixa com contribuições reais | perfil | grande | decisão sobre a build |
| D1 | Teste de contraste das cores | perfil | pequeno | — |
| D2 | Hero mais leve | perfil | pequeno | — |
| D3 | Teste de paridade entre os READMEs | perfil | pequeno | — |
| D4 | Galeria de prévia para revisar PRs | perfil | pequeno | — |
| D5 | Ações do CI fixadas por commit e atualizadas | perfil | pequeno | — |
| E1 | Conquistas do GitHub | — | contínuo | — |

Ordem sugerida: A9, A1, A2, A3, A5, A8, B1, D1, D2, depois o resto conforme interesse.

---

## A. Repositórios dos projetos

Quem clica num card cai nesses repositórios. Hoje a experiência cai bastante entre o perfil e eles.

### A1. Dashboard roda a partir de um clone

**Objetivo.** `streamlit run DFOSP.py` funciona em qualquer máquina logo depois do `git clone`.

**Por quê.** O `DFOSP.py` lê `D:\FOSP\colo_utero1.csv` e `D:\FOSP\sp_drs_group_interactive.kml`, caminhos do seu computador. O CSV está no repositório, mas o app procura no `D:`. O `.kml` com o mapa das 17 regiões (DRS) não está no repositório.

**Plano.**
1. Adicionar `sp_drs_group_interactive.kml` ao repositório, se puder ser público, numa pasta `data/` junto do CSV.
2. Trocar os caminhos fixos por caminhos relativos ao script: `Path(__file__).parent / "data" / ...`.
3. Usar `@st.cache_data` na leitura, se ainda não estiver em uso, para o app abrir rápido.
4. Rodar localmente num clone limpo, em outra pasta, e conferir que o mapa e os gráficos aparecem.

**PRs.** `fix: load the data and the map from the repository` (move os arquivos e corrige os caminhos).

**Decisão sua.** Mandar o `.kml` e confirmar que ele pode ser público. Se não puder, o mapa vira opcional e o app mostra um aviso quando o arquivo não existir.

**Atenção.** O check semanal de números (`scripts/check_numbers.py` no perfil) lê `colo_utero1.csv` e `DFOSP.py` na raiz do Dashboard. Se os arquivos mudarem de lugar, atualize as constantes `CSV` e `APP` do script no mesmo dia, ou o job de segunda-feira falha.

### A2. README do Dashboard

**Objetivo.** Quem chega pelo card entende o projeto em 10 segundos e consegue rodá-lo em 2 minutos.

**Plano.** README em português com resumo em inglês, contendo:
1. Título e uma frase: o que é e para quem.
2. Captura de tela do app (PNG em `docs/`), com os filtros e o mapa.
3. Números principais, os mesmos do card: 55.647 registros, 2000–2023, 17 regiões, sobrevida de Kaplan–Meier em 36 meses, 3 filtros.
4. Como rodar: `pip install -r requirements.txt` e `streamlit run DFOSP.py`.
5. Dados: origem (FOSP, dados públicos), o que cada coluna usada significa (`ANODIAG`, `ECGRUP`, `ULTINFO`, `nDRS`) e o atraso de registro de 2023.
6. Link de volta para o perfil.

**PRs.** `docs: add a README with a screenshot, how to run and the data source`.

**Depende de A1**, para o "como rodar" ser verdade.

### A3. Limpeza do Dashboard

**Plano.**
1. Remover `01_the_machine_learning_landscape.ipynb`, que parece ser o capítulo 1 do livro *Hands-On Machine Learning* e não faz parte do projeto. Se você quiser guardá-lo, mova para um repositório de estudos.
2. Fixar versões no `requirements.txt`, testando num ambiente limpo.
3. Trocar a descrição "Dashboard-FOSP" (ver A8).

**PRs.** `chore: remove an unrelated notebook` e `build: pin the app's dependencies`.

**Decisão sua.** Confirmar a remoção do notebook.

### A4. Publicar o Dashboard online

**Objetivo.** Um link "Abrir app", no README do Dashboard e no card do perfil, que funciona sem instalar nada.

**Plano.**
1. Publicar no Streamlit Community Cloud (gratuito, ligado ao repositório). Você cria a conta e conecta o repositório; eu preparo o que o app precisa.
2. Conferir o limite de memória: o CSV tem 11 MB e o app calcula Kaplan–Meier por região.
3. No perfil: acrescentar o link à linha sob o card do Dashboard ("Python · Streamlit · … · Repositório · Abrir app"), nos dois READMEs. O `check_links.py` passa a verificá-lo toda semana.

**Depende de A1 e A3.**

### A5. README da pesquisa com resultados

**Objetivo.** O topo do README mostra o resultado antes da metodologia.

**Por quê.** O README atual explica bem os notebooks, mas não mostra C-index, número de pacientes nem hazard ratios. Também não usa `Figuras/COX.png`, que já existe.

**Plano.**
1. Bloco de abertura: uma frase sobre a pergunta ("quem sobrevive ao câncer colorretal, e por quê?"), os números (37.499 pacientes, 22.078 óbitos, C-index 0,747) e a figura. `COX.png` tem 2,6 MB; gere uma versão menor para o README.
2. Tabela com os 7 hazard ratios do card, com IC 95%, e a nota "associações ajustadas, não efeitos causais".
3. Manter a descrição atual dos notebooks, mais abaixo.
4. Resumo em inglês no topo (3–4 frases).
5. Link de volta para o perfil.

**PRs.** `docs: open the README with the results and the hazard ratio figure`, depois `docs: add an English summary`.

**Verificação.** Os números saem dos mesmos lugares que `scripts/check_numbers.py` lê. Confira com ele antes de publicar.

### A6. Dados e reprodutibilidade da pesquisa

**Plano.**
1. Seção "Dados": de onde vem a base da FOSP, como obter e qual versão foi usada (o notebook de Kaplan–Meier cita a base de dezembro de 2023).
2. Seção "Como rodar": Colab, com a ordem dos notebooks.
3. Licença. MIT, por exemplo, para o código. Os dados da FOSP seguem os termos da fonte.
4. Opcional: renomear os notebooks sem espaços e acentos. Isso quebra links antigos: atualize o README do perfil, o `SOURCES.md` e as constantes do `check_numbers.py` no mesmo dia.

**Decisão sua.** A licença, e se vale renomear os arquivos.

### A7. Resumo em inglês do monitor

O README do `codex-reset-monitor` já é completo, em português. Falta só um resumo de 3–4 frases em inglês no topo, para visitantes de fora.

**PRs.** `docs: add an English summary`.

### A8. Descrição, tópicos e imagem de prévia dos repositórios

**Objetivo.** A seção "Pinned" e a busca do GitHub mostram uma frase útil e tópicos em cada projeto.

**Plano.**
1. Descrições curtas, nos dois idiomas ou só em inglês:
   - Pesquisa: "Cox regression and Kaplan–Meier survival analysis on São Paulo's cancer registry (FOSP)".
   - Dashboard: "Streamlit dashboard of cervical cancer cases and survival in São Paulo (FOSP)".
   - Monitor: "Free, LLM-free monitor that alerts Discord about Codex usage resets".
2. Tópicos: `survival-analysis`, `cox-regression`, `kaplan-meier`, `lifelines`, `streamlit`, `plotly`, `geopandas`, `healthcare`, `github-actions`, `cloudflare-workers`, `discord`, conforme o projeto.
3. Opcional: imagem de prévia social (1280×640) para cada repositório, gerada com o mesmo estilo dos cards. Pode ser um `cards.py` com outro tamanho.
4. Aplicar com `gh repo edit --description ... --add-topic ...`.

**Decisão sua.** Isso altera conteúdo público dos repositórios: preciso do seu ok para cada um. A imagem de prévia só pode ser enviada pela interface do GitHub (Settings → Social preview); isso fica com você.

### A9. Fixar os três projetos no perfil

A seção "Pinned", logo abaixo do README, mostra dois repositórios do FFCfelps1. No perfil, use "Customize your pins" e escolha Predicao-da-Sobrevida, Dashboard e codex-reset-monitor, os três dos cards. Os outros dois podem continuar, se houver espaço (são até 6).

---

## B. Ouriço

As poses ficam em `scripts/hedgehog.py`: grades de caracteres de 27×20, olhando para a direita. A rotina da faixa é o `SCRIPT` declarativo em `build_assets.py`. Um comportamento que reaproveita poses é uma entrada nova no `SCRIPT`. Uma pose nova é um frame em `hedgehog.py`, uma entrada em `POSES` e um desenho no dicionário `art` de `strip()`. O ouriço foi desenhado por você: **toda pose nova precisa da sua aprovação da arte** antes do PR. Eu proponho o frame, mostro ampliado e ajusto.

### B1. Ouriço do rodapé se despedindo

**Objetivo.** O ouriço do fim da página (`rest()`, `assets/strip/rest-*.svg`) se despede de quem chegou ao final, em vez de só piscar.

**Plano.**
1. **Arte.** Dois ou três frames novos a partir do frame em pé (`FRAMES[0]`): a pata dianteira levantada em alturas diferentes, para um aceno. A cor `f` ("raised paw") já existe na paleta. Opcional: um frame com os olhos fechados e um sorriso, para o fim do aceno.
2. **Roteiro** (ciclo de uns 8 s): parado, pisca, acena 3 vezes (uns 0,25 s por frame, indo e voltando), fica com a pata levantada um instante, volta à pose parada.
3. **Implementação.** Em `rest()`: um grupo por frame de aceno, com keyframes de opacidade, no mesmo padrão dos `wf{i}` da caminhada. O frame em pé fica por baixo. Mantém o espelhamento (olhando para a página).
4. **Movimento reduzido.** A pose parada continua sendo a visível (olhos abertos), sem aceno. O `base_css` já para tudo.
5. **Opcional:** um balão pequeno "tchau!" / "bye!" ao lado. Isso tornaria o SVG dependente de idioma (`rest-en-*`, `rest-pt-*`) e faria o texto passar pela checagem de 12 px.
6. **Textos.** Atualizar o alt nos dois READMEs ("…se despede acenando…") e o `SOURCES.md`.
7. **Testes.** Um teste em `test_strip.py` garantindo que os frames de aceno mantêm os pés plantados (mesma linha de base do frame em pé), como os testes de `recovery()`.

**Verificação.** `preview.py` em 4 ou 5 instantes do ciclo, no claro e no escuro, mais `--reduced`.

**PRs.** `feat: draw the hedgehog's waving frames` (só a arte, com teste) e `feat: wave goodbye at the end of the page`.

### B2. Novos comportamentos na faixa do topo

Cada um é um PR. Os marcados com *poses existentes* são só uma entrada nova no `SCRIPT`.

| Comportamento | Descrição | Poses |
|---|---|---|
| Cheirar o chão | para no meio, abaixa a cabeça sobre uma célula, a célula acende forte | nova: cabeça baixa |
| Bocejo | parado, abre a boca, pisca devagar | nova: boca aberta |
| Cochilo enrolado | rola até parar, fica em bola, sobe um "z" pequeno, desenrola | existentes (bola) + um "z" desenhado |
| Pulinho | um salto curto no lugar, como o `hop` do ricochete | existentes (`hop`) |
| Espreguiçar | estica o corpo para frente e para trás | nova: corpo alongado |
| Olhar para cima | levanta o focinho como se visse algo no topo da página | nova: focinho para cima |

**Plano geral de cada um.**
1. Definir o roteiro com `Hold`, `Leg`, `Look` e `Edge` existentes. Se precisar de pose nova, desenhar o frame (com aprovação), criar o `Pose` e o desenho em `art`.
2. Encaixar no `SCRIPT` sem quebrar o loop contínuo (o ciclo começa onde a última viagem termina).
3. Manter o `STEP` alinhado ao período, como já é feito.
4. As células só acendem com patas no chão. Um comportamento no ar não acende nada.
5. Testes em `test_strip.py`, no estilo de `test_stops_halfway_and_glances_back_before_carrying_on`.
6. Atualizar o alt da faixa nos dois READMEs e a descrição no `SOURCES.md`.

**Atenção.** Cada comportamento aumenta o período do loop. Acima de uns 90 s, quem olha a página pode nunca ver alguns deles. Prefira trocar um comportamento existente a só acrescentar.

### B3. Ouriço reagindo ao tema escuro

No tema escuro, o ouriço poderia ter uma rotina "noturna", com mais cochilos e passos mais lentos, ou uma lua pequena no canto. As variantes `walk-dark*.svg` já são arquivos separados, então dá para ter um `SCRIPT` por tema sem afetar o claro. O plano é o mesmo do B2, com um parâmetro `theme` em `_motion()`.

### B4. Variantes sazonais

Um gorro em dezembro, uma fantasia em outubro.

**Problema.** A build é determinística e o CI exige que o rebuild não mude os assets. Uma variante por data quebraria isso.

**Plano possível.**
1. A variante sazonal é um parâmetro explícito, `SEASON = None | "winter" | ...`, numa constante em `build_assets.py`.
2. Um PR liga a variante no início da estação e outro desliga no fim. São PRs pequenos e previsíveis, e contam para o Pull Shark.
3. Os acessórios são camadas desenhadas por cima do ouriço, como frames extras, sem mexer nas poses.

---

## C. Conteúdo do perfil

### C1. Card do projeto de ECG

**Quando.** Quando o trabalho com ECG puder ser público (a nota "Agora" do topo já fala dele).

**Plano.**
1. Novo builder em `cards.py` (`BUILDERS["ecg"]`), com a mesma estrutura dos outros: eyebrow, título, corpo, 4 números e uma figura. A figura pode ser um traçado de ECG animado em CSS, com a validação médica como destaque.
2. Os números vêm de um arquivo em `scripts/data/` e são documentados no `SOURCES.md`. O `check_numbers.py` passa a recalculá-los a partir do repositório do projeto.
3. Um número dele na faixa de números (a faixa vira 4 colunas, ou o ECG substitui um dos três).
4. Linha de stack e links sob o card, nos dois READMEs. As ferramentas novas entram na Toolbox (o teste `test_project_stacks_are_in_the_toolbox` exige isso).
5. Atualizar a nota "Agora".

### C2. Rotina para atualizar "Agora / Explorando"

As notas do topo (`STATUS_COPY` em `build_assets.py`) envelhecem sem ninguém perceber.

**Plano.**
1. Acrescentar uma data discreta ("atualizado em nov/2026") às notas, ou só ao `SOURCES.md`.
2. Um lembrete trimestral: uma issue aberta por workflow agendado ("Revisar Agora/Explorando"). Você fecha a issue com um PR de atualização.

### C3. Publicações e apresentações

Uma linha ou um bloco pequeno com a iniciação científica (o PDF `PESQUISAS IC.pdf` já está no repositório da pesquisa), apresentações e eventos, com link para o seu Lattes (já está na barra lateral do perfil). Começa como texto em Markdown, no fim de Projetos; vira SVG se crescer.

### C4. Células da faixa com contribuições reais

Hoje as células sob o ouriço são decorativas (`SOURCES.md` diz isso).

**Ideia.** Usar as suas contribuições reais dos últimos meses, via API do GitHub.

**Problema.** Igual ao B4: a build deixaria de ser reproduzível.

**Plano possível.**
1. Um workflow semanal busca as contribuições, grava `scripts/data/contributions.json`, reconstrói a faixa e abre um PR (conta para o Pull Shark).
2. O `strip()` lê os níveis desse arquivo em vez do gerador pseudoaleatório.
3. O CI continua determinístico, porque os dados ficam commitados.

**Decisão sua.** Se vale ter um PR automático toda semana.

---

## D. Qualidade e manutenção

### D1. Teste de contraste das cores

Um teste em `test_assets.py` que calcula o contraste de cada cor de texto (`fg`, `mu`, `fa`, `ac` em `THEMES`) contra o fundo de cada tema e exige 4,5:1 para texto (WCAG AA). As funções `_luminance` e `_contrast` já existem em `build_assets.py`. Se alguma cor falhar, o PR do teste também ajusta a cor.

### D2. Hero mais leve

Cada SVG do hero tem uns 400 KB, por causa dos três ícones em PNG base64. O perfil carrega dois deles (claro ou escuro, mais o mobile, se a largura mudar).

**Plano.**
1. Medir a resolução dos PNGs em `scripts/icons/` contra o tamanho em que aparecem. Provavelmente estão com 2–3× mais pixels do que o necessário.
2. Reduzir em `cut_icons.py` e otimizar os PNGs sem perda.
3. Teste de orçamento: nenhum SVG acima de, por exemplo, 200 KB.

**Verificação.** Comparar com `preview.py` antes e depois, ampliado.

### D3. Teste de paridade entre os READMEs

Um teste que compara a estrutura de `README.md` e `README.pt-BR.md`: mesmas seções, na mesma ordem, os mesmos links externos e as mesmas imagens, com `-en-`/`-pt-` trocados. Evita que uma mudança entre só num idioma.

### D4. Galeria de prévia para revisar PRs

Um script `scripts/gallery.py` que gera uma página HTML com todas as variantes (tema × layout × idioma), lado a lado e nas larguras reais (795 e 293 px). Serve para revisar um PR visual de uma vez, inclusive pelo celular. Opcional: o CI anexa a galeria como artefato do PR.

### D5. Ações do CI fixadas por commit e atualizadas

Os workflows usam `actions/checkout@v7` e `actions/setup-python@v7` por tag. Fixar por SHA de commit, com um comentário da versão, protege contra uma tag movida. O Dependabot (`.github/dependabot.yml`, ecossistema `github-actions`) abre PRs de atualização, que também contam para o Pull Shark.

---

## E. Conquistas do GitHub

| Conquista | Como se ganha | Situação | Plano |
|---|---|---|---|
| Pull Shark | PRs integrados: 2, 16, 128, 1024 | x2 (16+); 120 PRs integrados em novembro de 2026, somando todos os repositórios | faltam 8 para o próximo nível (128). Continuar com um PR por mudança; os itens deste roadmap rendem dezenas |
| YOLO | integrar um PR sem revisão | já tem | — |
| Quickdraw | fechar uma issue ou PR até 5 min depois de abrir | já tem | — |
| Pair Extraordinaire | commit em coautoria com outra pessoa, integrado | não tem | trabalhar com um colega (repositório da disciplina, projeto semestral) com `Co-authored-by` dele |
| Galaxy Brain | resposta aceita em GitHub Discussions | não tem | responder dúvidas em Discussions de bibliotecas que você usa (lifelines, Streamlit) |
| Starstruck | um repositório com 16 estrelas | não tem | consequência de A1–A8: projetos apresentáveis e divulgados |

A coautoria do Pair Extraordinaire precisa ser de uma pessoa. Commits deste repositório não levam coautoria de IA.
