"""CLI for Content Credibility Radar."""

from __future__ import annotations

import argparse
import json

from .llm import LLMConfigurationError, LLMRequestError, generate_text
from .radar import analyze_content, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate content claim/source credibility.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("content_json")
    analyze.add_argument("--format", choices=["text", "json"], default="text")
    analyze.add_argument("--llm", action="store_true", help="Add optional Kimi/ZenMux editorial review.")
    args = parser.parse_args()

    payload = load_json(args.content_json)
    report = analyze_content(payload)
    llm_analysis = _optional_llm_analysis(args.llm, payload, report)
    if args.format == "json":
        output = report.to_dict()
        if llm_analysis:
            output["llm_analysis"] = llm_analysis
        print(json.dumps(output, indent=2))
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
    if llm_analysis:
        print("\nKimi Editorial Review")
        print(llm_analysis)


def _optional_llm_analysis(enabled: bool, payload: dict[str, object], report: object) -> str | None:
    if not enabled:
        return None
    payload_for_prompt = dict(payload)
    transcript = str(payload_for_prompt.get("transcript", ""))
    payload_for_prompt["transcript"] = transcript[:1500]
    prompt = (
        "Review this credibility report as a human-in-the-loop editorial QA assistant. "
        "Do not claim something is true without sources; focus on verification workflow.\n\n"
        f"CONTENT PAYLOAD:\n{json.dumps(payload_for_prompt, indent=2)}\n\n"
        f"DETERMINISTIC REPORT:\n{json.dumps(report.to_dict(), indent=2)}\n\n"
        "Return: 1) risk summary, 2) source gaps, 3) neutral rewrite guidance, "
        "4) search queries for manual verification, 5) publish/no-publish recommendation. "
        "Keep the full answer under 350 words with compact bullets."
    )
    try:
        return generate_text(
            prompt,
            system="You are a fact-checking workflow analyst, not a truth oracle.",
            max_tokens=6000,
        )
    except (LLMConfigurationError, LLMRequestError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
