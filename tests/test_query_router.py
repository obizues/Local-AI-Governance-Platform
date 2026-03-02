import pytest
import pandas as pd
from llm_backend import query_router
import os
import re
import builtins

def make_metadata(salaries):
    # salaries: list of (name, title, dept, salary)
    rows = []
    for name, title, dept, salary in salaries:
        text = f"Name: {name} | Department: {dept}"
        if title:
            text += f" | Title: {title}"
        text += f" | Salary: ${salary}"
        rows.append({'text': text})
    return pd.DataFrame(rows)

def test_salary_intent_my_vs_all():
    assert query_router.detect_salary_intent("show my salary") == 'my'
    assert query_router.detect_salary_intent("what is my salary?") == 'my'
    assert query_router.detect_salary_intent("show all salaries") == 'all'
    assert query_router.detect_salary_intent("everyone's salary") == 'all'
    assert query_router.detect_salary_intent("salary") is None

def test_department_mapping():
    assert query_router.get_department_from_role("Alice Johnson (CPO)") == 'HR'
    assert query_router.get_department_from_role("David Kim (Engineer)") == 'Technology'
    assert query_router.get_department_from_role("Olivia Zhang (CTO)") == 'Technology'
    assert query_router.get_department_from_role("Bob Smith (HR)") == 'HR'
    assert query_router.get_department_from_role("Random User") is None

def test_route_query_salary_hr_all():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
    ]
    metadata = make_metadata(salaries)
    # HR user, all salaries
    resp, _ = query_router.route_query("show all salaries", "Alice Johnson (CPO)", metadata)
    assert "Alice Johnson" in resp and "Bob Smith" in resp and "David Kim" in resp

def test_route_query_salary_hr_my():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
    ]
    metadata = make_metadata(salaries)
    # HR user, my salary
    resp, _ = query_router.route_query("show my salary", "Alice Johnson (CPO)", metadata)
    assert "Alice Johnson" in resp and "Bob Smith" not in resp and "David Kim" not in resp

def test_route_query_onboarding_hr():
    # Should return HR onboarding for Alice Johnson
    resp, _ = query_router.route_query("show onboarding", "Alice Johnson (CPO)", pd.DataFrame())
    assert "HR Department Onboarding" in resp

def test_route_query_onboarding_technology():
    # Should return Technology onboarding for David Kim
    resp, _ = query_router.route_query("show onboarding", "David Kim (Engineer)", pd.DataFrame())
    assert "Technology Department Onboarding" in resp

def test_route_query_onboarding_cto():
    # Should return Technology onboarding for Olivia Zhang (CTO)
    resp, _ = query_router.route_query("show onboarding", "Olivia Zhang (CTO)", pd.DataFrame())
    assert "Technology Department Onboarding" in resp

def test_route_query_salary_cto_all():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
        ("Olivia Zhang", "CTO", "Technology", "250,000"),
    ]
    metadata = make_metadata(salaries)
    # CTO user, all salaries (should see all Technology, not HR)
    resp, _ = query_router.route_query("show all salaries", "Olivia Zhang (CTO)", metadata)
    assert "Olivia Zhang" in resp and "David Kim" in resp
    assert "Alice Johnson" not in resp and "Bob Smith" not in resp

def test_route_query_salary_cto_my():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
        ("Olivia Zhang", "CTO", "Technology", "250,000"),
    ]
    metadata = make_metadata(salaries)
    # CTO user, my salary (should see only own)
    resp, _ = query_router.route_query("show my salary", "Olivia Zhang (CTO)", metadata)
    assert "Olivia Zhang" in resp and "David Kim" not in resp and "Alice Johnson" not in resp and "Bob Smith" not in resp

def test_route_query_salary_engineer_my():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
        ("Olivia Zhang", "CTO", "Technology", "250,000"),
    ]
    metadata = make_metadata(salaries)
    # Engineer user, my salary (should see only own)
    resp, _ = query_router.route_query("show my salary", "David Kim (Engineer)", metadata)
    assert "David Kim" in resp and "Olivia Zhang" not in resp and "Alice Johnson" not in resp and "Bob Smith" not in resp

def test_route_query_salary_engineer_all():
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
        ("Olivia Zhang", "CTO", "Technology", "250,000"),
    ]
    metadata = make_metadata(salaries)
    # Engineer user, all salaries (should be denied)
    resp, _ = query_router.route_query("show all salaries", "David Kim (Engineer)", metadata)
    assert "You do not have access" in resp

