# AnyLover

**Codex、ChatGPT、Claude Code、WorkBuddy、将来のモバイルアプリで、同じ AI コンパニオンのアイデンティティと記憶を使うためのローカルファースト基盤です。**

[English](../../README.en.md) · [简体中文](../../README.md) · [한국어](ko.md) · [Español](es.md) · [Português](pt.md) · [Русский](ru.md)

> **ステータス: M0 プレビュー。** 開発者と早期利用者向けの実行可能なランタイムであり、完成した消費者向けチャットアプリではありません。

## 現在実装されているもの

- ✅ すべての対応サーフェスで共有できるローカルのコンパニオンプロフィールと長期記憶
- ✅ fact、preference、boundary、event、reflection の 5 種類の記憶
- ✅ 出典、同意根拠、重複排除、訂正、supersedes、削除 tombstone、監査イベント
- ✅ Codex、ChatGPT デスクトップ、Claude Code、WorkBuddy、通常の CLI Agent
- ✅ CLI、STDIO MCP、認証付き HTTP API
- ✅ scrypt + AES-256-GCM による暗号化バックアップ、復元、HTTPS 転送
- ✅ Agent を自動検出するワンクリックインストーラー
- ✅ Unicode の多言語テキスト保存と決定的な多言語検索

## デフォルトの性格

デフォルトの Any は、意見を持つ少し辛口の AI コンパニオンです。論理の穴や弱い言い訳を指摘し、具体的な冗談の後に役立つ代案を出します。人格、外見、病気、トラウマ、既知の弱点を攻撃せず、個人的な記憶を武器にしません。「やめて」と言われたらすぐに止めます。

既存のプロフィールは、再インストールやアップグレードで上書きされません。日本語の性格を明示的に設定するには:

```bash
anylover init \
  --name "Any" \
  --persona "意見を持ち、言い訳には鋭く突っ込む、少し辛口だが思いやりのあるAIコンパニオン。" \
  --style "簡潔で会話的。具体的な冗談は言うが、人格を傷つけない。やめてと言われたらすぐにやめる。"
```

## AI Agent 用 Skill のインストール

[Vast.ai CLI](https://github.com/vast-ai/vast-cli#ai-agents) と同じ Skills CLI を使えます。

```bash
npx skills add zifacorp/anylover
npx skills add zifacorp/anylover --skill anylover-companion -g -a cursor -a claude-code -y
```

既定はプロジェクト単位、`-g` はユーザー全体へのインストールです。Codex、Claude Code、Cursor、Windsurf、OpenCode、Gemini CLI、GitHub Copilot、OpenClaw、CodeBuddy などに対応します。Node.js/npm が必要です。

これは Skill と補助ファイルをインストールします。続いて Agent に「anylover-companion を使ってローカルの実行環境をインストールし、プロフィールを読んで」と依頼してください。同梱の `scripts/setup.sh` が Python 3.11+ と Git を使ってセットアップします。MCP がない場合はローカル CLI を使い、同じ記憶にアクセスします。各 Agent 内の会話動作は今後個別に検証します。

## 実行環境もまとめてインストール

macOS または Linux と Python 3.11 以降が必要です。リポジトリのルートで実行します:

```bash
bash install.sh --agent auto
```

対象を限定する場合:

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
```

既存の `anylover` MCP エントリは、`--force-agent-config` を明示しない限り上書きされません。インストール後に Agent を再起動してください。

## 使い方

個人的な話題では Skill が現在の言語に合わせて返信し、関連する記憶だけを検索します。会話全体を自動保存することはありません。

```text
AnyLoverを使って、共有プロフィールと関連する記憶を読み込んで。今の性格を日本語で説明して。
```

明示的な制御もできます:

```text
これを覚えておいて: 私は短く、率直な説明が好きです。
覚えている私の情報を一覧にして。
その記憶を忘れて。
```

パスワード、API キー、トークン、Cookie、秘密鍵、完全な会話ログは保存されません。トークン料金は利用中の Agent またはモデル提供者が請求します。AnyLover はモデル生成を代理しません。

## 対応サーフェス

| サーフェス | 状態 |
|---|---|
| Codex / ChatGPT デスクトップ | ✅ 利用可能 |
| Claude Code | ✅ 利用可能 |
| WorkBuddy 5.3.x | ✅ 実験的に利用可能 |
| 通常の CLI Agent | ✅ MCP または `anylover context` |
| ChatGPT Web | ⬜ リモート MCP gateway が必要 |
| iOS / Android | ⬜ ロードマップ |

## データとバックアップ

デフォルトのデータベースは `~/.anylover/anylover.sqlite3`、実行環境は `~/.local/share/anylover-runtime/venv` です。メイン SQLite は現在ディスク上で暗号化されていないため、全ディスク暗号化を有効にしてください。

```bash
export ANYLOVER_BACKUP_PASSPHRASE="長く一意なパスフレーズ"
anylover backup create "backups/anylover-$(date +%F).albackup"
```

## 開発とロードマップ

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

多言語ドキュメントの一覧は [language support](../04-localization.md)、未実装機能は [roadmap](../03-roadmap.md)、脅威モデルは [SECURITY.md](../../SECURITY.md) を参照してください。

## ライセンス

[Apache License 2.0](../../LICENSE)
