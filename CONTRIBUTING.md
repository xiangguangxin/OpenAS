# Contributing

Make changes on a separate branch and preserve existing user edits. Keep roles, skills, and documentation broadly applicable. Put domain-specific examples in separate fixtures rather than making them default rules for other projects.

## Validate changes

Use Python 3.10+ and Node.js 22 on Linux / WSL. Follow the [README](README.md) to run structural validation, both Python test suites, and the JavaScript tests.
For new behavior, first add tests that reproduce the defect; for text-only changes, check sources, links, and the diff. Do not repair intentionally failing fixtures in the distributed source directory; copy them to a temporary directory first.

When changing skills, check trigger scope, existing authorization, project constraints, and failure handoffs. Run relevant tasks on an available client following the [behavior evaluation guide](docs/skill-evaluation.md). Ordinary unit tests cannot establish correct model behavior. Real-client evaluations consume model quota and are not part of default CI.

PR descriptions should state the problem, changes, actual validation commands, and coverage gaps. Report CI results separately from native-client validation. Do not commit authentication information, full client logs, or user project data.

## Updates and releases

1. Run relevant checks and review the diff; confirm that vendored REA files and licenses have not been changed accidentally.
2. Update the plugin manifest version and CHANGELOG. When changing record formats, document the migration procedure.
3. Follow the [compatibility notes](docs/compatibility.md) to check current client arguments, native loading, and hot reload. Leave checks incomplete when the required environment is unavailable.
4. After PR approval and merge, confirm main-branch CI. Create the corresponding Git tag / Release only with explicit release authorization; users can then update their marketplace caches.

Project-owned content uses the [MIT License](LICENSE). The original licenses and provenance of third-party REA remain in the [integration directory](plugins/openas/integrations/rea/README.md).

## Bilingual maintenance

Keep paired Chinese and English editions of roles and project-owned skills, following the [bilingual maintenance guide](docs/bilingual.md). When changing shared behavior, review the translations together and verify their meaning before updating translations.json fingerprints. Structural checks do not replace translation-quality review or real-client behavior evaluation.
