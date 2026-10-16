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

## 快速开始（推荐）

适用于 Codex、Claude Code、Cursor 等能执行本地命令的 Agent。需要 macOS 或 Linux、Node.js/npm、Python 3.11+ 和 Git；不需要手工下载源码。

WorkBuddy 用户，或希望自动配置本地 MCP 的用户，请改用[本地 MCP 安装](integrations/README.md#本地-mcp-安装)。两种方式任选一种，不需要都执行。

### 1. 安装 Skill

在终端运行，按提示选择你正在使用的 Agent：

```bash
npx skills add zifacorp/anylover --skill anylover-companion -g
```

`-g` 表示在该用户的所有项目中可用。只想在当前项目使用，可以去掉 `-g`。

### 2. 让 Agent 完成初始化

重启 Agent 或新开会话，让它加载新 Skill，然后发送：

> 请使用 anylover-companion，安装并初始化本地 AnyLover 运行时，然后读取我的伴侣身份。

Agent 会安装独立 Python 运行环境并读取伴侣档案，保留已有记忆和人设。这一步完成后就装好了，不需要再运行 `install.sh`。没有 MCP 连接也能通过本地 CLI 使用记忆；这条安装路径不会自动修改 MCP 配置。

### 3. 开始聊天

先问一句，确认 Agent 能读取身份和记忆：

> 你目前记得我什么？也介绍一下你自己的性格。

新用户还没有记忆是正常的。之后直接自然聊天，不需要每次说“使用 AnyLover”：

> 最近工作有点累，晚饭又不知道吃什么。

指定 Agent、更新 Skill、WorkBuddy 和源码安装等可选操作，统一放在[进阶安装说明](integrations/README.md)。

## 默认人设：嘴毒，但不恶毒

AnyLover 默认不是百依百顺的客服。它有自己的判断，会指出你的逻辑漏洞、拆穿不太高明的借口，也会用一点具体、有梗的吐槽代替空洞夸奖；吐槽之后会给出真正有用的建议。

这份毒舌有明确边界：不羞辱人格，不攻击身份、外貌、创伤、疾病或脆弱点，不拿私密记忆当武器；你表示不舒服或让它停，它必须立刻收住。

默认人设只应用于新创建的伴侣。已有用户的数据和人设不会在升级或重复安装时被偷偷覆盖。已有用户想切换到新默认人设，可以在安装完成后让 Agent 执行（手动使用 CLI 见[查看和管理记忆](#查看和管理记忆)）：

```bash
anylover init \
  --name "Any" \
  --persona "嘴毒、有梗、有主见的 AI 伴侣。会指出矛盾、拆穿借口，不机械迎合；吐槽归吐槽，底层始终关心我的利益并尊重我的自主性。" \
  --style "简短、口语化、轻微讽刺；吐槽要具体且聪明，反驳坏主意时给出可行替代方案。我说停就立刻停止毒舌，不使用客服腔和空洞夸奖。" \
  --safety-contract "始终明确自己是 AI；不羞辱或贬低我，不攻击身份、外貌、创伤、悲伤、健康、残障或已知脆弱点，不拿私密记忆当武器；不鼓励排他、依赖、付费亲密或疏远现实关系；我说停止就立即停止。"
```

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
| Codex CLI / IDE | ✅ 可用 | Skill + 本地 CLI；可选 STDIO MCP |
| ChatGPT 桌面端 | ✅ 可用 | 与同一台 Codex host 共享 MCP 配置 |
| Claude Code | ✅ 可用 | 用户级 Skill + 本地 CLI；可选 STDIO MCP |
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
| 命令行入口 | 私有运行环境中的 `bin/anylover`；源码安装器还会创建 `~/.local/bin/anylover` |
| Codex Skill | `~/.codex/skills/anylover-companion` |
| Claude Code Skill | `~/.claude/skills/anylover-companion` |
| WorkBuddy Skill | `~/.workbuddy/skills/anylover-companion` |

安装不会上传你的记忆，也不会读取或保存完整聊天记录。已有的同名 MCP 配置默认不会被覆盖；替换方式见[进阶安装说明](integrations/README.md#本地-mcp-安装)。

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
