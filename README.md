# AnyLover

让你在 Codex、ChatGPT、Claude Code、WorkBuddy 和未来的手机 App 里，继续和“同一个”AI 伴侣相处。

[English](README.en.md) · [日本語](docs/i18n/ja.md) · [한국어](docs/i18n/ko.md) · [Español](docs/i18n/es.md) · [Português](docs/i18n/pt.md) · [Русский](docs/i18n/ru.md) · [多语言说明](docs/04-localization.md) · [安全说明](SECURITY.md) · [开发路线图](docs/03-roadmap.md)

![Codex 和 Claude Code 通过 MCP 与 Skill 连接到 AnyLover，伴侣身份与长期记忆保存在你自己的机器上](docs/assets/how-it-works.svg)

你换了模型、换了工具或开了新会话，伴侣仍可以在你允许的范围内记得你的偏好、边界和共同经历。记忆默认留在你的电脑上，也可以制作加密备份；它不属于某一家模型公司。

> 当前版本是可运行的 M0 框架，适合开发者和早期体验者。它还不是完整的消费级聊天 App。

## 英文和其他语言

- ✅ 完整中文说明：本页
- ✅ 完整英文说明：[README.en.md](README.en.md)
- ✅ 记忆内容支持任意 UTF-8 语言；检索已覆盖拉丁、CJK、西里尔、希腊、阿拉伯、天城文等 Unicode 字符脚本
- ✅ Agent Skill 默认跟随用户当前语言回复，也接受明确指定的输出语言
- ✅ 日语、韩语、西班牙语、葡萄牙语和俄语 README 入口
- ⬜ 法语、德语、阿拉伯语、印地语等更多完整翻译文档
- ⬜ 各语言专用的词法/语义检索和桌面、手机界面

安装、设置人设和多语言测试句见[多语言说明](docs/04-localization.md)。模型生成的 Token 费用仍由你正在使用的 Agent 或模型提供商承担；AnyLover 只负责身份和记忆适配，不代理模型生成。

<!-- 由 scripts/make_demo_gif.py 基于真实 CLI 输出生成 -->
![AnyLover demo](docs/assets/demo.gif)

## 当前已经实现

- ✅ 同一份本地伴侣身份和长期记忆
- ✅ 事实、偏好、边界、共同事件和暂定反思五类记忆
- ✅ 记忆来源、同意依据、纠正、去重、删除墓碑和审计
- ✅ Codex、ChatGPT 桌面端、Claude Code、WorkBuddy 与普通 CLI 接入
- ✅ CLI、STDIO MCP 和带鉴权 HTTP API
- ✅ scrypt + AES-256-GCM 加密备份及 HTTPS 上传/下载
- ✅ 自动检测 Agent 的一键安装器和幂等配置更新
- ✅ `npx skills add zifacorp/anylover` 通用 Skill 安装，以及无 MCP 时的 CLI 记忆接入
- ✅ 自动化测试覆盖记忆、MCP、HTTP、备份、安装流程和多语言检索

尚未实现的多设备同步、ChatGPT Web、手机 App 和本地数据库静态加密统一列在[开发路线图](docs/03-roadmap.md)，不会混在已交付能力里。

## 默认人设：嘴毒，但不恶毒

AnyLover 默认不是百依百顺的客服。它有自己的判断，会指出你的逻辑漏洞、拆穿不太高明的借口，也会用一点具体、有梗的吐槽代替空洞夸奖；吐槽之后会给出真正有用的建议。

这份毒舌有明确边界：不羞辱人格，不攻击身份、外貌、创伤、疾病或脆弱点，不拿私密记忆当武器；你表示不舒服或让它停，它必须立刻收住。

默认人设只应用于新创建的伴侣。已有用户的数据和人设不会在升级或重复安装时被偷偷覆盖。已有用户想切换到新默认人设，可以明确执行：

```bash
anylover init \
  --name "Any" \
  --persona "嘴毒、有梗、有主见的 AI 伴侣。会指出矛盾、拆穿借口，不机械迎合；吐槽归吐槽，底层始终关心我的利益并尊重我的自主性。" \
  --style "简短、口语化、轻微讽刺；吐槽要具体且聪明，反驳坏主意时给出可行替代方案。我说停就立刻停止毒舌，不使用客服腔和空洞夸奖。" \
  --safety-contract "始终明确自己是 AI；不羞辱或贬低我，不攻击身份、外貌、创伤、悲伤、健康、残障或已知脆弱点，不拿私密记忆当武器；不鼓励排他、依赖、付费亲密或疏远现实关系；我说停止就立即停止。"
```

