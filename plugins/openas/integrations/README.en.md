# Optional MCP integrations

[中文](README.md) | English

OpenAS provides configuration examples and on-demand guidance; loading the plugin does not register or start these services. Reuse equivalent tools already available in the host. Tool names, arguments, and role visibility are determined by the current session's actual tool list and schemas.

| Integration | Roles and skills | Prerequisites |
| --- | --- | --- |
| [Playwright](playwright/README.en.md) | test-engineer, verifier, ux-designer; integration-testing, accessibility-review | Node/npm, browsers, and their system dependencies |
| [GitHub](github/README.en.md) | product-manager, developer, red-team, it; requirements and review workflows | Official server binary, GitHub token, and network access |
| [Context7](context7/README.en.md) | researcher, cto, developer; technical-research, technology-selection | Network access and service API key |

## Configuration and activation

Start with the [integration quick start](QUICKSTART.en.md): select services → merge configuration → supply your credentials → run local preflight → connect the client and validate each service. The bundled [configuration and checking tool](setup_mcp.py) requires Python 3.9+, merges any selection of the three services, preserves unrelated configuration, stops on name conflicts, and does not write real credentials.

```bash
python3 plugins/openas/integrations/setup_mcp.py configure --project /path/to/customer-project --services all
python3 plugins/openas/integrations/setup_mcp.py check --project /path/to/customer-project --services all
```

Run these commands from the OpenAS repository root; use the actual script path for an installed copy. Select fewer services with, for example, `--services github context7`. Preflight neither starts services nor validates network access or credentials; continue with the actual client acceptance tasks.

Each `claude.mcp.example.json` is a Claude Code project-scoped template. Merge only needed `mcpServers` entries into the target project's `.mcp.json`, retaining existing configuration rather than replacing the file. Supply environment variables to the process that starts the client; do not commit credentials. See the [official MCP documentation](https://code.claude.com/docs/en/mcp) for variable expansion. Native Windows and WSL are different environments: commands, browsers, and variables must be available in the actual host environment.

Reconnect the target project session and inspect `/mcp` or `claude mcp list`. Project configuration may require host trust confirmation. Role tool allowlists must explicitly permit the corresponding tools in the target host; this package does not expand permissions. Installing examples does not guarantee subagents can use tools.

Register separately using the configuration format of other clients, including Codex; this JSON is not directly usable by Codex. The existing Codex workflow adapter does not parse these templates, inject MCP configuration, or expand task scope/network mode. Confirm tools in the actual stage session.

To undo registration, remove only service entries added by this work, reconnect, and stop their remaining processes while preserving unrelated services. Removing registration does not revoke server credentials; manage those with the service when needed.

## Evidence and acceptance

Static validation proves only readable JSON/reference structure. A connected `/mcp` status proves discovery, not task completion. Perform each integration's minimal read-only task in the target host, recording tools, objects, version/time, results, and limitations. Distinguish startup, authentication, visibility, and task failures instead of repeatedly reinstalling.

Delivery status: configuration/preflight tools, templates, role/skill routing, and acceptance steps are provided. Only `configure` writes target-project configuration; services are not automatically installed and real MCP acceptance has not been performed with customer credentials. Hosted quotas and permissions follow current account/service rules.

Upstream configuration was checked on 2026-10-23. Pinned npm versions constrain the client package, not remote service behavior. Recheck configuration, tool schemas, and minimal tasks after upgrades or tool changes. For shipped-artifact analysis, see the separate [REA integration](rea/README.en.md).
