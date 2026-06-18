"""CLI for Content Credibility Radar."""

from __future__ import annotations

import argparse
import json

from .radar import analyze_content, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate content claim/source credibility.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("content_json")
    analyze.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    report = analyze_content(load_json(args.content_json))
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
        return

    print("Content Credibility Radar")
    print(f"Score: {report.score}/100")
    print(f"Status: {report.status}")
    print(f"Source types: {', '.join(report.source_types) or 'none'}")
    if report.unsupported_claims:
        print("\nUnsupported claims")
        for claim in report.unsupported_claims:
            print(f"- {claim}")
    if report.emotional_language_flags:
        print("\nEmotional language flags")
        for flag in report.emotional_language_flags:
            print(f"- {flag}")
    print("\nRecommendations")
    for recommendation in report.recommendations:
        print(f"- {recommendation}")


if __name__ == "__main__":
    main()