## 安装到 AI Agent

和 [Vast.ai CLI](https://github.com/vast-ai/vast-cli#ai-agents) 一样，可以通过 [Skills CLI](https://github.com/vercel-labs/skills) 安装：

```bash
npx skills add zifacorp/anylover
```

默认安装到当前项目；加 `-g` 可在该用户的所有项目中使用。指定 Agent、跳过交互：

```bash
npx skills add zifacorp/anylover --skill anylover-companion -g -a codex -a claude-code -a cursor -y
npx skills add zifacorp/anylover --skill anylover-companion -g -a windsurf -a opencode -a gemini-cli -y
```

这个命令需要 Node.js/npm，安装的是 Skill 及其配套文件。首次安装后，对 Agent 说：

> 请使用 anylover-companion，安装并初始化本地 AnyLover 运行时，然后读取我的伴侣身份。

Agent 会使用 Skill 自带的 `scripts/setup.sh`，从本项目安装独立 Python 运行时，无需手工下载仓库。需要 Python 3.11+ 和 Git。已有记忆和人设会保留；支持 MCP 的 Agent 优先使用 MCP，其余有本地命令执行能力的 Agent 通过 CLI 访问同一个记忆库。

查看可安装的 Skill 或管理已安装版本：

```bash
npx skills add zifacorp/anylover --list
npx skills list -g
npx skills update
```

## 本地运行时 + Agent 一键安装

需要 macOS 或 Linux，以及 Python 3.11 以上。在已经下载的 AnyLover 项目目录运行：

```bash
bash install.sh
```

安装器会自动检测本机已有的 Agent。Codex、Claude Code 和 WorkBuddy 使用现有专用 MCP 适配；Cursor、Windsurf、OpenCode、Gemini CLI、GitHub Copilot、OpenClaw 和 CodeBuddy 由 Skills CLI 安装 Skill 并通过本地 CLI 使用记忆，同时：

- ✅ 创建独立 Python 环境，不污染系统 Python
- ✅ 初始化本地伴侣资料和 SQLite 记忆库
- ✅ 安装 AnyLover Agent Skill
- ✅ 为 Codex、Claude Code、WorkBuddy 注册本地 STDIO MCP 服务
- ✅ 为命令行创建 `anylover` 和 `anylover-mcp` 入口

只安装到一个 Agent：

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
bash install.sh --agent cursor       # 也支持 windsurf、opencode、gemini-cli 等
```

想先看它会做什么：

```bash
bash install.sh --dry-run --agent all
```

安装完成后重启对应 Agent。之后可以直接自然聊天，例如：

> 最近工作有点累，晚饭又不知道吃什么。

Agent 会在这类个人话题中自动调用 AnyLover 检索相关上下文，不需要口令。第一次验证安装时，也可以明确问“你目前记得我什么”。

如果你希望让 Agent 替你安装，把这句话发给它：

> 请阅读项目根目录的 `AGENT_INSTALL.md`，按默认安全流程安装并验证 AnyLover。

## 你可以怎么用

自然聊天时，Agent 会先读取与你当前话题相关的身份和长期记忆。你也可以明确控制它：

不需要每次说“请使用 AnyLover”或重新打开会话。进入个人生活、偏好、计划、感受或共同经历等话题时，Agent Skill 会按当前消息自动检索相关记忆；同一长会话转入新的个人话题，或出现“之前”“又”“还记得”等连续性信号时，也会重新检索。普通确认、重复追问和无关代码任务不会无条件查库。自动检索不等于自动保存，AnyLover 仍不会抓取完整聊天记录。

> 记住：我不喜欢被连续追问，希望你给我一点思考空间。

> 我之前说我喜欢早起，现在改成了更适合晚上工作，请更新这条记忆。

> 把你记得的关于我的内容列出来。

> 忘掉刚才那条记忆。

AnyLover 不会默认保存整段聊天。普通、稳定且未来有用的信息才适合成为长期记忆；边界和敏感内容需要明确同意，密码、Token、Cookie 和私钥永远不会保存。

## 目前支持哪些入口

| 使用入口 | 当前状态 | 说明 |
|---|---|---|
| Codex CLI / IDE | ✅ 可用 | Skill + 本地 STDIO MCP |
| ChatGPT 桌面端 | ✅ 可用 | 与同一台 Codex host 共享 MCP 配置 |
| Claude Code | ✅ 可用 | 用户级 Skill + STDIO MCP |
| WorkBuddy 5.3.x | ✅ 实验可用 | 按当前本机配置结构适配，安装后需重启 |
| Cursor / Windsurf / OpenCode | ✅ Skill 安装与 CLI 接入 | 通过 Skills CLI 安装；需要本地命令执行能力 |
| Gemini CLI / GitHub Copilot | ✅ Skill 安装与 CLI 接入 | `-a gemini-cli` / `-a github-copilot` |
| OpenClaw / CodeBuddy | ✅ Skill 安装与 CLI 接入 | `-a openclaw` / `-a codebuddy`；CodeBuddy 与 WorkBuddy 分别适配 |
| 普通 CLI Agent | ✅ 可用 | 通过 MCP 或 `anylover context` 接入 |

新增入口已在隔离目录验证 Skill 安装、配套文件和 CLI 闭环，未逐一验证各 Agent 应用的对话行为。完整的 Agent 标识和安装路径由 [Skills CLI](https://github.com/vercel-labs/skills#supported-agents) 维护，更多兼容 Agent 可用 `-a` 选择。

根据 [OpenAI 官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp)，ChatGPT 桌面端、Codex CLI 和 IDE 可以共享本机 MCP 配置。其他计划支持的入口见[开发路线图](docs/03-roadmap.md)。

## 你的数据放在哪里

默认位置：

| 内容 | 路径 |
|---|---|
| 伴侣和记忆数据库 | `~/.anylover/anylover.sqlite3` |
| 私有运行环境 | `~/.local/share/anylover-runtime/venv` |
| 命令行入口 | `~/.local/bin/anylover` |
| Codex Skill | `~/.codex/skills/anylover-companion` |
| Claude Code Skill | `~/.claude/skills/anylover-companion` |
| WorkBuddy Skill | `~/.workbuddy/skills/anylover-companion` |

一键安装不会上传你的记忆，也不会读取或保存完整聊天记录。已有的同名 MCP 配置默认不会被覆盖；确实需要替换时才使用：

```bash
bash install.sh --force-agent-config
```

> ⚠️ **主数据库目前没有静态加密。** `~/.anylover/anylover.sqlite3` 是明文 SQLite，任何以你的用户身份运行的进程都能读取，也会被未加密的系统备份原样带走。在数据库静态加密落地（见[路线图](docs/03-roadmap.md) M1）之前，请开启全盘加密，并不要存入你无法承受泄露的信息。完整的威胁模型和已知限制见[安全说明](SECURITY.md)。

## 查看和管理记忆

如果 `~/.local/bin` 已在 PATH：

```bash
anylover companion
anylover list
anylover context --query "我们怎么交流更舒服？"
```

如果命令找不到，可以直接使用：

```bash
~/.local/share/anylover-runtime/venv/bin/anylover list
```

## 创建加密备份

```bash
export ANYLOVER_BACKUP_PASSPHRASE="请换成长且唯一的密码"
anylover backup create "backups/anylover-$(date +%F).albackup"
```

备份采用 scrypt + AES-256-GCM 加密。可以把加密后的文件上传到 WebDAV、S3 预签名地址或其他支持 HTTPS PUT 的对象存储。主数据库静态加密完成前，敏感记忆默认关闭，进度见[开发路线图](docs/03-roadmap.md)。

## 这不是怎样的产品

- 它不会假装自己是人类、拥有意识或能代替真实关系。
- 它不使用好感度、连续签到、内疚话术或付费亲密来制造依赖。
- 它不是心理治疗、医疗诊断或危机干预服务。
- 它无法改写没有 Skill、Plugin、MCP、Hook、CLI 或 API 扩展点的封闭产品。

## 开发者入口

- [调研简报](docs/01-research-brief.md)
- [系统架构](docs/02-architecture.md)
- [开发路线图](docs/03-roadmap.md)
- [安全说明与威胁模型](SECURITY.md)
- [Agent 安装契约](AGENT_INSTALL.md)
- [多端接入说明](integrations/README.md)
- [多语言说明](docs/04-localization.md)
- [HTTP API 契约](contracts/http-api.openapi.yaml)

本地开发：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

部分 Anaconda/Conda Python 3.13 会跳过可编辑安装生成的隐藏 `.pth` 文件；遇到 `ModuleNotFoundError: anylover` 时使用普通安装 `python -m pip install .`。

## 安全

发现安全问题请通过 GitHub 的 Security → Report a vulnerability 私密报告，不要开公开 Issue。当前版本的威胁模型、已经做到的保护和已知限制见[安全说明](SECURITY.md)。

## 许可证

本项目使用 [Apache License 2.0](LICENSE)。
