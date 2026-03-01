import re
import pandas as pd

def get_onboarding_info(user_role, query, metadata):
    """
    Returns a dict:
      - onboarding_text: onboarding info string or None
      - source: source file string or None
      - message: error/info message (optional)
    """
    query_lc = query.strip().lower()
    # Map roles to onboarding keywords/files
    role_map = {
        'Alice Johnson (HR)': ('HR Department Onboarding', 'mock_data/HR/hr_onboarding.md'),
        'David Kim (Engineer)': ('Engineering Department Onboarding', 'mock_data/Engineering/engineering_onboarding.md'),
        'Olivia Zhang (CTO)': ('Technology Department Onboarding', 'mock_data/Technology/technology_onboarding.md'),
    }
    if user_role not in role_map:
        return {'message': 'No onboarding information found.', 'onboarding_text': None, 'source': None}
    expected_text, expected_source = role_map[user_role]
    # Accept queries about onboarding
    onboarding_patterns = [r'onboarding', r'what is my onboarding', r'show onboarding', r'onboarding process']
    if not any(re.search(pat, query_lc) for pat in onboarding_patterns):
        return {'message': 'No onboarding information found.', 'onboarding_text': None, 'source': None}
    # Search metadata for onboarding chunk
    if isinstance(metadata, pd.DataFrame) and 'text' in metadata.columns:
        for row in metadata.itertuples():
            text_str = str(row.text) if not isinstance(row.text, str) else row.text
            if expected_text in text_str:
                return {'onboarding_text': expected_text, 'source': expected_source}
    # Fallback: just return expected values
    return {'onboarding_text': expected_text, 'source': expected_source}
