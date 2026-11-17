"""Resolve model credentials and endpoints for the runtime and its benchmark."""
from dataclasses import dataclass, field
import os
from urllib.parse import urlsplit, urlunsplit

DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"


@dataclass(frozen=True)
class ModelConnection:
    model: str
    api_key: str = field(repr=False)
    endpoint: str
    kind: str


def add_model_arguments(parser):
    parser.add_argument("--model", help="Provider model name or LiteLLM gateway alias")
    endpoint = parser.add_mutually_exclusive_group()
    endpoint.add_argument("--endpoint", help="Full OpenAI-compatible Chat Completions URL")
    endpoint.add_argument("--litellm-base-url", help="LiteLLM gateway URL, with an optional trailing /v1")


def _litellm_endpoint(base_url):
    try:
        parts = urlsplit(base_url)
        port = parts.port
    except ValueError as exc:
        raise ValueError("Invalid LiteLLM gateway base URL") from exc
    if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username is not None
            or parts.password is not None or parts.query or parts.fragment or port == 0):
        raise ValueError("LiteLLM gateway base URL must be HTTP(S) without credentials, query, or fragment")
    if any(character.isspace() for character in base_url):
        raise ValueError("LiteLLM gateway base URL cannot contain whitespace")
    path = parts.path.rstrip("/")
    if path.endswith("/chat/completions"):
        raise ValueError("Pass the gateway base URL, without /chat/completions, to --litellm-base-url")
    if not path.endswith("/v1"):
        path += "/v1"
    return urlunsplit((parts.scheme, parts.netloc, path + "/chat/completions", "", ""))


def resolve_model_connection(args):
    model = args.model if args.model is not None else os.getenv("OPENAS_GUI_MODEL")
    endpoint = args.endpoint
    gateway = args.litellm_base_url
    if gateway == "":
        raise ValueError("--litellm-base-url requires a nonempty URL")
    if endpoint is None and gateway is None:
        endpoint = os.getenv("OPENAS_GUI_API_URL")
        gateway = os.getenv("OPENAS_LITELLM_BASE_URL")
        if endpoint and gateway:
            raise ValueError("Both model routes are configured. Select --endpoint or --litellm-base-url explicitly.")

    if gateway:
        key_name = "LITELLM_API_KEY"
        kind = "litellm"
        endpoint = _litellm_endpoint(gateway)
    else:
        key_name = "OPENAS_GUI_API_KEY"
        kind = "openai-compatible"
        if endpoint == "":
            raise ValueError("The direct model endpoint requires a nonempty URL")
        if endpoint is None:
            endpoint = DEFAULT_ENDPOINT
    key = os.getenv(key_name)
    if not key or not model:
        raise ValueError(f"Set {key_name} and OPENAS_GUI_MODEL (or --model)")
    return ModelConnection(model, key, endpoint, kind)
