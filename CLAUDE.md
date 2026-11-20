# Sub Tuum Praesidium — guia para o Claude Code

App pessoal do Gabriel para viver a fé católica segundo a Tradição.
Nome tirado da oração mariana mais antiga: *Sub tuum praesidium* ("À vossa proteção recorremos").

Este arquivo é a fonte da verdade para qualquer sessão do Claude Code que continue o projeto.
Leia tudo antes de mexer no código.

---

## 1. Princípios (não quebrar)

1. **Uso pessoal.** Um único usuário. Não há login, nem multiusuário, nem loja.
2. **Calendário tradicional.** A referência é o Missal Romano de 1962 (rubricas de 1960).
3. **Respeito pela situação do usuário.** O Gabriel frequenta a Missa nova com um pároco
   que ele considera muito bem formado e piedoso, porque não há Missa tradicional perto de casa.
   O app **nunca** deve pressioná-lo ou culpá-lo por isso. Ele complementa: Próprio tradicional
   do domingo em casa, comunhão espiritual, terço em família e idas ocasionais à Missa tradicional.
4. **Penitências moderadas e discretas.** Penitências maiores só com o confessor. O app sempre diz isso.
5. **Duas colunas no jejum.** Mostrar sempre lado a lado a **lei atual** (CIC 1983 + CNBB) e a
   **disciplina tradicional** (Código de 1917). Nunca misturar as duas.
6. **Não inventar citações** de pessoas reais (Dom Lefebvre, Pe. Paulo Ricardo, Pe. Leonardo Wagner).
   Para conteúdo deles, usar links de busca no YouTube ou textos verificados com fonte.
7. **Estética tradicional mariana.** Azul de lápis-lazúli, ouro, pergaminho, vermelho das rubricas
   (℣ ℟ em vermelho, como nos missais). Imagem da Imaculada (mulher vestida de sol, lua sob os pés,
   coroa de doze estrelas, Ap 12,1) no frontispício e como marca d'água ao fundo.

---

## 2. Tudo o que foi levantado na conversa

### 2.1 Pedidos e contexto do Gabriel

- Quer um app para se guiar na fé católica, com valores tradicionais.
- Contexto pesquisado: FSSPX, IBP (Instituto do Bom Pastor), Instituto Cristo Rei, FSSP e demais
  institutos Ecclesia Dei. Diferença central: a FSSPX tem posição crítica ao Concílio e à Missa nova;
  os institutos Ecclesia Dei estão em comunhão regular com a Santa Sé e reconhecem a validade da Missa nova.
- Escolha de modelo de IA: pensa em **Opus com esforço alto**. Recomendação feita: modelo híbrido.
  - `claude-opus-5-5` com esforço alto para direção espiritual e dúvidas doutrinárias complexas.
  - `claude-sonnet-5-5` ou `claude-haiku-5-5` para tarefas do dia a dia (liturgia do dia, orações, calendário).
  - Ancorar as respostas em fontes: Catecismo de São Pio X, Catecismo Romano (Trento), Suma Teológica.
- Referência de mercado: o app **Mapa do Católico** (Liturgia Diária, Terço guiado, Novenas, Bíblia em 365 dias).
- O app é **só para ele**.
- **Não há Missa tradicional perto de casa.** Continua frequentando a Missa nova; o pároco é muito bom.
- Quer **todos os tempos litúrgicos de sempre**.
- Quer **aviso quando a Quaresma se aproxima**.
- Quer saber **quando é dia de jejum, de abstinência de carne e de penitência**, com **sugestões de penitência**.
- Quer que o app **tire as dúvidas** sobre jejum e abstinência.
- Quer ser **guiado no que fazer a cada dia**.
- Quer uma **aba do terço em latim e em português**, com os **mistérios de cada dia**.
- No **rosário**, quer os mistérios com **explicação de cada meditação**.
- Quer **estética tradicional**, com **imagens de Maria** e **fundo com Nossa Senhora**.
- Quer **nomes de referência**: Dom Marcel Lefebvre, Pe. Leonardo Wagner (Administração Apostólica
  Pessoal São João Maria Vianney), Pe. Paulo Ricardo.
- Quer, **a cada dia, um tema de doutrina para meditar**, com **recomendações de vídeos no YouTube**.

