# Attention Please

A Codex and Claude Agent SKILL that notifies you when your attention is needed.

![Support](supported.png)

Attention Please is an Agent SKILL that boosts your productivity by telling you when a turn ends or when your input is required.

Compatible with macOS today. Windows and Linux are coming soon.

## Install (skills.sh)

This skill uses the same `npx skills add` command across Codex, Claude, and other agentic CLI/IDE clients. Omit `--agent` when using the default install target for your environment.

```bash
npx skills add Mindgames/attention-please -g -y
```

Project-scoped (current repo only):

```bash
npx skills add Mindgames/attention-please
```

Install for one or more agents when needed:

```bash
npx skills add Mindgames/attention-please --agent codex
```

```bash
npx skills add Mindgames/attention-please --agent claude-code
```

Install for both clients when needed:

```bash
npx skills add Mindgames/attention-please --agent codex claude-code -g -y
```

## Instruct your Agent

Tell your agent to run the skill at the end of each turn or when input/confirmation is needed:

```text
$attention-please update AGENTS.md to run the attention-please skill at the end of each turn or when input/confirmation is needed.
```

---

Follow me on X: https://x.com/mathiiias123