def read_last_audit_log():
    log_path = os.path.join(os.path.dirname(__file__), '../access_audit.log')
    if not os.path.exists(log_path):
        return ''
    with open(log_path, 'r', encoding='utf-8') as f:
        return f.read()

def clear_audit_log():
    log_path = os.path.join(os.path.dirname(__file__), '../access_audit.log')
    if os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('')

def test_salary_access_denied_logging(tmp_path, monkeypatch):
    import builtins
    test_log = tmp_path / "access_audit.log"
    test_log.write_text("")  # Ensure the file exists
    monkeypatch.setenv('ACCESS_AUDIT_LOG', str(test_log))
    monkeypatch.setattr(builtins, 'open', builtins.open)
    salaries = [
        ("Alice Johnson", "CPO", "HR", "112,000"),
        ("Bob Smith", "", "HR", "98,500"),
        ("David Kim", "Engineer", "Technology", "185,200"),
        ("Olivia Zhang", "CTO", "Technology", "250,000"),
    ]
    metadata = make_metadata(salaries)
    # Engineer tries to see all salaries (should be denied)
    resp, _ = query_router.route_query("show all salaries", "David Kim (Engineer)", metadata)
    assert "You do not have access" in resp
    log_contents = test_log.read_text()
    assert "David Kim (Engineer)" in log_contents and "show all salaries" in log_contents
    # Engineer tries to see HR salary (should be denied)
    resp, _ = query_router.route_query("show salary for Alice Johnson", "David Kim (Engineer)", metadata)
    assert "You do not have access" in resp
    log_contents = test_log.read_text()
    assert "David Kim (Engineer)" in log_contents and "Alice Johnson" in log_contents
    # HR can see all, should not be denied
    resp, _ = query_router.route_query("show all salaries", "Alice Johnson (CPO)", metadata)
    assert "You do not have access" not in resp
    # CTO asks for HR salary (should be denied)
    resp, _ = query_router.route_query("show salary for Alice Johnson", "Olivia Zhang (CTO)", metadata)
    assert "You do not have access" in resp
    log_contents = test_log.read_text()
    assert "Olivia Zhang (CTO)" in log_contents and "Alice Johnson" in log_contents

def test_deploy_sop_engineer_access():
    # Engineer should get actual SOP content from the real file
    resp, _ = query_router.route_query("how to deploy software", "David Kim (Engineer)", pd.DataFrame())
    assert "Deploying New Software Build" in resp or "deploy" in resp.lower()

def test_deploy_sop_cto_denied(tmp_path, monkeypatch):
    import builtins
    test_log = tmp_path / "access_audit.log"
    sop_path = tmp_path / "deploy_software_sop.md"
    sop_path.write_text("Step 1: Do X\nStep 2: Do Y")
    test_log.write_text("")  # Ensure the file exists
    monkeypatch.setenv('ACCESS_AUDIT_LOG', str(test_log))
    orig_join = os.path.join
    def join_patch(*a):
        joined = orig_join(*a)
        # Only patch the SOP file path, not the audit log
        if str(sop_path) in joined or 'deploy_software_sop.md' in joined:
            return str(sop_path)
        return joined
    monkeypatch.setattr('os.path.join', join_patch)
    # CTO should be denied
    resp, _ = query_router.route_query("how to deploy software", "Olivia Zhang (CTO)", pd.DataFrame())
    assert "You do not have a need to access this" in resp
    log_contents = test_log.read_text()
    assert "Olivia Zhang (CTO)" in log_contents and "how to deploy software" in log_contents

def test_deploy_sop_hr_denied(tmp_path, monkeypatch):
    import builtins
    test_log = tmp_path / "access_audit.log"
    sop_path = tmp_path / "deploy_software_sop.md"
    sop_path.write_text("Step 1: Do X\nStep 2: Do Y")
    test_log.write_text("")  # Ensure the file exists
    monkeypatch.setenv('ACCESS_AUDIT_LOG', str(test_log))
    orig_join = os.path.join
    def join_patch(*a):
        joined = orig_join(*a)
        # Only patch the SOP file path, not the audit log
        if str(sop_path) in joined or 'deploy_software_sop.md' in joined:
            return str(sop_path)
        return joined
    monkeypatch.setattr('os.path.join', join_patch)
    # HR should be denied
    resp, _ = query_router.route_query("how to deploy software", "Alice Johnson (CPO)", pd.DataFrame())
    assert "You do not have a need to access this" in resp
    log_contents = test_log.read_text()
    assert "Alice Johnson (CPO)" in log_contents and "how to deploy software" in log_contents