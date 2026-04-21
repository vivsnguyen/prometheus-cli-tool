import yaml

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
# Rule
good_rule = {"alert": "HighErrorRate", "labels": {"severity": "critical"}}
bad_rule = {"alert": "HighErrorRate"}
bare_labels = {"alert": "HighErrorRate", "labels": {}}

# print(is_missing_severity(good_rule))   # should print False
# print(is_missing_severity(bad_rule))    # should print True
# print(is_missing_severity(bare_labels)) # should print True

# # Summary
# good_summary = {"alert": "Test", "annotations": {"summary": "Something is wrong"}}
# no_annotations = {"alert": "Test"}
# bare_annotations = {"alert": "Test", "annotations": {}}

# print(is_missing_summary(good_summary))    # False
# print(is_missing_summary(no_annotations))  # True
# print(is_missing_summary(bare_annotations)) # True

# # Description
# good_description = {"alert": "Test", "annotations": {"description": "This means X is happening"}}
# print(is_missing_description(good_description))  # False
# print(is_missing_description(no_annotations))    # True

# # Runbook
# good_runbook = {"alert": "Test", "annotations": {"runbook_url": "https://runbooks.example.com"}}
# also_good_runbook = {"alert": "Test", "annotations": {"runbook": "https://runbooks.example.com"}}
# print(is_missing_runbook(good_runbook))       # False
# print(is_missing_runbook(also_good_runbook))  # False
# print(is_missing_runbook(no_annotations))     # True

# good_for = {"alert": "Test", "expr": "up == 0", "for": "5m"}
# short_for = {"alert": "Test", "expr": "up == 0", "for": "30s"}
# no_for = {"alert": "Test", "expr": "up == 0"}

# print(is_missing_for_duration(good_for))   # False
# print(is_missing_for_duration(short_for))  # False - it has a 'for', just short
# print(is_missing_for_duration(no_for))     # True

print(analyze_rule(good_rule))
print(analyze_rule(bad_rule))