# Content Credibility Radar

Claim and source-quality evaluator for YouTube videos, podcasts, articles, and political/news-style content.

This is not a truth oracle. It is a structured review tool that asks better questions:

- What claims are being made?
- Are sources attached?
- Are sources primary, secondary, or weak?
- Is the language emotionally loaded?
- Does the content need manual fact-checking before sharing?

## Quick Start

```bash
PYTHONPATH=src python3 -m credibility_radar.cli analyze examples/video_claims.json
```

JSON output:

```bash
PYTHONPATH=src python3 -m credibility_radar.cli analyze examples/video_claims.json --format json
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Output

- credibility score
- status: `publishable`, `review`, or `high-risk`
- unsupported claims
- source diversity score
- emotional-language flags
- recommended next fact-checking actions

## Portfolio Signal

This repo supports:

- AI content evaluation
- fake-news review workflows
- source-quality QA
- YouTube transcript analysis
- claim extraction pipelines
- human-in-the-loop fact checking

