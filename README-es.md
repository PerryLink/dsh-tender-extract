# dsh-tender-extract — Comprobación de la tabla de extractos de cláusulas del pliego (procedencia y texto original)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-tender-extract` lee una tabla de extractos de cláusulas —la cabecera del expediente más una fila por extracto—, aplica un paquete de reglas versionado y devuelve un informe sobre esa tabla y solo sobre ella: que cada fila indique su procedencia (`sourceRef`), que la columna del texto original (`rawText`) esté cumplimentada, que la exigencia destilada (`requirement`) comparta algún término con ese texto, que la categoría registrada figure en la lista de su institución, que no se repita ningún número de extracto (`seq`), que la cabecera nombre el proyecto y el documento de origen, y que no quede ningún marcador de plantilla en el texto original. El vocabulario de categorías de cláusula viene vacío y, sin nada configurado, `TE-004` se declara en `skipped` en lugar de pasar en silencio.

## Cómo se ve la salida

![Terminal demo of dsh-tender-extract: real output over its TE-007 fixture](https://raw.githubusercontent.com/PerryLink/dsh-tender-extract/main/docs/assets/dsh-tender-extract-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `TE-007` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Un extracto de mi tabla no tiene nada en la columna de procedencia. ¿Se informa de eso? | Sí. `TE-001` exige `sourceRef` en todos los extractos e informa de cada fila en la que esté vacío. Comprueba que la procedencia esté registrada, nunca que apunte al lugar correcto, y no demuestra que falte un extracto: la exhaustividad solo puede juzgarse contra el pliego completo, que este plugin nunca ve. |
| La columna del texto original está rellenada, ¿confirma el plugin que coincide palabra por palabra con el pliego? | `TE-002` solo comprueba que la columna `rawText` esté cumplimentada. No coteja ese texto con el pliego; esa comparación requiere tener el documento original a mano. |
| La exigencia destilada parece venir de otro sitio por completo. ¿Se señalará? | `TE-003` busca términos compartidos entre `requirement` y `rawText` —bigramas Han solapados y palabras latinas completas— e informa de la fila cuando no comparten nada. Parafrasear cambia legítimamente las palabras, así que un hallazgo significa que las dos columnas parecen no tener relación y merecen una mirada humana, nunca que la destilación sea errónea. Tampoco detecta una destilación equivocada que sí comparta vocabulario, y el umbral `minShared` de 2 es una convención local, no una cifra normativa. |
| Todavía no hemos decidido cómo clasificar nuestras cláusulas. ¿Qué pasa con la columna de categoría? | Sus valores vienen vacíos, así que `TE-004` se declara en `skipped` en lugar de pasar en silencio hasta que los rellene. Una vez configurado solo comprueba que el valor registrado figure en su lista; no decide a qué categoría pertenece una cláusula. |
| Dos extractos de la tabla llevan el mismo número. | `TE-005` compara los valores de `seq` ignorando las diferencias de espaciado e informa de la repetición, porque un número que aparece dos veces no puede citarse sin ambigüedad. No juzga si la numeración es sensata por lo demás. |
| El texto original de un extracto sigue siendo el de la plantilla. | `TE-007` informa de la fila cuyo `rawText` todavía contiene un marcador de la lista de fábrica —`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`— porque un extracto que aún lo lleva se copió de la plantilla en vez de rellenarse. La lista excluye deliberadamente `（略）`, una forma legítima de abreviar una cláusula larga, y solo puede encontrar las palabras de esa lista. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-extract
dsh --profile <name> --dump-config | grep 'dsh-tender-extract'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-extract.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-extract
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-extract contributors.