### 2.2 O que "Dom Lefebvre" (interpretação) acrescentou

- O coração do app é a **Missa de sempre**: calendário de 1962 e o **Próprio de cada dia em latim e português**.
- **Doutrina clara**: Catecismo de São Pio X e Catecismo Romano de Trento, em perguntas e respostas.
- **Vida interior**: Santo Rosário, **exame de consciência** antes da confissão, **meditações de Santo Inácio**.
- **Localizar a Missa tradicional**: como não há perto, guardar a mais próxima e lembrar de ir de tempos em tempos.
- **Não ficar muito tempo sem confissão.**
- **Domingo em casa**: ler o Próprio do dia, fazer **comunhão espiritual**, **terço em família**.
- **Espaço para anotar dúvidas** e o que vive na oração, para levar ao confessor ou diretor espiritual.
- **Septuagésima**: três domingos antes da Quaresma, a Igreja já avisa (paramentos roxos).
- Marcar **Quatro Têmporas** e **vigílias**.
- Jejum: mostrar **lei atual** e **disciplina tradicional** lado a lado.
- Penitências **moderadas e discretas**; as maiores, **com o confessor**.
- **Quinze mistérios**: gozosos (segunda e quinta), dolorosos (terça e sexta), gloriosos (quarta, sábado e domingo).
- O que faltava:
  - **Ritmo do dia**: oração da manhã e da noite; **Angelus às 6h, 12h e 18h** com aviso discreto.
  - **Santo do dia** segundo o calendário tradicional.
  - **Leitura espiritual**: um capítulo da *Imitação de Cristo*.
  - **Consagração total a Nossa Senhora** (São Luís de Montfort), com os **33 dias de preparação**.
  - Acompanhar **primeiras sextas-feiras** e **primeiros sábados**.
  - **Reinado Social de Nosso Senhor Jesus Cristo**: a fé na família, no trabalho e na sociedade.
  - **Rezar todos os dias pelos sacerdotes**, a começar pelo pároco.

---

## 3. O que o protótipo (`index.html`) já faz

Arquivo único, HTML + CSS + JavaScript puro, sem bibliotecas. Abre no navegador.

| Aba (`#hash`) | Conteúdo |
|---|---|
| `#hoje` | Dia litúrgico (1962), cor, classe, santo, tempo; avisos (Advento, Septuagésima, Quaresma, Têmporas); jejum de hoje nas duas disciplinas; roteiro do dia com marcação; Angelus seguinte; tema de meditação + links do YouTube; capítulo da *Imitação*; penitência sugerida; intenção; próximas datas |
| `#missa` | Próximo domingo, como seguir o Próprio em casa, comunhão espiritual, Missa tradicional mais próxima (anotação), última confissão |
| `#rosario` | 15 mistérios com passagem bíblica, meditação e fruto; escolha do dia; latim / português / lado a lado; **terço guiado passo a passo** (78 passos) |
| `#calendario` | Mês com cor litúrgica de cada dia e marcas de jejum, Têmporas e vigílias; detalhe do dia |
| `#jejum` | Regras atuais × tradicionais, idades, jejum eucarístico, próximos dias de jejum, lista de penitências |
| `#oracoes` | Manhã, Angelus/Regina Caeli (troca sozinho no Tempo Pascal), noite com exame de consciência, marianas, defuntos, sacerdotes |
| `#devocoes` | Consagração de Montfort (33 dias, com fases), primeiras sextas (9) e primeiros sábados (5), Reinado Social |
| `#caderno` | Notas para o confessor / diretor espiritual |
| `#mestres` | Dom Lefebvre, Pe. Paulo Ricardo, Pe. Leonardo Wagner (links de busca no YouTube) e fontes |

### Estrutura do script (procure pelos cabeçalhos `/* === ... === */`)

1. `DADOS` — `SANTORAL` (texto `MM-DD|nome|classe|cor|L`), `MISTERIOS`, `ORACOES`, `TEMAS`, `PENITENCIAS`, `EXAME`.
2. `DATAS` — `pascoa(ano)`, `advento1(ano)`, `datas(ano)` (todas as datas móveis, Têmporas, vigílias).
3. `MOTOR LITÚRGICO` — `tempo(d)`, `nomeDomingo`, `nomeFeria`, `diaLiturgico(d)` com precedência simplificada.
4. `JEJUM` — `jejumAtual(d)` e `jejumTradicional(d)`.
5. `ARMAZENAMENTO` — `store.get/set` com `localStorage` (prefixo `stp:`), sempre em `try/catch`.
6. `TELAS` — uma função `render<Aba>()` por aba; roteador pelo `location.hash`.

