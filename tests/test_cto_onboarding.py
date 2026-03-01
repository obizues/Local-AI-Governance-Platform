
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import streamlit
import pandas as pd
from llm_backend.onboarding_service import get_onboarding_info

# Mock CTO role and onboarding query
def test_cto_onboarding_returns_technology_chunk():
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    retrieved_chunks = pd.DataFrame(columns=['file', 'text'])
    result = get_onboarding_info('Olivia Zhang (CTO)', query, retrieved_chunks)
    assert 'Technology Department Onboarding' in result['onboarding_text']
    assert 'mock_data/Technology/technology_onboarding.md' in result['source']

# Mock DataFrame with technology onboarding chunk
def test_cto_onboarding_returns_chunk_from_dataframe():
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    retrieved_chunks = pd.DataFrame([
        {'file': 'mock_data/Technology/technology_onboarding.md', 'text': 'Technology Department Onboarding\n1. Complete your technical setup.'}
    ])
    result = get_onboarding_info('Olivia Zhang (CTO)', query, retrieved_chunks)
    assert 'Technology Department Onboarding' in result['onboarding_text']
    assert 'mock_data/Technology/technology_onboarding.md' in result['source']

# Ensure fallback returns error if file missing
def test_cto_onboarding_fallback_file_missing():
    streamlit.session_state['user_role'] = 'Olivia Zhang (CTO)'
    query = "What's the onboarding process?"
    retrieved_chunks = pd.DataFrame(columns=['file', 'text'])
    # Simulate missing role
    result = get_onboarding_info('Unknown User', query, retrieved_chunks)
    assert 'No onboarding information found.' in result['message']
