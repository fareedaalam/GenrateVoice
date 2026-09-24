#!/usr/bin/env python3
"""CLI for cloning a voice with XTTS-v2.

Example:
    python examples/voice_cloning/clone_voice.py \\
        --text "Hello, this is a cloned voice." \\
        --speaker-wav my_reference.wav \\
        --language en \\
        --output examples/voice_cloning/output/cloned.wav

Only clone voices you own or have explicit consent to clone.
"""

import argparse
import sys
from pathlib import Path

from voice_cloner import SUPPORTED_LANGUAGES, VoiceCloner

DEFAULT_OUTPUT = Path(__file__).parent / "output" / "cloned.wav"


def parse_args():
    parser = argparse.ArgumentParser(description="Clone a voice with XTTS-v2.")
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", type=str, help="Text to synthesize.")
    text_group.add_argument("--text-file", type=str, help="Path to a file containing the text to synthesize.")

    parser.add_argument(
        "--speaker-wav", type=str, nargs="+", required=True,
        help="One or more reference audio files of the target voice.",
    )
    parser.add_argument(
        "--language", type=str, default="en",
        choices=SUPPORTED_LANGUAGES, help="Language of the text (default: en).",
    )
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Output wav path.")
    parser.add_argument("--device", type=str, default=None, help="Force device, e.g. 'cuda' or 'cpu'.")
    return parser.parse_args()


def main():
    args = parse_args()

    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")

    print(
        "Reminder: only clone voices you own or have explicit consent to clone. "
        "Do not use this for impersonation, fraud, or deception.",
        file=sys.stderr,
    )

    cloner = VoiceCloner(device=args.device)
    output_path = cloner.clone(
        text=text,
        speaker_wav=args.speaker_wav,
        output_path=args.output,
        language=args.language,
    )
    print(f"Saved cloned voice to: {output_path}")


if __name__ == "__main__":
    main()
