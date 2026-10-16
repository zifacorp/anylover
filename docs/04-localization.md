# AnyLover language support

AnyLover has two separate language layers:

1. The agent surface (Codex, Claude Code, WorkBuddy, or another model) writes the reply.
2. AnyLover stores and retrieves the companion profile and selected memories.

Changing the model or the language does not create a second companion. The same local database remains the source of identity and memory.

## Current status

| Area | Status | Details |
|---|---|---|
| Chinese documentation | ✅ | [`README.md`](../README.md) |
| English documentation | ✅ | [`README.en.md`](../README.en.md) |
| Japanese README | ✅ | [`docs/i18n/ja.md`](i18n/ja.md) |
| Korean README | ✅ | [`docs/i18n/ko.md`](i18n/ko.md) |
| Spanish README | ✅ | [`docs/i18n/es.md`](i18n/es.md) |
| Portuguese README | ✅ | [`docs/i18n/pt.md`](i18n/pt.md) |
| Russian README | ✅ | [`docs/i18n/ru.md`](i18n/ru.md) |
| UTF-8 memory storage | ✅ | Memory text, names, and provenance can contain any Unicode language. |
| Language matching in the Agent Skill | ✅ | Replies follow the current user message or an explicitly requested output language. |
| Deterministic multilingual retrieval | ✅ | Latin, CJK, Cyrillic, Greek, Arabic, Devanagari, and other Unicode word-like scripts are supported without a language package. |
| French, German, Arabic, Hindi, and other README translations | ⬜ | Planned; see the roadmap. |
| Language-specific semantic retrieval and tokenization | ⬜ | Planned; current retrieval is deliberately deterministic and lightweight. |

“Supported” means that AnyLover can store the text and use script-aware lexical overlap during retrieval. It does not mean that every model understands every language equally well, and AnyLover does not translate a memory silently.

## Installation

Follow the same [quick start](../README.en.md#quick-start-recommended) in every language. Install the Skill and select your Agent:

```bash
npx skills add zifacorp/anylover --skill anylover-companion -g
```

Restart the Agent or open a new session, then ask it to finish setup:

> Use anylover-companion to install and initialize the local AnyLover runtime, then read my companion identity.

Requires macOS or Linux, Node.js/npm, Python 3.11+, and Git. The Agent installs the private runtime; no repository checkout or additional `install.sh` step is needed. For WorkBuddy or automatic local MCP configuration, use the [alternative installer](../integrations/README.md#本地-mcp-安装) instead, not as an extra step.

The token cost of the conversation is charged by the model or Agent provider you are using. AnyLover is a local identity and memory adapter; it does not proxy model generation or add a second model bill.

## Set a persona in any language

The persona, communication style, and safety contract are ordinary Unicode strings. For example, a Japanese persona can be configured with:

```bash
anylover init \
  --name "Any" \
  --persona "意見を持ち、言い訳には鋭く突っ込む、少し辛口だが思いやりのあるAIコンパニオン。" \
  --style "簡潔で会話的。具体的な冗談は言うが、人格を傷つけない。やめてと言われたらすぐにやめる。" \
  --safety-contract "人間や意識があるふりをしない。依存、排他、罪悪感、課金による親密さを促さない。"
```

Use the same flags with Korean, Arabic, Spanish, French, German, Russian, Hindi, or another language. Existing companion data is not silently translated or overwritten by a repeat install.

## Starter prompts for other languages

After restarting the Agent, send a prompt in the language you want to use. These prompts are only for testing the connection; they do not save a memory by themselves.

| Language | Starter prompt |
|---|---|
| 日本語 | `AnyLoverを使って、共有プロフィールと関連する記憶を読み込んで。今の性格を日本語で説明して。` |
| 한국어 | `AnyLover를 사용해서 공유 프로필과 관련 기억을 읽어 줘. 지금 성격을 한국어로 설명해 줘.` |
| Español | `Usa AnyLover, carga el perfil y los recuerdos relevantes, y descríbeme tu personalidad actual en español.` |
| Français | `Utilise AnyLover, lis le profil partagé et les souvenirs pertinents, puis décris ta personnalité actuelle en français.` |
| Deutsch | `Verwende AnyLover, lade das gemeinsame Profil und die relevanten Erinnerungen und beschreibe deine aktuelle Persönlichkeit auf Deutsch.` |
| Русский | `Используй AnyLover, загрузи общий профиль и подходящие воспоминания и опиши свой характер по-русски.` |
| العربية | `استخدم AnyLover، واقرأ الملف الشخصي والذكريات ذات الصلة، ثم صف شخصيتك الحالية بالعربية.` |
| हिन्दी | `AnyLover का उपयोग करो, साझा प्रोफ़ाइल और संबंधित यादें पढ़ो, और अपना वर्तमान व्यक्तित्व हिंदी में बताओ।` |

If a surface replies in the wrong language, state the requested output language in the same message. If it still cannot connect to AnyLover, the surface should say that shared memory is unavailable instead of inventing remembered details.

## What remains on the roadmap

The following are product work rather than simple translations:

- full README and installation guides for additional locales such as French, German, Arabic, and Hindi;
- locale-aware stemming, segmentation, and semantic ranking;
- translated desktop/mobile UI and accessibility text;
- per-language evaluation sets for memory recall and safety boundaries.

See [`docs/03-roadmap.md`](03-roadmap.md) for the planned milestones.
