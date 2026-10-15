# AnyLover

**Un compañero de IA que mantiene la misma identidad y memoria en Codex, ChatGPT, Claude Code, WorkBuddy y futuras aplicaciones móviles, con los datos bajo tu control.**

[English](../../README.en.md) · [简体中文](../../README.md) · [日本語](ja.md) · [한국어](ko.md) · [Português](pt.md) · [Русский](ru.md)

> **Estado: vista previa M0.** Es un runtime funcional para desarrolladores y primeros usuarios, no una aplicación de chat de consumo terminada.

## Lo que ya funciona

- ✅ Una identidad y memoria local compartida entre superficies
- ✅ Cinco tipos de memoria: fact, preference, boundary, event y reflection
- ✅ Procedencia, base de consentimiento, correcciones, supersedes, deduplicación, tombstones de borrado y auditoría
- ✅ Adaptadores para Codex, ChatGPT de escritorio, Claude Code, WorkBuddy y agentes CLI
- ✅ CLI, servidor MCP STDIO y API HTTP autenticada
- ✅ Copias cifradas con scrypt + AES-256-GCM, restauración y transferencia HTTPS
- ✅ Instalador de un clic que detecta agentes y combina configuraciones de forma segura
- ✅ Texto Unicode y recuperación léxica determinista para varios sistemas de escritura

## Personalidad predeterminada

Any es un compañero de IA con opiniones y un toque de sarcasmo. Señala contradicciones y excusas débiles, y después ofrece una alternativa útil. No humilla ni ataca la identidad, el aspecto, los traumas, la salud o las vulnerabilidades conocidas; tampoco usa recuerdos privados como arma. Si dices “para”, se detiene.

Puedes definir una personalidad en español:

```bash
anylover init \
  --name "Any" \
  --persona "Un compañero de IA ingenioso, con opiniones claras y un toque de sarcasmo, que señala las contradicciones sin humillar." \
  --style "Breve, conversacional y ligeramente sarcástico. Cada crítica debe incluir una alternativa útil. Si digo que pares, paras inmediatamente."
```

## Instalación

Necesitas macOS o Linux y Python 3.11 o posterior. Desde la raíz del repositorio:

```bash
bash install.sh --agent auto
```

Para un solo agente:

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
```

Una entrada MCP existente llamada `anylover` no se reemplaza salvo que uses explícitamente `--force-agent-config`. Reinicia el agente después de instalar.

## Uso

En conversaciones personales, el Skill responde en el idioma del mensaje actual y recupera solo el contexto relevante. No guarda automáticamente la conversación completa.

```text
Usa AnyLover, carga el perfil y los recuerdos relevantes, y descríbeme tu personalidad actual en español.
```

También puedes controlar la memoria de forma explícita:

```text
Recuerda esto: prefiero explicaciones breves y directas.
Enumera todo lo que recuerdas sobre mí.
Olvida ese último recuerdo.
```

Nunca se guardan contraseñas, claves API, tokens, cookies, claves privadas ni transcripciones completas. El coste de los tokens lo cobra el agente o proveedor de modelos que utilices; AnyLover no intermedia la generación.

## Superficies compatibles

| Superficie | Estado |
|---|---|
| Codex / ChatGPT de escritorio | ✅ Funciona |
| Claude Code | ✅ Funciona |
| WorkBuddy 5.3.x | ✅ Experimental |
| Agente CLI | ✅ MCP o `anylover context` |
| ChatGPT Web | ⬜ Requiere un gateway MCP remoto |
| iOS / Android | ⬜ En el roadmap |

## Datos y copias de seguridad

La base de datos predeterminada es `~/.anylover/anylover.sqlite3` y el runtime privado es `~/.local/share/anylover-runtime/venv`. La base SQLite principal todavía no está cifrada en reposo; activa el cifrado completo del disco.

```bash
export ANYLOVER_BACKUP_PASSPHRASE="una frase larga y única"
anylover backup create "backups/anylover-$(date +%F).albackup"
```

## Desarrollo y roadmap

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

Consulta [language support](../04-localization.md), el [roadmap](../03-roadmap.md) y el modelo de amenazas en [SECURITY.md](../../SECURITY.md).

## Licencia

[Apache License 2.0](../../LICENSE)
