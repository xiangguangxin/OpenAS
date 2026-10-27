# Plugin architecture and loading boundaries

[中文](architecture.md) | English

OpenAS distributes one native plugin, `openas`. The root marketplace says where to find it, and its manifest identifies it. The host discovers skills, registers agents, manages lifecycle, and reloads resources. OpenAS does not introduce a competing plugin registry or resident process.

```text
OpenAS/.claude-plugin/marketplace.json
                 | source: ./plugins/openas
                 v
     plugins/openas/.claude-plugin/plugin.json
                 |
        +--------+-----------+
        v        v           v
      skills/  agents/    workflows/ (optional Codex adapter)
        |        |           |
        +---- references/ ---+
                 | explicit consumer project
                 v
       consumer/.openas/memory/
```

## Resources and state

The plugin contains versioned prompts, skills, references, templates, and optional scripts using plugin-relative links. The Python adapter locates roles, project adaptation, and memory from its own path, independently of consumer layout.

Project state belongs only to the consumer. Memory CLI requires `--root`; the adapter exposes `--project-root`. Neither the plugin nor its subdirectories may be memory targets. Knowledge survives plugin deletion, and another project's records.json is not injected into new projects. Cross-project sharing requires reviewed migration, not an implicit global singleton.

Roles share [project adaptation](../plugins/openas/references/project-context.en.md), discovering target stack/acceptance without another fixed configuration format. The Codex adapter passes the full conventions/task to each role; Claude roles use the team contract and the JS template carries adaptation guidance. Python/Node are script runtimes, not mandatory development languages for consumers.

## Lifecycle

- Local development: load `--plugin-dir`, then `/reload-plugins`. Automatic file discovery, cache behavior, and reloadable components depend on the actual client.
- Persistent use: marketplace → install → enable/disable/uninstall → reload. Cached installations require version updates; repository edits do not necessarily update caches.
- In-flight calls may retain old code. Reload affects subsequent work. There is no custom background process to terminate on removal.
- Validate structure/links before reload. On failure inspect client plugin errors and fix disk content, reload, or restore a known Git version. OpenAS does not implement a client rollback controller.

## Client differences

Claude Code natively consumes plugin.json and `openas:` IDs. Codex does not consume this manifest; the optional adapter reads shared resources and calls an installed CLI. JS orchestration still requires host-injected agent/args/log.

Shared principles do not mean identical executors. Report structure, mock-host, real-model, and native-Claude results separately. REA MCP/engines are optional, not automatic installation steps.

## Orchestration and persistent state

The single-task Python runner selects `workflow` and stores successful stages in versioned records. Resumption checks task, options, source snapshots, rule fingerprints, and stage results; changed source/rules cannot silently reuse old reviews. Host checks/verifier rerun and revision budgets remain.

handoff.json holds current context, and acceptance.json separates machine checks from model review; both are distinct from long-term memory. reviewed means read-only review delivery, not an implementation-verified fact eligible for automatic harvesting.

graph-runner.py validates dependencies before clients start and executes nodes sequentially with actual upstream results. Failures block dependents while independent nodes may continue; user interruption prevents further starts. There is no concurrent scheduling or automatic whole-graph recovery. See the [skill directory](../plugins/openas/skills) and [workflow guide](../plugins/openas/workflows/README.en.md).
