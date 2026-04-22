import yaml
import sys
import re

def get_all_rules(data):
    rules = []
    for group in data["groups"]:
        rules.extend(group["rules"])
    return rules

def print_rule_issues(name, issues):
    print(f"  Rule '{name}':")
    for issue in issues:
        print(f"    - {issue}")

def analyze_file(filepath):
    with open(filepath) as f:
        data = yaml.safe_load(f)

    print(f"\n{filepath}")
    found_issues = False

    all_rules = get_all_rules(data)

    severities_by_alert = {}
    for rule in all_rules:
        name = rule.get("alert")
        severity = rule.get("labels", {}).get("severity")
        if severity:
            severities_by_alert.setdefault(name, []).append(severity)

    for rule in all_rules:
        issues = analyze_rule(rule)
        name = rule.get("alert", "?")
        severities = severities_by_alert.get(name, [])
        if "critical" in severities and not "warning" in severities:
            issues.append("critical alert has no corresponding warning — add a warning-severity alert to give advance notice before paging")
        if issues:
            found_issues = True
            print_rule_issues(name, issues)
    if not found_issues:
        print("  No issues found.")

def is_missing_severity(rule):
    return not "severity" in rule.get("labels", {})

def is_missing_summary(rule):
    return not "summary" in rule.get("annotations", {})

def is_missing_description(rule):
    return not "description" in rule.get("annotations", {})

def is_missing_runbook(rule):
    annotations = rule.get("annotations", {})
    return (not "runbook" in annotations) and (not "runbook_url" in annotations)

def is_missing_for_duration(rule):
    return rule.get("for") is None

def is_for_duration_too_short(rule, min_seconds=300):
    duration = rule.get("for")
    if duration is None:
        return False
    match = re.match(r'^(\d+)(s|m|h)$', str(duration))
    if not match:
        return False
    value, unit = int(match.group(1)), match.group(2)
    seconds = value * {"s": 1, "m": 60, "h": 3600}[unit]
    return seconds < min_seconds

STANDARD_SEVERITIES = {"critical", "warning", "info"}

def is_nonstandard_severity(rule):
    severity = rule.get("labels", {}).get("severity")
    if severity is None:
        return False
    return not severity in STANDARD_SEVERITIES

def has_no_label_selectors(rule):
    expr = rule.get("expr", "")
    if not "{" in expr:
        return True
    if re.search(r'\{\s*\}', expr):
        return True
    return False

def analyze_rule(rule):
    issues = []
    if is_missing_severity(rule):
        issues.append("missing severity label — add labels.severity: critical | warning | info")
    if is_nonstandard_severity(rule):
        issues.append(f"non-standard severity '{rule['labels']['severity']}' — use critical, warning, or info so routing rules match correctly")
    if is_missing_summary(rule):
        issues.append("missing summary annotation — add a one-line description of what the alert means")
    if is_missing_description(rule):
        issues.append("missing description annotation — add context about what's happening and why it matters")
    if is_missing_runbook(rule):
        issues.append("missing runbook — add a runbook_url annotation linking to a response procedure")
    if is_missing_for_duration(rule):
        issues.append("missing for duration — add a 'for' field (e.g. 5m) to avoid firing on transient conditions")
    if is_for_duration_too_short(rule):
        issues.append(f"for duration '{rule['for']}' is too short (< 5m) — increase to at least 5m to avoid paging on transient spikes")
    if has_no_label_selectors(rule):
        issues.append("expr has no label selectors — scope with job, env, or other labels to avoid matching all instances")
    return issues

if len(sys.argv) < 2:
    print("Usage: python3 tool.py <rules_file> [rules_file ...]")
else:
    for filepath in sys.argv[1:]:
        analyze_file(filepath)
