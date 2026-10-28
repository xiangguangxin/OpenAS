"""Agent execution boundary. Backends are trusted host code, not task plugins.

Capabilities describe adapter contracts, not detected client versions or stronger
security guarantees than the selected client's actual execution environment.
"""
from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import NamedTuple


class BackendError(ValueError):
    def __init__(self, message, kind='backend_capability'):
        super().__init__(message)
        self.kind = kind


class AgentRequest(NamedTuple):
    client: str
    workspace: Path
    prompt: str
    access: str
    timeout: float
    schema_file: Path
    result_file: Path
    stdout_file: Path
    stderr_file: Path
    search_mode: str = None
    execution_events: bool = False


class AgentInvocation(NamedTuple):
    request: AgentRequest
    argv: tuple


class AgentResult(NamedTuple):
    exit_code: int
    native_search_count: int = 0


class AgentBackend(ABC):
    name = 'abstract'
    version = 1
    capabilities = frozenset()

    def identity(self):
        """Change version when a provider's execution semantics change."""
        return {'name': self.name, 'version': self.version,
                'capabilities': sorted(self.capabilities)}

    def require(self, capabilities):
        missing = set(capabilities) - self.capabilities
        if missing:
            raise BackendError(f'Backend {self.name} lacks required capabilities: {", ".join(sorted(missing))}')

    def validate(self, request):
        if request.access not in ('read-only', 'workspace-write'):
            raise BackendError('Unsupported access mode')
        if request.search_mode not in (None, 'live', 'disabled'):
            raise BackendError('Unsupported search mode')
        if request.timeout <= 0:
            raise BackendError('Positive execution timeout required')
        required = {request.access, 'structured-output', 'timeout', 'cancellation'}
        if request.search_mode is not None:
            required.add('search-control')
        if request.search_mode == 'live':
            required.add('native-search-evidence')
        if request.execution_events:
            required.add('execution-events')
        self.require(required)

    @abstractmethod
    def prepare(self, request):
        """Validate and prepare execution without starting a process."""

    @abstractmethod
    def run(self, invocation, execute):
        """Execute using the host's timeout/cancellation-aware process runner.

        Write the final JSON to request.result_file and process evidence to the
        requested log files. Return exit status and provider-normalized evidence.
        The workflow owns result validation, scope checks and acceptance.
        """


class CodexBackend(AgentBackend):
    name = 'codex'
    capabilities = frozenset({'read-only', 'workspace-write', 'structured-output',
                              'timeout', 'cancellation', 'search-control',
                              'execution-events', 'native-search-evidence'})

    def prepare(self, request):
        self.validate(request)
        argv = [request.client, 'exec', '--ephemeral', '--skip-git-repo-check', '--color', 'never',
                '--sandbox', request.access, '-C', str(request.workspace),
                '--output-schema', str(request.schema_file), '-o', str(request.result_file), '-']
        options = []
        if request.execution_events:
            options.append('--json')
        if request.search_mode is not None:
            options.extend(['-c', 'web_search="' + request.search_mode + '"'])
        argv[2:2] = options
        return AgentInvocation(request, tuple(argv))

    def run(self, invocation, execute):
        request = invocation.request
        self.validate(request)
        rc = execute(list(invocation.argv), request.workspace, request.timeout,
                     request.stdout_file, request.stderr_file, request.prompt)
        count = 0
        if rc == 0 and request.search_mode == 'live' and request.execution_events:
            for line in request.stdout_file.read_text().splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if (isinstance(event, dict) and event.get('type') == 'item.completed'
                        and isinstance(event.get('item'), dict)
                        and event['item'].get('type') == 'web_search'):
                    count += 1
        return AgentResult(rc, count)
