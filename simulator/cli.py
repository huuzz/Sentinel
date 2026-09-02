import argparse
import os

from simulator.generator import send_events
from simulator.scenarios import api_volume_events, brute_force_events, normal_events, password_spray_events, suspicious_success_events


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate safe synthetic SentinelAI events")
    parser.add_argument("scenario", choices=["normal", "brute-force", "password-spray", "api-volume", "suspicious-success"])
    parser.add_argument(
        "--url", default=os.getenv("SENTINEL_SIMULATOR_URL", "http://localhost:8000")
    )
    parser.add_argument("--token", default=os.getenv("SENTINEL_SIMULATOR_TOKEN"))
    args = parser.parse_args()
    scenarios = {
        "normal": normal_events,
        "brute-force": brute_force_events,
        "password-spray": password_spray_events,
        "api-volume": api_volume_events,
        "suspicious-success": suspicious_success_events,
    }
    events = scenarios[args.scenario]()
    responses = send_events(args.url, events, args.token)
    alert_ids: set[str] = set()
    for response in responses:
        values = response.get("alert_ids")
        if isinstance(values, list):
            alert_ids.update(str(value) for value in values)
    print(f"Sent {len(responses)} synthetic events; alerts: {len(alert_ids)}")


if __name__ == "__main__":
    main()
