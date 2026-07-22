"""Alert engine entry point."""
import argparse
import yaml
import logging
from pathlib import Path
from .rules import VolumeSpikeRule
from .notifiers import EmailNotifier, WebhookNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_rules(config_path: Path) -> list:
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    rules = []
    for r in cfg.get("rules", []):
        name = r.get("name", "unnamed")
        # Very simple example: we only support volume spike rule for demo
        if r.get("type") == "volume_spike":
            # Placeholder filter: always True
            def _filter(_):
                return True
            rule = VolumeSpikeRule(
                name=name,
                filter_fn=_filter,
                window_seconds=r.get("window_seconds", 300),
                threshold=r.get("threshold", 10),
                coeoldown_seconds=r.get("cooldown", 600),
            )
            rules.append(rule)
        else:
            logger.warning("Unsupported rule type: %s", r.get("type"))
    return rules


def main() -> None:
    parser = argparse.ArgumentParser(description="Run alert rules on enriched events")
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config/rules.yaml"),
        help="Path to YAML rules configuration",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Directory or file containing enriched events (JSON lines)",
    )
    args = parser.parse_args()

    rules = load_rules(args.config)
    # In a real implementation we would read events from input_data = []
    if args.input.is_dir():
        for p in args.input.rglob("*.jsonl"):
            with p.open() as f:
                for line in f:
                    if line.strip():
                        input_data.append(json.loads(line))
    else:
        with args.input.open() as f:
            for line in f:
                if line.strip():
                    input_data.append(json.loads(line))

    for rule in rules:
        if rule.evaluate(input_data):
            msg = rule.message()
            logger.info("Trigger: %s", msg)
            # For demo, just log; in real system we would call notifiers.
            # Example: notifier.send(msg, to="alerts@example.com")

if __name__ == "__main__":
    main()