Classes: 1 a 3 = classes de 1962; 4 = comemoração ou féria simples.
Cores: `v` violeta, `w` branco, `g` verde, `r` vermelho, `p` rosa, `n` preto.

---

## 4. Limitações conhecidas (corrigir no app real)

- **Precedência litúrgica simplificada.** Conferir com um Ordo de 1962 (FSSP, IBP ou FSSPX).
  Casos a revisar: domingos "retomados" da Epifania depois do 23º domingo depois de Pentecostes,
  transferências (São José e Anunciação na Semana Santa), Têmporas × festas de 2ª classe.
- **Santoral** cobre as festas principais de cada mês, não todas as comemorações.
- **Próprio da Missa** ainda não está no app: há link para o Divinum Officium. Para embutir os textos,
  usar o latim (domínio público) e verificar a licença de qualquer tradução em português.
- **Imitação de Cristo**: o app indica livro e capítulo, mas não traz o texto. Usar tradução em domínio público.
- **Notificações do Angelus** não funcionam no protótipo (o navegador bloqueia). No app real, usar notificação push.
- **Dados ficam no navegador** (`localStorage`). Se limpar os dados do navegador, as anotações somem.
- **CNBB e abstinência às sextas**: o app diz para confirmar com o pároco a norma complementar que
  permite trocar a abstinência das sextas comuns por outra penitência. Verificar o texto oficial.

---

## 5. Próximos passos sugeridos (em ordem)

1. **Virar PWA** (Progressive Web App): instala no celular, funciona sem internet, permite notificações.
   - `manifest.json`, ícones, `service-worker.js` com cache do app.
   - Notificações locais: Angelus 6h/12h/18h, véspera de dia de jejum, 7 dias antes da Septuagésima,
     Cinzas, Têmporas e primeiras sextas/sábados.
2. **Separar dados em arquivos JSON** (`data/santoral.json`, `data/oracoes.json`, `data/temas.json`)
   para facilitar revisão.
3. **Santoral completo de 1962** e precedência exata, com testes (ver seção 6).
4. **Próprio da Missa** de domingos e festas (latim + português).
5. **Catecismos em perguntas e respostas** (São Pio X; Romano de Trento), com busca.
6. **Exercícios Espirituais de Santo Inácio**: roteiro de meditação (preparação, pontos, colóquio).
7. **Novenas** e plano de leitura bíblica (como no Mapa do Católico), na tradução que o usuário escolher.
8. **Assistente de IA** (opcional), com a API da Anthropic:
   - doutrina e direção espiritual → `claude-opus-5-5`, esforço alto;
   - perguntas rápidas do dia → `claude-sonnet-5-5` ou `claude-haiku-5-5`;
   - prompt de sistema que obriga a citar catecismo ou fonte, distingue lei atual de disciplina
     tradicional e manda questões de consciência ao confessor;
   - conferir parâmetros e preços atuais em https://docs.claude.com antes de implementar.
   - A chave da API **nunca** vai no front-end: usar um pequeno servidor ou função serverless.

---

## 6. Testes mínimos do motor litúrgico

Casos que devem passar (ano → resultado esperado):

- `pascoa(2026)` = 5 de abril; `pascoa(2027)` = 28 de março.
- `advento1(2026)` = 29 de novembro de 2026.
- Septuagésima de 2027 = 24 de janeiro de 2027; Cinzas de 2027 = 10 de fevereiro de 2027.
- Têmporas do Advento de 2026 = 16, 18 e 19 de dezembro.
- 19/11/2026 → Santa Isabel da Hungria (3ª classe, branco), Tempo depois de Pentecostes.
- 22/11/2026 → Último Domingo depois de Pentecostes (verde).
- 08/12/2026 → Imaculada Conceição (1ª classe, branco).
- Sexta-feira Santa → jejum e abstinência nas duas disciplinas.
- Qualquer segunda-feira da Quaresma → jejum só na disciplina tradicional.
