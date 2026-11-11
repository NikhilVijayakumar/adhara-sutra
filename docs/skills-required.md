For AdharaSutra, there are several free, open-source Agent Skills you can reuse rather than writing every development workflow from scratch.

Since AdharaSutra covers Python infrastructure, CLI protocols, Electron, connectors, architecture verification, migration, security, testing, and packaging, I'd use a curated collection of skills, not one large skills repository enabled indiscriminately.

These are particularly useful with Claude Code, Codex, and OpenCode.

## 1. Best open-source skill repositories

[GitHub - addyosmani/agent-skills: Production-grade engineering skills for AI coding agents. · GitHub](https://images.openai.com/static-rsc-4/ykLXEuvSjUsBEoBsRLhuEYrRLCaBDu_npNphAyrwdSg3hF_EgVaKZnpK5porzPmiZa8fV55Y1AKulDXd_xjP8XgFRSKF9takhfeloowQ8fRGs-9GhedMftfXSU6vjGM4U4v0lH1s-eRLknEQawLM_9AILmNMwQX51zG0SZSPeoE?purpose=inline)

[wshobson/agents](https://github.com/wshobson/agents?utm_source=chatgpt.com)

My first choice for AdharaSutra. Includes skills for Python packaging, async programming, testing, architecture patterns, TypeScript, security, and technical documentation.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Free • Open-source • Broad technical coverage

[GitHub 热榜项目 - 日榜(2026-03-20) - 技术栈](https://images.openai.com/static-rsc-4/EKM6SAPZ--R3RjNT7cDeQfT83ldschEWLSFKcEvOXMQMZNgM2PrwLsVdd2_YfjRWyXgH-Czfal2YiLVdB6xHox6TxaSLzqd8-uOYXHPmh3Ct_7Rqhkv41R1aQ3rGh6ZV5y7t4DMX3gXLICD8M_9jWR5qTikJY91FEFu7Oeu7eHg?purpose=inline)

[obra/superpowers](https://github.com/obra/superpowers?utm_source=chatgpt.com)

Structured development workflow: planning, test-driven development, debugging, verification, and review. Useful for implementing AdharaSutra modules incrementally.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://agskills.dev\&sz=32)

agskills.dev



Free • MIT license

[skills/skills/frontend-design/SKILL.md at main · anthropics/skills · GitHub](https://images.openai.com/static-rsc-4/HHHGBrVTM0DZkJdmWfDHOxDe0zCFQZ1l1KUQztBvYnTVErejgvbpJ6Zft6a2Ou55gKxZr0HL6bllKK1YTjwpK_h3kRsl7S0gZ9MX2GFRxazbJLE3jJLqh6ScYfT820Gl3SwjrSthtTA05-WsXA8QxvB4uJTBYVNeHcnqh4cbs1k?purpose=inline)

[anthropics/skills](https://github.com/anthropics/skills?utm_source=chatgpt.com)

Reference implementation of the Agent Skills format, including skill creation and evaluation resources. Useful when developing AdharaSutra-specific skills. Check individual folder licenses.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Public repository • Mixed component licensing

[GitHub - vercel-labs/agent-browser: Browser automation CLI for AI agents](https://images.openai.com/static-rsc-4/Kmax9QRP2NfCu5j3K7g3NlZEKzFO59Q5CiLH9Ivd20QzaYHwpq6M1ijfErLElU06hk2G-mnqXcdb38UXZi08QsmBQM-lruY8Bp6FKR3u93rihbTmTcDTT2Ot9dRck-M8qcUawf_d5we5MtplizK-WLXCa07Ffiu3Zzwy00PT8dY?purpose=inline)

[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser?utm_source=chatgpt.com)

Includes an Electron automation skill for desktop UI testing and inspection. Useful for validating packaged Electron applications.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://openskills.app\&sz=32)

Open Skills



Free tooling • Electron automation

## 2. Skills mapped to AdharaSutra

The following skill names are available in the identified repositories. The last column is how I'd prioritize them for your framework.

| Skill                             | AdharaSutra use                                        | Priority  |
| --------------------------------- | ------------------------------------------------------ | --------- |
| `architecture-patterns`           | DDD, hexagonal layers, adapters, dependency boundaries | Essential |
| `async-python-patterns`           | Async runtime, concurrency, cancellation               | Essential |
| `python-type-safety`              | Public API contracts, protocols, typing                | Essential |
| `python-testing-patterns`         | pytest, fixtures, contract tests                       | Essential |
| `python-packaging`                | Wheels, `pyproject.toml`, PyPI                         | Essential |
| `javascript-testing-patterns`     | Electron bridge TypeScript tests                       | High      |
| `uv-package-manager`              | Python dependency and environment management           | High      |
| `sast-configuration`              | Security scanning and CI                               | High      |
| `stride-analysis-patterns`        | Trust-boundary threat modeling                         | High      |
| `architecture-decision-records`   | Architecture decision documentation                    | High      |
| `changelog-automation`            | Release history                                        | Medium    |
| `python-performance-optimization` | Runtime and protocol benchmarking                      | Medium    |
| `typescript-advanced-types`       | Type-safe Electron bridge interfaces                   | Medium    |
| `multi-reviewer-patterns`         | Cross-agent architecture/code reviews                  | Medium    |
| `test-driven-development`         | Test-first implementation and verification             | Essential |

The `wshobson/agents` catalog includes the Python, architecture, security, review, and documentation skills. `test-driven-development` comes from `obra/superpowers`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+2



## 3. Install the recommended skills

You can install individual skills with the open-source Skills CLI. It supports multiple coding-agent environments.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://vercel.com\&sz=32)

Vercel



For the initial AdharaSutra implementation, I'd start with these:

```
# Architecture
npx skills add wshobson/agents --skill architecture-patterns

# Python infrastructure
npx skills add wshobson/agents --skill async-python-patterns
npx skills add wshobson/agents --skill python-type-safety

# Testing
npx skills add wshobson/agents --skill python-testing-patterns
npx skills add obra/superpowers --skill test-driven-development

# Packaging and releases
npx skills add wshobson/agents --skill python-packaging
npx skills add wshobson/agents --skill uv-package-manager

# Security
npx skills add wshobson/agents --skill sast-configuration
npx skills add wshobson/agents --skill stride-analysis-patterns

# Architecture documentation
npx skills add wshobson/agents --skill architecture-decision-records
```

For Electron development and testing, add:

```
npx skills add wshobson/agents --skill javascript-testing-patterns
npx skills add wshobson/agents --skill typescript-advanced-types
npx skills add vercel-labs/agent-browser --skill electron
```

Review each skill's instructions and scripts before installation, particularly those capable of running commands or modifying files.

## 4. What existing skills do not fully cover

For AdharaSutra, I would reuse those general-purpose skills and eventually create a small set of project-specific Agent Skills.

| Proposed AdharaSutra skill         | Responsibility                                                 |
| ---------------------------------- | -------------------------------------------------------------- |
| `adhara-architecture`              | Apply approved module and dependency boundaries                |
| `adhara-runtime`                   | Implement runtime, lifecycle, DI, and action registration      |
| `adhara-cli-protocol`              | Enforce NDJSON messages, errors, concurrency, and cancellation |
| `adhara-connectors`                | Implement HTTP, WebSocket, process, and SQLite contracts       |
| `adhara-electron`                  | Integrate the shared bridge and packaged Python backend        |
| `adhara-testing`                   | Generate applicable contract, integration, and fault tests     |
| `adhara-architecture-verification` | Interpret and resolve verifier findings                        |
| `adhara-migration`                 | Plan and execute controlled legacy migration                   |
| `adhara-packaging`                 | Build and verify Python/npm/desktop artifacts                  |

These do not exist as ready-made AdharaSutra skills; they are proposed skills to create after the architecture contracts are finalized.

Your existing cross-agent workflow can then share the same `SKILL.md` files rather than maintaining separate architectural instructions for Claude Code, Codex, and OpenCode.

## 5. Recommended adoption sequence

Phase 1 — Reuse existing skills

Install architecture, Python, testing, packaging, and security skills. Use them to implement the foundational AdharaSutra components.

Phase 2 — Finalize your architecture documents

Resolve cross-document differences, approve public contracts, and define the architecture profile and rule catalogs.

Phase 3 — Create AdharaSutra-specific skills

Use the approved documents to create compact, task-focused skills that reference the relevant contracts without copying entire design documents into every skill.

Phase 4 — Add your formal implementation workflow

Introduce OpenSpec and your existing workflow standards only after the foundational architecture has been reviewed and finalized.

My recommendation: Start with the `wshobson/agents` skills plus `obra/superpowers`. They cover a substantial portion of the engineering workflow, while AdharaSutra-specific skills can enforce the framework's unique requirements.

A useful distinction: skills guide coding agents; AdharaSutra's actual architecture verifier, test suite, and build pipeline enforce correctness. Skills should invoke and interpret those tools, not replace them.