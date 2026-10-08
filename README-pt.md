# dsh-tender-extract — Verificação da tabela de extratos de cláusulas do caderno de encargos (origem e texto original)

`dsh-tender-extract` lê uma tabela de extratos de cláusulas — o cabeçalho do processo mais uma linha por extrato —, aplica um pacote de regras versionado e devolve um relatório sobre essa tabela e só sobre ela: que cada linha indique a sua origem (`sourceRef`), que a coluna do texto original (`rawText`) esteja preenchida, que a exigência destilada (`requirement`) partilhe algum termo com esse texto, que a categoria registada conste da lista da sua instituição, que nenhum número de extrato (`seq`) se repita, que o cabeçalho nomeie o projeto e o documento de origem, e que não reste nenhum marcador de modelo no texto original. O vocabulário de categorias de cláusula vem vazio e, sem nada configurado, `TE-004` declara-se em `skipped` em vez de passar em silêncio.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Um extrato da minha tabela não tem nada na coluna da origem. Isso é reportado? | Sim. `TE-001` exige `sourceRef` em todos os extratos e reporta cada linha em que esteja vazio. Verifica que a origem está registada, nunca que aponta para o lugar certo, e não prova que falta um extrato: a completude só pode ser julgada contra o caderno de encargos completo, que este plugin nunca vê. |
| A coluna do texto original está preenchida — o plugin confirma que coincide palavra a palavra com o caderno de encargos? | `TE-002` verifica apenas que a coluna `rawText` está preenchida. Não compara esse texto com o caderno de encargos; essa comparação exige ter o documento original em mãos. |
| A exigência destilada parece vir de outro sítio completamente. Isso será assinalado? | `TE-003` procura termos partilhados entre `requirement` e `rawText` — bigramas Han sobrepostos e palavras latinas inteiras — e reporta a linha quando não partilham nada. Parafrasear altera legitimamente as palavras, por isso um achado significa que as duas colunas parecem não ter relação e merecem uma vista humana, nunca que a destilação está errada. Também não deteta uma destilação errada que partilhe vocabulário, e o limiar `minShared` de 2 é uma convenção local, não um valor normativo. |
| Ainda não decidimos como classificar as nossas cláusulas. O que acontece à coluna da categoria? | Os valores vêm vazios, por isso `TE-004` declara-se em `skipped` em vez de passar em silêncio até os preencher. Depois de configurado, verifica apenas que o valor registado consta da sua lista; não decide a que categoria pertence uma cláusula. |
| Dois extratos da tabela têm o mesmo número. | `TE-005` compara os valores de `seq` ignorando diferenças de espaçamento e reporta a repetição, porque um número que aparece duas vezes não pode ser citado sem ambiguidade. Não julga se a numeração é sensata no resto. |
| O texto original de um extrato ainda é o do modelo. | `TE-007` reporta a linha cujo `rawText` ainda contém um marcador da lista de fábrica — `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例` — porque um extrato que ainda o traz foi copiado do modelo em vez de preenchido. A lista exclui deliberadamente `（略）`, uma forma legítima de abreviar uma cláusula longa, e só consegue encontrar as palavras dessa lista. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《中华人民共和国招标投标法》 | 1999年8月30日通过，2017年12月27日修正（全国人大常委会《关于修改〈中华人民共和国招标投标法〉、〈中华人民共和国计量法〉的决定》），本法自2000年1月1日起施行 | TE-001, TE-002, TE-003, TE-004, TE-005, TE-006, TE-007 |

**Boundary:** this plugin checks a **招标文件条款摘录表** for what a checklist can be held to — that every
extract gives its source, that the raw clause text is recorded, that the distilled requirement bears some
lexical relation to that text, that the category comes from your vocabulary, that numbers are unique, and that
no placeholder survives.

> ### ⚠️ What this plugin can and cannot do
>
> **It cannot prove that a clause was missed.** Deciding whether an extract is *complete* requires comparing
> against the whole tender document, and **this plugin only ever sees the extract table**. It does not claim
> otherwise, and its rule notes say so: `TE-001` checks that a source is *recorded*, never that the extract is
> exhaustive.
>
> `TE-003` is the only content judgement here, and it is deliberately weak. It looks for **shared terms**
> between the raw text and the distilled requirement, using overlapping Han bigrams and whole Latin words, and
> reports only when the two share **nothing**. Paraphrase legitimately changes wording, so a finding means
> "these two columns look unrelated, worth a human look" and **never** "the distillation is wrong". It also
> **cannot catch a distillation that is wrong while sharing vocabulary** — that limit is stated in the rule's
> own note and in its README entry.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《中华人民共和国招标投标法》and its implementing regulations. The verification pass could not
> retrieve verbatim clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule
> at `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise
> `kind` to `direct`.** The clause-category vocabulary ships **empty**; with nothing configured, `TE-004`
> reports itself in `skipped` rather than passing quietly.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-extract
dsh --profile <name> --dump-config | grep 'dsh-tender-extract'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-extract.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-extract
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-extract contributors.
