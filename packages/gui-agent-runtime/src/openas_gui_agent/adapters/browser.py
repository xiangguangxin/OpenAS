"""Playwright-backed browser tools for an explicitly selected test application."""
from contextlib import contextmanager
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urljoin, urlsplit


def _origin(url):
    parts = urlsplit(url)
    if (parts.scheme not in {"http", "https"} or not parts.hostname
            or parts.username is not None or parts.password is not None):
        raise ValueError("Expected an HTTP(S) URL without credentials")
    return parts.scheme, parts.hostname, parts.port or (443 if parts.scheme == "https" else 80)


def _tool(tool_name, description, *arguments):
    return {"name": tool_name, "description": description, "inputSchema": {
        "type": "object", "properties": {key: {"type": "string"} for key in arguments},
        "required": list(arguments), "additionalProperties": False}}


TOOLS = (
    _tool("browser_navigate", "Navigate to a same-origin URL or relative path.", "url"),
    _tool("browser_click", "Click a visible element by exact accessible role and name.", "role", "name"),
    _tool("browser_fill", "Fill a visible field by exact accessible label. Use only test data.", "label", "text"),
    _tool("browser_wait_for_text", "Wait for exact visible text for at most 10 seconds.", "text"),
)
DOWNLOAD = _tool("browser_download", "Click the exact role/name and save the download under a new filename.",
                 "role", "name", "filename")


class Browser:
    def __init__(self, page, start_url, download_dir=None, *, timeout=10_000):
        self.page = page
        self.start_url = start_url
        self.origin = _origin(start_url)
        self.download_dir = download_dir
        self.timeout = timeout
        self.tools = TOOLS if download_dir is None else (*TOOLS, DOWNLOAD)
        self.opened = False

    def allows(self, url):
        try:
            return _origin(url) == self.origin
        except ValueError:
            return False

    def _check_page(self):
        if not self.allows(self.page.url):
            raise ValueError("Browser is outside the configured origin")

    def observe(self):
        if not self.opened:
            self.page.goto(self.start_url, wait_until="domcontentloaded", timeout=self.timeout)
            self.opened = True
        self._check_page()
        address = urlsplit(self.page.url)
        return {"summary": f"Browser page {address.path or '/'}",
                "action_scope": self.page.url,
                "ui_tree": self.page.locator("body").aria_snapshot(timeout=self.timeout)[:5000],
                "tools": list(self.tools)}

    def _download_target(self, filename):
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", filename) or filename.endswith("."):
            raise ValueError("Use a plain filename for the download")
        if filename.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
                                                 *(f"COM{i}" for i in range(1, 10)),
                                                 *(f"LPT{i}" for i in range(1, 10))}:
            raise ValueError("Reserved download filename")
        target = self.download_dir / filename
        if target.exists() or target.is_symlink():
            raise ValueError("Download target already exists")
        return target

    def _save_download(self, download, target):
        # Stage beside the target, then publish atomically without replacing it.
        with tempfile.TemporaryDirectory(dir=self.download_dir) as folder:
            staged = Path(folder) / "download"
            download.save_as(staged)
            os.link(staged, target)

    def act(self, action):
        from playwright.sync_api import TimeoutError as BrowserTimeout

        self._check_page()
        name = action["name"]
        arguments = action.get("arguments", {})
        tool = next((tool for tool in self.tools if tool["name"] == name), None)
        if (tool is None or not isinstance(arguments, dict)
                or arguments.keys() != set(tool["inputSchema"]["required"])
                or not all(isinstance(value, str) and len(value) <= 4000 for value in arguments.values())):
            return {"ok": False, "summary": "Invalid browser action or arguments"}
        if name == "browser_navigate":
            url = urljoin(self.page.url, arguments["url"])
            if not self.allows(url):
                return {"ok": False, "summary": "Navigation is outside the configured origin"}
            self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
        elif name == "browser_wait_for_text":
            try:
                self.page.get_by_text(arguments["text"], exact=True).wait_for(
                    state="visible", timeout=self.timeout)
            except BrowserTimeout:
                return {"ok": False, "summary": "Expected browser text not visible before timeout"}
        elif name == "browser_fill":
            self.page.get_by_label(arguments["label"], exact=True).fill(arguments["text"], timeout=self.timeout)
        else:
            locator = self.page.get_by_role(arguments["role"], name=arguments["name"], exact=True)
            if name == "browser_download":
                try:
                    target = self._download_target(arguments["filename"])
                except ValueError as error:
                    return {"ok": False, "summary": str(error)}
                with self.page.expect_download(timeout=self.timeout) as pending:
                    locator.click(timeout=self.timeout)
                self._save_download(pending.value, target)
            else:
                locator.click(timeout=self.timeout)
        self._check_page()
        return {"ok": True, "summary": f"{name} completed"}


@contextmanager
def open_browser(start_url, download_dir=None, executable=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Install openas-gui-agent[browser] and Chromium for browser goals") from exc

    _origin(start_url)
    if download_dir is not None:
        download_dir = Path(download_dir).resolve(strict=True)
        if not download_dir.is_dir():
            raise ValueError("Expected a download directory")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable)
        try:
            context = browser.new_context(accept_downloads=True, service_workers="block")
            try:
                adapter = Browser(context.new_page(), start_url, download_dir)
                context.route("**/*", lambda route: (
                    route.continue_() if adapter.allows(route.request.url) else route.abort()))
                yield adapter
            finally:
                context.close()
        finally:
            browser.close()
