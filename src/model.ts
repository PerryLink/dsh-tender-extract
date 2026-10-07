/**
 * dsh-tender-extract — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'tender_extract'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  seq: ['序号', '条款号', '项号', 'seq'],
  sourceRef: ['出处', '页码', '文件位置', '章节', 'sourceRef'],
  rawText: ['原文', '条款原文', '原文摘录', 'rawText'],
  category: ['类别', '条款类别', '分类', 'category'],
  requirement: ['要求', '提炼要求', '要点', 'requirement'],
  isStar: ['是否星号', '星号条款', '★', 'isStar'],
  isMandatory: ['是否实质性', '实质性条款', '是否否决项', 'isMandatory'],
  response: ['响应', '需响应', '是否需要响应', 'response'],
  owner: ['责任部门', '责任人', '归口部门', 'owner'],
  extractedAt: ['提取日期', '整理日期', 'extractedAt'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'clauses', '条款'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '招标项目名称'],
  tenderNo: ['tenderNo', '招标编号', '项目编号'],
  source: ['source', '来源文件', '招标文件版本'],
  extractedBy: ['extractedBy', '提取人', '整理人'],
  extractedAt: ['extractedAt', '提取日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '原文',
  'rawText',
  '出处',
  'sourceRef',
  '要求',
  'requirement',
  '序号',
  'seq',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
