def get_salary_rows(user_role, salaries):
    """
    user_role: str, e.g. 'Alice Johnson (HR)', 'Olivia Zhang (CTO)', 'David Kim (Engineer)'
    salaries: list of (name, title, dept, salary) tuples
    Returns: list of salary tuples the user can see
    """
    if 'HR' in user_role:
        return salaries
    elif 'CTO' in user_role:
        # CTO sees all Technology salaries for 'all' intent, but not for 'my' intent (handled in query_router)
        return [row for row in salaries if row[2].lower() == 'technology']
    else:
        # Engineer or anyone else: only their own salary
        name = user_role.split(' (')[0].strip().lower()
        return [row for row in salaries if row[0].strip().lower() == name]
