# prometheus-cli-tool

A CLI tool that analyzes Prometheus alerting rule files and flags common quality issues and anti-patterns. It accepts one or more YAML rule files and prints a report with problems and suggestions for each.

## Usage

```bash
python3 tool.py <rules_file> [rules_file ...]
```

Example:
```bash
python3 tool.py rules.yml
python3 tool.py staging.yml production.yml
```

## Checks

| Check | Why it matters |
|---|---|
| Missing severity label | Alertmanager routing trees match on severity to decide where to send alerts. Without it, an alert won't match any route and may never reach the on-call engineer |
| Non-standard severity value | Values outside `critical/warning/info` won't match common routing rules, so the alert goes to the wrong receiver or nowhere |
| Missing summary | On-call engineers need a one-line description to triage quickly |
| Missing description | Without context, engineers waste time figuring out what the alert means during an incident |
| Missing runbook | No runbook means no clear response path under pressure |
| Missing `for` duration | Alerts without `for` fire immediately on a single data point, which causes flapping |
| Short `for` duration (< 5m) | Very short windows fire on transient spikes that self-resolve before anyone can act |
| No label selectors in expr | An unscoped metric matches every job and environment, making the alert ambiguous and noisy |
| Critical with no corresponding warning | A critical alert with no warning means the first signal is already an emergency. Engineers should get advance notice before a page |

## Key Decisions and Tradeoffs

**Embedded suggestions vs structured output**

Each issue includes an inline suggestion (e.g. `"missing runbook -- add a runbook_url annotation"`) rather than separating problems and suggestions into structured fields. I considered returning `(problem, suggestion)` tuples from `analyze_rule` to keep data and presentation separate, but because it's a terminal tool and the suggestions are short I thought inline would work. The added structure wouldn't pay off until there's a real need for multiple output formats like JSON or markdown, so I left it simple for now.

**Short `for` threshold of 5 minutes**

The minimum `for` duration is set at 5 minutes, which aligns with what the Prometheus docs and community examples use for typical alerts like high latency or memory pressure. The threshold is a named parameter so it's easy to adjust for alerts that need faster response times.

**Broad selector check**

The selector check flags any `expr` with no `{...}` block, or with an empty `{}`. It checks the expression as a plain string rather than parsing it as PromQL, which keeps the code simple but means it could miss cases like this:

```
rate(http_errors_total[5m]) / rate(http_requests_total{job="api"}[5m])
```

The second metric has `{job="api"}` so the tool sees `{` in the string and doesn't flag it. But the first metric has no label selector at all and would match every job and environment. A proper PromQL parser would catch this, but adding one felt like a lot of complexity for an edge case that's less common than bare metric names with no selectors at all.

**Which checks to leave out**

I skipped "too narrow" selectors (e.g. hardcoded pod names or instance IPs). Detecting over-specification requires knowing what the metric labels look like in practice, and without the metric schema a static check would produce too many false positives. I also didn't try to analyze inhibition rules or full alert dependency graphs since those require reasoning about the entire Alertmanager config, not just the rule files.

**Single-rule vs cross-rule analysis**

Most checks look at one rule at a time and live in `analyze_rule`. The warning/critical relationship check is different because it needs to know whether a `warning` version of an alert exists anywhere in the file before it can flag a `critical`. This required two passes: one to collect all severities by alert name, and a second to run the checks.
