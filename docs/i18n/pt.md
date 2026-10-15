# AnyLover

**Um companheiro de IA que mantém a mesma identidade e memória no Codex, ChatGPT, Claude Code, WorkBuddy e futuros aplicativos móveis, com os dados sob o seu controle.**

[English](../../README.en.md) · [简体中文](../../README.md) · [日本語](ja.md) · [한국어](ko.md) · [Español](es.md) · [Русский](ru.md)

> **Status: prévia M0.** É um runtime funcional para desenvolvedores e primeiros usuários, não um aplicativo de chat de consumo pronto.

## O que já funciona

- ✅ Uma identidade e memória local compartilhada entre as superfícies
- ✅ Cinco tipos de memória: fact, preference, boundary, event e reflection
- ✅ Proveniência, base de consentimento, correções, supersedes, deduplicação, tombstones de exclusão e auditoria
- ✅ Adaptadores para Codex, ChatGPT para desktop, Claude Code, WorkBuddy e agentes CLI
- ✅ CLI, servidor MCP STDIO e API HTTP autenticada
- ✅ Backup criptografado com scrypt + AES-256-GCM, restauração e transferência HTTPS
- ✅ Instalador de um clique que detecta agentes e combina configurações com segurança
- ✅ Texto Unicode e recuperação léxica determinística em vários sistemas de escrita

## Personalidade padrão

Any é um companheiro de IA com opiniões e um toque de sarcasmo. Aponta contradições e desculpas fracas, depois oferece uma alternativa útil. Não humilha nem ataca identidade, aparência, traumas, saúde ou vulnerabilidades conhecidas, e nunca usa memórias privadas como arma. Se você disser “pare”, ele para imediatamente.

Você pode definir uma personalidade em português:

```bash
anylover init \
  --name "Any" \
  --persona "Um companheiro de IA espirituoso, com opiniões claras e um toque de sarcasmo, que aponta contradições sem humilhar." \
  --style "Breve, conversacional e levemente sarcástico. Toda crítica deve trazer uma alternativa útil. Se eu disser para parar, pare imediatamente."
```

## Instalação

Você precisa de macOS ou Linux e Python 3.11 ou superior. Na raiz do repositório:

```bash
bash install.sh --agent auto
```

Para um único agente:

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
```

Uma entrada MCP existente chamada `anylover` não é substituída sem `--force-agent-config`. Reinicie o agente depois da instalação.

## Uso

Em conversas pessoais, o Skill responde no idioma da mensagem atual e recupera apenas o contexto relevante. A conversa completa não é salva automaticamente.

```text
Use o AnyLover, leia o perfil compartilhado e as memórias relevantes e descreva sua personalidade atual em português.
```

Você também pode controlar a memória explicitamente:

```text
Lembre-se disto: prefiro explicações curtas e diretas.
Liste tudo o que você lembra sobre mim.
Esqueça essa última memória.
```

Senhas, chaves de API, tokens, cookies, chaves privadas e transcrições completas nunca são armazenados. O custo dos tokens é cobrado pelo agente ou provedor de modelos que você usa; o AnyLover não intermedeia a geração.

## Superfícies compatíveis

| Superfície | Status |
|---|---|
| Codex / ChatGPT para desktop | ✅ Funciona |
| Claude Code | ✅ Funciona |
| WorkBuddy 5.3.x | ✅ Experimental |
| Agente CLI | ✅ MCP ou `anylover context` |
| ChatGPT Web | ⬜ Requer um gateway MCP remoto |
| iOS / Android | ⬜ No roadmap |

## Dados e backup

O banco padrão é `~/.anylover/anylover.sqlite3` e o runtime privado é `~/.local/share/anylover-runtime/venv`. O SQLite principal ainda não é criptografado em repouso; ative a criptografia completa do disco.

```bash
export ANYLOVER_BACKUP_PASSPHRASE="uma frase longa e exclusiva"
anylover backup create "backups/anylover-$(date +%F).albackup"
```

## Desenvolvimento e roadmap

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

Veja [language support](../04-localization.md), o [roadmap](../03-roadmap.md) e o modelo de ameaças em [SECURITY.md](../../SECURITY.md).

## Licença

[Apache License 2.0](../../LICENSE)
