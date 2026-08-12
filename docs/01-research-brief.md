# AnyLover 跨 Agent 情感陪伴与长期记忆调研简报

日期：2026-08-11

模式：Quick research brief
研究问题：在不绑定单一模型或聊天界面的前提下，怎样让多个 Agent 工具与移动端共享一个可控、可迁移、可备份的情感陪伴身份和长期记忆？

## 结论摘要

AnyLover 最合理的产品形态不是新的模型壳，而是独立的“伴侣运行时”。行为层用 Agent Skill/系统指令描述伴侣的表达方式和安全边界；状态层用 MCP/API 读写伴侣身份、用户偏好、关系边界与共同经历；存储层本地优先，并把加密备份与多设备同步分开设计。这样，Codex、Claude Code、WorkBuddy 和移动端只是不同界面，不再各自拥有互不相通的“另一个伴侣”。

首版不应承诺“接管任何 Agent”。可实现的准确说法是：对支持 MCP、Skill、Plugin、Hook、CLI 或 HTTP API 的工具提供适配；对完全封闭、没有扩展点的产品，只能通过复制上下文或专用自动化桥接。

## 证据与启示

长期一致性需要独立记忆架构，而不只是扩大上下文窗口。Generative Agents 把完整经历记录、相关记忆检索、高层反思和规划分为不同组件，并通过消融显示 observation、planning、reflection 都影响行为可信度（Park et al., 2023）<!--ref:park2023--><!--anchor:page:1-2-->。因此 AnyLover 将“事实/事件”“暂定反思”“伴侣行为策略”分层，反思不能冒充事实。

超长对话仍是公开模型的薄弱点。LoCoMo 的对话平均约 600 轮、跨最多 32 个会话；论文报告长上下文和 RAG 虽有改善，但仍明显落后于人类表现（Maharana et al., 2024）<!--ref:maharana2024--><!--anchor:page:13851-13852-->。这支持“选择性结构化记忆 + 来源信息”，而不是把整段聊天无限塞回提示词。

MemoryBank 证明了伴侣场景中“存储、检索、更新、用户画像”可以作为模型外部模块，并可同时服务闭源和开源模型（Zhong et al., 2024）<!--ref:zhong2024--><!--anchor:page:1-2-->。但它主要验证记忆机制，不等于已经解决跨设备同步、同意、删除传播和密钥管理；这些必须由 AnyLover 运行时负责。

LongMemEval 将长期记忆拆成 indexing、retrieval、reading，并测试信息抽取、跨会话推理、时间推理、知识更新和拒答。其结果显示持续交互下存在明显准确率下降，且时间感知检索与结构化读取能改善表现（Wu et al., 2025）<!--ref:wu2025--><!--anchor:page:1-2-->。因此数据模型必须保留时间、来源、更新/替代关系，并允许“没有足够记忆”而不是强行补全。

情感价值有初步行为证据，但不能扩大成治疗承诺。多项研究显示 AI companion 使用后可带来短时孤独感下降，其中“让用户感到被听见”是重要解释变量（De Freitas et al., 2025）<!--ref:defreitas2025--><!--anchor:section:Abstract-->。该证据支持认真倾听与连续性设计，却不支持宣称长期心理疗效，也不支持用排他依赖换留存。

## 接入面核实

截至 2026-08-11，OpenAI 官方文档把 Skill 定义为可复用工作流，把 Plugin 定义为可组合 Skill 与 MCP connector 的安装包；本地 Codex/ChatGPT 桌面端支持 STDIO 与 Streamable HTTP MCP，ChatGPT Web 则通过远程、插件承载的 MCP 工具接入。Claude Code 官方文档同样支持本地 STDIO 和远程 HTTP MCP，并采用 Agent Skills 标准。当前机器上的 WorkBuddy 5.3.5 具有 MCP JSON 配置、独立 memory 目录和 SQLite 会话库，说明可以先按 MCP + Skill 路径做实验适配，但这不是公开兼容性承诺。

## 推荐产品边界

1. 伴侣身份与记忆归用户，不归某个模型供应商。
2. 完整聊天默认不入库；只存经过筛选、带来源和同意依据的长期信息。
3. 边界优先于偏好，当前纠正优先于历史记忆，删除可跨设备传播。
4. 本地数据库、加密备份、实时同步是三个不同能力，分别验收。
5. 情感表达可以温暖，但必须透明地承认 AI 身份，不做排他、内疚、付费亲密或危机替代。

## 来源核验

| 来源 | 出版状态 | 核验 | 用途 |
|---|---|---|---|
| Park et al., 2023 | ACM UIST 同行评议会议论文 | DOI 与全文已核对 | 记忆流、反思、规划 |
| Maharana et al., 2024 | ACL Long Paper | DOI 与 ACL 全文已核对 | 超长对话评测 |
| Zhong et al., 2024 | AAAI 同行评议论文 | DOI、OpenAlex 与作者全文已核对 | 模型外长期记忆 |
| Wu et al., 2025 | ICLR 2025 会议论文 | 论文首页与全文已核对 | indexing/retrieval/reading |
| De Freitas et al., 2025 | Journal of Consumer Research | DOI、期刊元数据与摘要已核对 | 孤独感与“被听见” |

## 局限

本次是架构导向的快速调研，不是系统综述；未比较所有商业陪伴产品的留存、定价与合规策略，也没有完成真实用户研究。WorkBuddy 结论来自本机 5.3.5 安装结构，不应外推到所有版本。跨端实时同步、端侧数据库加密与远程 MCP 的认证模型仍需在 M1/M2 阶段验证。

## 参考文献

- De Freitas, J., Oğuz-Uğuralp, Z., Uğuralp, A. K., & Puntoni, S. (2025). [AI Companions Reduce Loneliness](https://doi.org/10.1093/jcr/ucaf040). *Journal of Consumer Research*.
- Maharana, A., Lee, D.-H., Tulyakov, S., Bansal, M., Barbieri, F., & Fang, Y. (2024). [Evaluating Very Long-Term Conversational Memory of LLM Agents](https://doi.org/10.18653/v1/2024.acl-long.747). *Proceedings of ACL 2024*, 13851–13870.
- Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). [Generative Agents: Interactive Simulacra of Human Behavior](https://doi.org/10.1145/3586183.3606763). *UIST '23*.
- Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W., & Yu, D. (2025). [LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory](https://arxiv.org/abs/2410.10813). *ICLR 2025*.
- Zhong, W., Guo, L., Gao, Q., Ye, H., & Wang, Y. (2024). [MemoryBank: Enhancing Large Language Models with Long-Term Memory](https://doi.org/10.1609/aaai.v38i17.29946). *Proceedings of AAAI*, 38(17), 19724–19731.

AI 披露：本简报由 AI 辅助完成检索、来源核验、证据整理和写作；关键论文的元数据与正文已在本次任务中核对。最终产品决策仍需人工评审和用户研究。
