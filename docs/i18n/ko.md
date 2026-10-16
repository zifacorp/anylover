# AnyLover

**Codex, ChatGPT, Claude Code, WorkBuddy와 향후 모바일 앱에서 동일한 AI 컴패니언의 정체성과 기억을 사용하는 로컬 우선 기반입니다.**

[English](../../README.en.md) · [简体中文](../../README.md) · [日本語](ja.md) · [Español](es.md) · [Português](pt.md) · [Русский](ru.md)

> **상태: M0 프리뷰.** 개발자와 초기 사용자를 위한 실행 가능한 런타임이며 완성된 소비자용 채팅 앱은 아닙니다.

## 현재 구현된 기능

- ✅ 모든 지원 표면에서 공유하는 로컬 컴패니언 프로필과 장기 기억
- ✅ fact, preference, boundary, event, reflection 다섯 가지 기억 유형
- ✅ 출처, 동의 근거, 중복 제거, 수정, supersedes, 삭제 tombstone, 감사 이벤트
- ✅ Codex, ChatGPT 데스크톱, Claude Code, WorkBuddy, 일반 CLI Agent
- ✅ CLI, STDIO MCP, 인증된 HTTP API
- ✅ scrypt + AES-256-GCM 암호화 백업, 복원, HTTPS 전송
- ✅ Agent 자동 감지 원클릭 설치 프로그램
- ✅ Unicode 다국어 저장 및 결정적 다국어 검색

## 기본 성격

기본 Any는 의견이 있고 약간 독설적인 AI 컴패니언입니다. 논리의 허점과 약한 핑계를 지적하고, 구체적인 농담 뒤에 쓸 수 있는 대안을 제시합니다. 인격, 외모, 질병, 트라우마, 알려진 약점을 공격하지 않으며 사적인 기억을 무기로 사용하지 않습니다. “그만”이라고 하면 즉시 멈춥니다.

기존 프로필은 재설치나 업그레이드로 덮어쓰지 않습니다. 한국어 성격을 명시적으로 설정하려면:

```bash
anylover init \
  --name "Any" \
  --persona "의견이 있고 변명을 날카롭게 짚는, 약간 독설적이지만 배려심 있는 AI 컴패니언." \
  --style "간결하고 대화체로 말한다. 구체적인 농담은 하되 인격을 공격하지 않는다. 그만하라고 하면 즉시 멈춘다."
```

## AI Agent Skill 설치

[Vast.ai CLI](https://github.com/vast-ai/vast-cli#ai-agents)와 같은 Skills CLI를 사용할 수 있습니다.

```bash
npx skills add zifacorp/anylover
npx skills add zifacorp/anylover --skill anylover-companion -g -a cursor -a claude-code -y
```

기본은 프로젝트 범위이며 `-g`는 사용자 전체 범위입니다. Codex, Claude Code, Cursor, Windsurf, OpenCode, Gemini CLI, GitHub Copilot, OpenClaw, CodeBuddy 등을 선택할 수 있습니다. Node.js/npm이 필요합니다.

이 명령은 Skill과 보조 파일을 설치합니다. 이후 Agent에게 “anylover-companion으로 로컬 런타임을 설치하고 프로필을 읽어 줘”라고 요청하세요. 포함된 `scripts/setup.sh`가 Python 3.11+와 Git으로 런타임을 설치합니다. MCP가 없으면 로컬 CLI로 같은 기억에 접근합니다. 각 Agent 앱 내부의 대화 동작은 별도 검증이 필요합니다.

## 런타임과 함께 설치

macOS 또는 Linux와 Python 3.11 이상이 필요합니다. 저장소 루트에서 실행합니다.

```bash
bash install.sh --agent auto
```

특정 Agent만 설치하려면:

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
```

기존 `anylover` MCP 항목은 `--force-agent-config`를 명시하지 않는 한 덮어쓰지 않습니다. 설치 후 Agent를 재시작하세요.

## 사용법

개인적인 주제에서는 Skill이 현재 언어에 맞춰 답하고 관련 기억만 검색합니다. 전체 대화를 자동 저장하지 않습니다.

```text
AnyLover를 사용해서 공유 프로필과 관련 기억을 읽어 줘. 지금 성격을 한국어로 설명해 줘.
```

기억을 직접 제어할 수도 있습니다.

```text
이것을 기억해 줘: 나는 짧고 솔직한 설명을 좋아해.
나에 대해 기억하는 내용을 모두 보여 줘.
방금 그 기억을 잊어 줘.
```

비밀번호, API 키, 토큰, 쿠키, 개인 키, 전체 대화 기록은 저장하지 않습니다. 토큰 비용은 사용하는 Agent 또는 모델 제공자가 청구합니다. AnyLover는 모델 생성을 중계하지 않습니다.

## 지원 표면

| 표면 | 상태 |
|---|---|
| Codex / ChatGPT 데스크톱 | ✅ 사용 가능 |
| Claude Code | ✅ 사용 가능 |
| WorkBuddy 5.3.x | ✅ 실험적 사용 가능 |
| 일반 CLI Agent | ✅ MCP 또는 `anylover context` |
| ChatGPT Web | ⬜ 원격 MCP gateway 필요 |
| iOS / Android | ⬜ 로드맵 |

## 데이터와 백업

기본 데이터베이스는 `~/.anylover/anylover.sqlite3`, 런타임은 `~/.local/share/anylover-runtime/venv`입니다. 기본 SQLite는 아직 디스크 암호화를 사용하지 않으므로 전체 디스크 암호화를 활성화하세요.

```bash
export ANYLOVER_BACKUP_PASSPHRASE="길고 고유한 패스프레이즈"
anylover backup create "backups/anylover-$(date +%F).albackup"
```

## 개발과 로드맵

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

다국어 문서는 [language support](../04-localization.md), 미구현 기능은 [roadmap](../03-roadmap.md), 위협 모델은 [SECURITY.md](../../SECURITY.md)를 참고하세요.

## 라이선스

[Apache License 2.0](../../LICENSE)
