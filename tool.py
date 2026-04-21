import yaml
import sys

def analyze_file(filepath):
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    for group in data["groups"]:
        for rule in group["rules"]:
            issues = analyze_rule(rule)
            if issues:
                print(f"Rule '{rule.get('alert', '?')}': {', '.join(issues)}")

# with open("test.yml") as f:
#     data = yaml.safe_load(f)

# print(data)

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

def analyze_rule(rule):
    issues = []
    if is_missing_severity(rule):
        issues.append("missing severity label")
    if is_missing_summary(rule):
        issues.append("missing summary annotation")
    if is_missing_description(rule):
        issues.append("missing description")
    if is_missing_for_duration(rule):
        issues.append("missing for duration")
    return issues


analyze_file("test_rules.yml")