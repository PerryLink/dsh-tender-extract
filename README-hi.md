# dsh-tender-extract — टेंडर दस्तावेज़ की खंड-उद्धरण तालिका की जाँच (स्रोत और मूल पाठ)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-tender-extract` एक खंड-उद्धरण तालिका पढ़ता है — सामग्री का हेडर और प्रत्येक उद्धरण की एक पंक्ति —, संस्करणबद्ध नियम-पैक लागू करता है, और केवल उसी तालिका पर रिपोर्ट देता है: हर पंक्ति अपना स्रोत (`sourceRef`) देती है या नहीं, मूल खंड-पाठ का कॉलम (`rawText`) भरा है या नहीं, निकाली गई अपेक्षा (`requirement`) उस मूल पाठ से कुछ शब्द साझा करती है या नहीं, दर्ज श्रेणी आपकी संस्था की सूची में है या नहीं, कोई उद्धरण-क्रमांक (`seq`) दोहराया नहीं गया है या नहीं, हेडर परियोजना और स्रोत दस्तावेज़ का नाम देता है या नहीं, और मूल पाठ में कोई टेम्पलेट प्लेसहोल्डर शेष नहीं है या नहीं। खंड-श्रेणी के मान फ़ैक्टरी में खाली हैं, और कुछ भी कॉन्फ़िगर न होने पर `TE-004` चुपचाप पास होने के बजाय `skipped` में स्वयं को दर्ज करता है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-tender-extract: real output over its TE-007 fixture](https://raw.githubusercontent.com/PerryLink/dsh-tender-extract/main/docs/assets/dsh-tender-extract-demo.png)

इस प्लगइन का अपने ही `TE-007` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| मेरी तालिका के एक उद्धरण के स्रोत कॉलम में कुछ नहीं है। क्या यह दर्ज होता है? | हाँ। `TE-001` हर उद्धरण में `sourceRef` की अपेक्षा करता है और जिस पंक्ति में वह खाली हो उसे दर्ज करता है। यह देखता है कि स्रोत दर्ज है, यह कभी नहीं कि वह सही जगह की ओर इशारा करता है, और यह सिद्ध नहीं करता कि कोई उद्धरण छूट गया — पूर्णता केवल पूरे टेंडर दस्तावेज़ से तुलना करके आँकी जा सकती है, जो यह प्लगइन कभी नहीं देखता। |
| मूल पाठ का कॉलम भरा हुआ है — क्या प्लगइन पुष्टि करता है कि वह टेंडर दस्तावेज़ से शब्द-दर-शब्द मेल खाता है? | `TE-002` केवल यह देखता है कि `rawText` कॉलम भरा है। यह उस पाठ की टेंडर दस्तावेज़ से तुलना नहीं करता; उस तुलना के लिए मूल दस्तावेज़ हाथ में होना चाहिए। |
| निकाली गई अपेक्षा किसी और ही जगह से आई लगती है। क्या यह चिह्नित होगा? | `TE-003` देखता है कि `requirement` और `rawText` में कुछ शब्द साझा हैं या नहीं — अतिव्यापी हान द्विग्राम और पूर्ण लातिनी शब्द — और जहाँ कुछ भी साझा न हो वह पंक्ति दर्ज करता है। भावानुवाद स्वाभाविक रूप से शब्द बदल देता है, इसलिए यह संकेत का अर्थ है कि ये दोनों कॉलम असंबद्ध दिखते हैं और मानवीय समीक्षा योग्य हैं, यह कभी नहीं कि निष्कर्ष गलत है। यह ऐसा गलत निष्कर्ष भी नहीं पकड़ सकता जिसमें शब्द साझा हों, और `minShared` की सीमा 2 एक स्थानीय परिपाटी है, कोई मानक संख्या नहीं। |
| हमने अभी तय नहीं किया कि खंडों का वर्गीकरण कैसे करेंगे। श्रेणी कॉलम का क्या होगा? | इसके मान फ़ैक्टरी में खाली हैं, इसलिए जब तक आप उन्हें न भरें `TE-004` चुपचाप पास होने के बजाय `skipped` में स्वयं को दर्ज करता है। कॉन्फ़िगर होने के बाद यह केवल देखता है कि दर्ज मान आपकी सूची में है; यह तय नहीं करता कि कोई खंड किस श्रेणी में आता है। |
| तालिका के दो उद्धरणों पर एक ही क्रमांक है। | `TE-005` दोनों पंक्तियों के `seq` की तुलना करता है (तुलना में श्वेत-स्थान का अंतर अनदेखा रहता है) और दोहराव दर्ज करता है, क्योंकि दो बार आया क्रमांक किसी खंड को निर्विवाद रूप से उद्धृत करने नहीं देता। क्रमांकन बाकी मामलों में उचित है या नहीं, यह नहीं आँकता। |
| एक उद्धरण का मूल पाठ अब भी टेम्पलेट वाला ही है। | `TE-007` उस पंक्ति को दर्ज करता है जिसके `rawText` में फ़ैक्टरी सूची का कोई प्लेसहोल्डर अब भी है — `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例` — क्योंकि ऐसा उद्धरण भरने के बजाय टेम्पलेट से उतारा गया है। सूची में `（略）` जानबूझकर नहीं है, क्योंकि लंबे खंड को छोटा करने का वह वैध तरीका है; और यह केवल उसी सूची के शब्द खोज सकता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-tender-extract
dsh --profile <name> --dump-config | grep 'dsh-tender-extract'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/tender-extract.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-extract
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-extract contributors.
