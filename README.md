# dsh-tender-extract — Tender document clause-extract table check (source and raw text)

`dsh-tender-extract` reads one clause-extract table — the package header plus one row per extract — applies a versioned rule pack and returns a report on that table alone: that every row gives its source (`sourceRef`), that the raw clause text column (`rawText`) is filled in, that the distilled requirement (`requirement`) shares at least some terms with that raw text, that a recorded category is on your institution's list, that no extract number (`seq`) is repeated, that the header names the project and the source document, and that no template placeholder survives in the raw text. The clause-category vocabulary ships empty, and with nothing configured `TE-004` reports itself in `skipped` instead of passing quietly.

## What it answers

| You ask | What it answers |
|---|---|
| One extract in my table has nothing in the source column. Is that reported? | Yes. `TE-001` requires `sourceRef` on every extract and reports each row where it is blank. It checks that the source is recorded, never that it points to the right place, and it does not prove that an extract is missing — completeness can only be judged against the whole tender document, which this plugin never sees. |
| The raw text column is filled in — does the plugin confirm it matches the tender document word for word? | `TE-002` only checks that the `rawText` column is filled. It does not compare that text against the tender document; that comparison needs the document itself in hand. |
| The distilled requirement looks as if it came from somewhere else entirely. Will that be flagged? | `TE-003` looks for shared terms between `requirement` and `rawText` — overlapping Han bigrams and whole Latin words — and reports the row when the two share nothing. Paraphrase legitimately changes wording, so a finding means the two columns look unrelated and are worth a human look, never that the distillation is wrong. It also cannot catch a distillation that is wrong while sharing vocabulary, and the `minShared` floor of 2 is a local convention, not a standard figure. |
| We have not decided how to classify our clauses yet. What happens to the category column? | Its values ship empty, so `TE-004` reports itself in `skipped` rather than passing quietly until you fill them in. Once configured it checks only that the recorded value is on your list; it does not decide which category a clause belongs to. |
| Two extracts in the table carry the same number. | `TE-005` compares the `seq` values ignoring whitespace differences and reports the repeat, because a number that appears twice cannot be cited unambiguously. It does not judge whether the numbering is otherwise sensible. |
| The raw text of one extract is still the template wording. | `TE-007` reports a row whose `rawText` still contains a placeholder from the factory list — `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例` — because an extract still carrying one was copied from the template rather than filled in. The list deliberately excludes `（略）`, a legitimate way to abridge a long clause, and it can only find the words on that list. |

## Standards it follows

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a whole document use `ptc` |

## What it does

Registers the `tender_extract` tool. It reads one clause-extract table — the package header plus one row per
extract — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `TE-001` | every extract gives its source | warn | principle |
| `TE-002` | every extract records the raw text | warn | principle |
| `TE-003` | the requirement shares terms with the raw text | warn | direct |
| `TE-004` | the category comes from your vocabulary (off by default) | info | local |
| `TE-005` | extract numbers are unique | warn | principle |
| `TE-006` | the table names its project and source document | warn | principle |
| `TE-007` | the raw text holds no unreplaced placeholder | warn | principle |
## Install

```sh
dsh plugin --profile <name> add dsh-tender-extract
dsh --profile <name> --dump-config | grep 'dsh-tender-extract'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-extract.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `TE-003` `leftField` / `rightField` / `minShared` — the two columns and the shared-term floor, `2` by
  default. Set it to `1` to be more permissive; the floor is **a local convention, not a standard figure**.
- `TE-004` `values` — your clause categories, e.g.
  `[资格条件, 技术规格, 商务条款, 评标办法, 合同条款]`. Empty means no check.
- `TE-007` `terms` — the placeholders to look for. 「略」 is deliberately **absent**: `……（略）` is a normal
  and legitimate way to abridge a long clause, so it is not treated as a placeholder.

## Material format

The tool accepts JSON or YAML:

```yaml
project: 某某工程施工招标
tenderNo: ZB-2026-018
source: 招标文件 2026-02-10 版
rows:
  - { 序号: '1', 出处: 第三章 第 3.2 条,
      原文: 投标人应具有建筑工程施工总承包二级及以上资质，并附资质证书复印件。,
      类别: 资格条件, 要求: 需具备建筑工程施工总承包二级及以上资质并提供证书复印件,
      是否实质性: 是, 响应: 需响应, 责任部门: 经营部 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the table's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/tender-extract.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`TE-003` fires on a distillation I am happy with.** The two columns share no terms — usually because the
  requirement was reworded into different vocabulary. Raise `minShared` to `1`, or disable the rule.
- **`TE-003` does not catch a distillation I know is wrong.** It cannot: the columns share vocabulary. This is
  the documented limit of a lexical check.
- **`TE-007` does not fire on `（略）`.** That is deliberate; add 「略」 to `terms` if your template really uses
  it to stand in for a whole clause.
- **`TE-004` never runs.** Its vocabulary is empty; fill it with your register's categories.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-tender-extract@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-tender-extract   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-extract contributors.
