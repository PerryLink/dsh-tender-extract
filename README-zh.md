# dsh-tender-extract — 招标文件条款摘录核对

`dsh-tender-extract` 读取一份条款摘录表——材料表头加每条摘录一行——套用版本化规则库，只就这张表本身出报告：每行是否给出出处（`sourceRef`）、原文栏（`rawText`）是否填写、提炼的要求（`requirement`）与原文是否有共同词、所填类别是否在本机构清单内、摘录序号（`seq`）是否重复、表头是否写明项目与来源文件、原文栏是否残留模板占位符。条款类别取值出厂为空，未配置时 `TE-004` 在 `skipped` 中说明自己未执行，而不是静默通过。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 我表里有一条摘录的出处栏是空的，会报出来吗？ | 会。`TE-001` 要求每条摘录都填写 `sourceRef`，为空的行逐行报出。它只核对出处是否填写，从不判断出处指得对不对；它也**不声称能发现漏摘**——某条摘录是否摘全，只能与招标文件全文比对，而本插件看不到全文。 |
| 原文栏已经填了——插件会确认它与招标文件逐字一致吗？ | `TE-002` 只核对 `rawText` 栏是否填写。它不拿这段原文与招标文件比对，那需要持有人招标文件正本。 |
| 提炼的要求看着跟原文完全对不上，会被提示吗？ | `TE-003` 看 `requirement` 与 `rawText` 是否有共同词——重叠的汉字二字组与完整拉丁词——两栏一个共同词都没有时提示该行。提炼本身就会改写措辞，所以这条提示的含义是「这两栏看不出关系，值得人工复核」，**不断言提炼有误**。它也发现不了「提炼错误但用词相似」的情况；`minShared` 出厂为 2，是本机构口径、不是标准数值。 |
| 我们还没定条款类别怎么分，类别栏会怎样？ | 取值出厂为空，未填写前 `TE-004` 在 `skipped` 中说明自己未执行，而不是静默通过。配置之后它只核对所填值是否在册，不判断该条款应归入哪一类。 |
| 表里有两条摘录的序号一样。 | `TE-005` 比较两行的 `seq`（比较时忽略空白字符差异）并报出重复，因为序号重复会让人无法准确引用条款。序号编得合不合理，它不作判断。 |
| 有一条摘录的原文还是模板里的话。 | `TE-007` 报出 `rawText` 仍含出厂占位符列表所列词的行——`【`、`】`、`{{`、`}}`、`XXX`、`xxx`、`待填`、`待补充`、`TBD`、`todo`、`示例`——原文栏还留着这些词，说明摘录是照模板抄的，不是填进去的。该列表刻意不含 `（略）`，那是省略长条款的正常写法；它也只看得到列表内的词。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-tender-extract
dsh --profile <name> --dump-config | grep 'dsh-tender-extract'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-extract.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-extract
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-extract contributors.
