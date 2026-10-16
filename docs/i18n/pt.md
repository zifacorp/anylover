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

## Início rápido (recomendado)

Requer macOS ou Linux, Node.js/npm, Python 3.11+ e Git. Para Codex, Claude Code, Cursor e outros agentes que executam comandos locais.

Para WorkBuddy ou configuração automática do MCP, use o [instalador MCP local](../../integrations/README.md#本地-mcp-安装) como alternativa. Escolha apenas um caminho; não é necessário executar os dois.

### 1. Instale o Skill

Execute no terminal e escolha seu agente:

```bash
npx skills add zifacorp/anylover --skill anylover-companion -g
```

`-g` disponibiliza o Skill em todos os seus projetos. Omita essa opção para usar apenas no projeto atual.

### 2. Peça ao agente para concluir a configuração

Reinicie o agente ou abra uma nova sessão e envie:

> Use anylover-companion para instalar e inicializar o runtime local do AnyLover e ler o perfil do meu companheiro.

O agente instala um ambiente Python privado e preserva sua personalidade e memórias existentes. Isso conclui a instalação; não execute também `install.sh`. Esse caminho não altera a configuração MCP: sem conexão MCP, usa o CLI local.

### 3. Comece a conversar

> O que você lembra sobre mim? Conte também como é sua personalidade.

É normal não ter memórias no início. Depois, converse naturalmente. Opções por agente e atualizações estão no [guia avançado](../../integrations/README.md). A conversa em cada aplicativo ainda precisa de verificação individual.

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
