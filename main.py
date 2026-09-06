"""Entry point: python main.py [--model MODEL_NAME]"""

import argparse

from cli import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DND Lite -- a text-based AI Dungeon Master.")
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Ollama model to use for this run. Overrides the DND_LITE_MODEL "
            "environment variable and the built-in default (see "
            "ollama_client.py)."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(model=args.model)
