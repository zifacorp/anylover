# AnyLover 路线图

状态说明：`✅` 已实现并经过当前仓库验证；`⬜` 尚未实现，属于后续计划。

## M0：可运行框架

- ✅ 本地 SQLite 记忆、来源、同意、去重和替代模型
- ✅ 默认“毒舌但不恶毒”的 Companion profile、表达风格与安全契约
- ✅ Fact、Preference、Boundary、Event、Reflection 五类记忆
- ✅ CLI、STDIO MCP 和带鉴权 HTTP API
- ✅ 内容清除后的 tombstone 与审计事件
- ✅ scrypt + AES-256-GCM 加密备份、恢复、HTTPS 上传和下载
- ✅ Codex、ChatGPT 桌面端、Claude Code、WorkBuddy 和普通 CLI 接入
- ✅ 自动检测 Agent 的一键安装脚本、绝对 MCP 路径和安全配置合并
- ✅ Skills CLI 通用安装、独立 Skill 运行时安装脚本、MCP 缺席时的 CLI 记忆接入
- ✅ Cursor、Windsurf、OpenCode、Gemini CLI、GitHub Copilot、OpenClaw、CodeBuddy 的 Skill 分发入口（隔离安装验证；应用内对话待逐端验证）
- ✅ Codex/ChatGPT Plugin scaffold 与标准 Agent Skill
- ✅ Agent Skill 按用户当前语言回复，并保留记忆原文
- ✅ Unicode 多脚本确定性检索（拉丁、CJK、西里尔、希腊、阿拉伯、天城文等）
- ✅ 英文、日文、韩文、西班牙文、葡萄牙文和俄文 README 入口
- ✅ 自动化测试及隔离环境 Agent 安装验证

## M1：记忆质量与本地产品化

- ⬜ `MemoryEngine` 插件接口和 ZifaMem adapter
- ⬜ 会话结束时的候选记忆提取与用户确认队列
- ⬜ 时间、实体、矛盾和 supersession 评测
- ⬜ SQLite FTS5 / embedding 混合检索与可解释分数
- ⬜ SQLCipher 或平台 Keychain 封装的数据库静态加密
- ⬜ macOS 菜单栏/桌面壳与可视化记忆检查器
- ⬜ LoCoMo、LongMemEval 和自建关系连续性回归集
- ⬜ 法语、德语、阿拉伯语、印地语等更多完整本地化文档
- ⬜ 各语言专用的分词、词干化、语义检索和本地化 UI

## M2：多设备、ChatGPT Web 与手机端

- ⬜ 远程 Streamable HTTP MCP gateway
- ⬜ 设备注册、短期 access token、撤销和速率限制
- ⬜ 端到端加密增量事件日志，不把明文交给同步服务
- ⬜ tombstone 跨设备传播、冲突合并、时钟偏差和重放保护
- ⬜ ChatGPT Web Plugin 发布与 OAuth
- ⬜ iOS / Android SDK 和最小聊天 App
- ⬜ 手机端设备密钥管理、备份恢复和生物识别解锁

## M3：可信情感陪伴

- ⬜ 共同叙事、关系边界与情绪动力的可解释模型
- ⬜ 反操纵设计审计：排他、内疚、付费亲密和 streak 压力
- ⬜ 青少年、危机、哀伤和高依赖场景的专家评审
- ⬜ 用户可见的“为什么记住 / 为什么召回”与一键纠错
- ⬜ 导出、账户迁移、删除 SLA 和第三方安全评估

## 近期产品验证

- ⬜ 在新增 Agent 应用内逐端验证 Skill 触发与完整陪伴对话
- ⬜ 让同一位用户在 Codex 与 Claude Code 中各完成一次陪伴对话
- ⬜ 验证第二端能召回第一端经用户同意保存的偏好
- ⬜ 验证未保存的原始对话不会被另一端召回
- ⬜ 创建加密备份，在新目录恢复并重复检索

这个窄闭环会同时检验“同一个伴侣”、选择性记忆和可迁移性，通过后再进入 M1 的记忆质量建设。
