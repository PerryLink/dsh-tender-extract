# dsh-tender-extract

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
| `TE-003` | the requirement shares terms with the raw text | warn | principle |
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
