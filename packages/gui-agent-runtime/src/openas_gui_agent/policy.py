"""Desktop action risk checks; not a sandbox."""
import hashlib, json, re
SENSITIVE = {"delete", "overwrite", "send", "pay", "install", "permissions", "export", "commit"}
def needs_approval(action):
    return action.get("impact") != "low" or any(re.search(r"(^|[_-])" + word + r"([_-]|$)", str(action.get("name", "")).lower()) for word in SENSITIVE)
def fingerprint(action):
    return hashlib.sha256(json.dumps(action, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
