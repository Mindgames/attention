# Attention Please

A Codex and Claude Agent SKILL that pings and speaks when a run ends or needs input.

![Support](supported.png)

Attention Please is an Agent SKILL that boosts your productivity by telling you when a turn ends or when your input is required.

Compatible with macOS today. Windows and Linux are coming soon (contributions welcome).

## Install

### Codex

Global install (available in all projects), then restart Codex:

```bash
git clone https://github.com/Mindgames/attention-please.git ~/.codex/skills/public/attention-please
```

Project install (only this repo), then restart Codex:

```bash
git clone https://github.com/Mindgames/attention-please.git /path/to/your-repo/.codex/skills/attention-please
```

### Claude Code / Claude CLI

Global install (available in all projects), then restart Claude:

```bash
git clone https://github.com/Mindgames/attention-please.git ~/.claude/skills/attention-please
```

Project install (only this repo), then restart Claude:

```bash
git clone https://github.com/Mindgames/attention-please.git /path/to/your-repo/.claude/skills/attention-please
```

## Instruct your Agent

Tell your agent to run the skill at the end of each turn or when input/confirmation is needed:

```text
$attention-please update AGENTS.md to run the attention-please skill at the end of each turn or when input/confirmation is needed.
```

---

Follow me on X: https://x.com/mathiiias123
