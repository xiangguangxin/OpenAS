# Playwright MCP

[中文](README.md) | English

Explore pages, perform user actions, inspect structure, and check interactions for test-engineer, verifier, and ux-designer tasks. Prefer existing stable Playwright tests; interactive MCP operations do not replace persistent regressions.

## Concepts

Playwright automates browser navigation, buttons, forms, and result checks. End-to-end (E2E) tests verify complete user paths, such as login → dashboard → user details.

| Component | Purpose | OpenAS use |
| --- | --- | --- |
| Playwright | Browser automation APIs | Programs interacting with pages |
| Playwright Test | Execution, assertions, isolation, parallelism, reports | Repeatable critical-path regressions and CI |
| Playwright MCP | Browser tools exposed to assistants | Exploration, interactions, and evidence for this check |

Core objects:

- **Browser:** launched or connected browser instance.
- **BrowserContext:** isolated cookies/login/browser data, suitable for multiple users; server data still needs preparation/cleanup.
- **Page:** tab for navigation, content inspection, and screenshots.
- **Locator:** target description; prefer stable roles, accessible names, and labels.
- **Action / Assertion:** clicking/filling are actions; verifying navigation, messages, or data are assertions. A click alone is not business acceptance.

References: [Playwright Test introduction](https://playwright.dev/docs/intro), [browser contexts](https://playwright.dev/docs/browser-contexts).

## Capabilities and use cases

| Capability | Purpose | Usage notes |
| --- | --- | --- |
| Page operations/E2E | Login, search, submissions | Cover success/failure and actual business outcomes |
| Auto-waiting/retrying assertions | Asynchronous controls and states | Actionability and web assertions wait for their conditions; still define business completion instead of fixed sleeps |
| Multiple browsers | Chromium, Firefox, WebKit compatibility | Declare target browsers in project tests; one MCP session does not cover all browsers |
| Isolated sessions/multiple users | Avoid authentication contamination | Separate Contexts and corresponding test accounts |
| Screenshots/visual comparison | Preserve state and detect layout changes | Automated comparison also needs baselines and stable environments |
| Traces/video/reports | Locate failing steps | Enable in project configuration; verify actual MCP recording tools separately |

References: [auto-waiting](https://playwright.dev/docs/actionability), [visual comparisons](https://playwright.dev/docs/test-snapshots), [Trace Viewer](https://playwright.dev/docs/trace-viewer).

### Minimal test example

This Playwright Test example requires an existing `@playwright/test` installation, browsers/dependencies, and a running local application exposing the matching controls/messages. It illustrates actions/assertions, not MCP configuration or a test already executed by OpenAS. Chinese selectors remain unchanged because they must match the example application's actual UI.

```javascript
import { test, expect } from '@playwright/test';

test('用户能够登录', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('用户名').fill('alice');
  await page.getByLabel('密码').fill('test-password');
  await page.getByRole('button', { name: '登录' }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText('欢迎，alice')).toBeVisible();
});
```

`await` waits for the asynchronous step. Use test accounts/data. Save persistent scenarios in target-project test files and run its commands. Test engineers design/maintain flows, verifiers inspect acceptance evidence, and UX designers assess interactions/layout. Pure algorithms, CLI tools, or simulator internals need appropriate non-browser tests; use Playwright for actual web interfaces.

## Configuration

The [Claude Code example](claude.mcp.example.json) pins `@playwright/mcp@0.0.83`, using `npx`, headless mode, and isolated sessions. Package metadata requires Node >=18; execution also needs compatible browsers/system dependencies. First launch may download npm content. Follow version-specific upstream guidance for missing browsers rather than changing system dependencies merely to verify a task. See [integration configuration](../README.en.md).

Closing an isolated session discards login state, but isolation is not a network/action-permission sandbox or server-data cleanup. The default does not attach to everyday browsers or load personal profiles.

## Procedure

1. Derive authorized URL, account, initial state, actions, and expectations from original acceptance; use only authorized sites/test data.
2. Discover actual tools, navigate, inspect structure, and locate controls from the current snapshot. Refresh structure after changes instead of reusing stale references.
3. Exercise representative success/failure paths, checking feedback and necessary backend effects. Wait for observable states with deadlines, not fixed sleeps.
4. Save screenshots/snapshots only at allowed locations and record URL, environment, steps, and expected/actual results; omit passwords, cookies, and sensitive forms from reports.
5. Close the session and clean up this test's data using established procedures; hand persistent regressions to project-native tests.

Accessibility snapshots establish only some structure, not contrast, full keyboard experience, or screen-reader behavior. Use [accessibility-review](../../skills/accessibility-review/SKILL.en.md) to state coverage.

## Minimal acceptance and fallback

Navigate an authorized local test page, read title and a visible control, perform a side-effect-free action, verify state, and close the browser. Record actual tools/results. Without tools run existing browser tests or supply manual steps, marking interactive checks unexecuted; static source inspection is not a browser pass.

Sources: [official repository](https://github.com/microsoft/playwright-mcp), [0.0.83 package metadata](https://registry.npmjs.org/@playwright/mcp/0.0.83). Upstream uses Apache-2.0; this directory contains independent guidance/configuration, not copied server source.
