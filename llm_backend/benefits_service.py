import os

def get_benefits_text():
    """Return the contents of the benefits overview file."""
    benefits_path = os.path.join(os.path.dirname(__file__), '../mock_data/HR/benefits_overview.txt')
    with open(benefits_path, 'r', encoding='utf-8') as f:
        return f.read()