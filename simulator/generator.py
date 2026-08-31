import json
import urllib.error
import urllib.request
from collections.abc import Iterable
from urllib.parse import urlparse


def validate_target(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
        "backend",
    }:
        raise ValueError("Simulator target must be the local SentinelAI development stack")
    return base_url.rstrip("/")


def send_events(base_url: str, events: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    target = f"{validate_target(base_url)}/api/v1/events"
    responses = []
    for event in events:
        request = urllib.request.Request(
            target,
            data=json.dumps(event).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                responses.append(json.loads(response.read()))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach SentinelAI at {target}") from exc
    return responses
