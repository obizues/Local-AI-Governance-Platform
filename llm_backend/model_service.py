import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import streamlit as st

@st.cache_resource(show_spinner=True)
def load_embed_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource(show_spinner=True)
def load_llm_pipeline(gen_model_name):
    if gen_model_name == 'ollama':
        return None, 'Ollama'
    else:
        llm = pipeline('text-generation', model=gen_model_name, device=-1, max_new_tokens=256)
        return llm, gen_model_name.upper()

# Data loading helpers
@st.cache_resource(show_spinner=True)
def load_faiss_index(index_path):
    return faiss.read_index(index_path)

@st.cache_resource(show_spinner=True)
def load_metadata(metadata_path):
    return pd.read_csv(metadata_path)

def extract_salaries_from_metadata(metadata_df):
    """
    Extract salary tuples (name, title, dept, salary) from a DataFrame with a 'text' column.
    Returns a list of tuples: (name, title, dept, salary)
    """
    salaries = []
    if isinstance(metadata_df, pd.DataFrame) and 'text' in metadata_df.columns:
        for row in metadata_df.itertuples():
            text_str = str(row.text) if not isinstance(row.text, str) else row.text
            import re
            match = re.search(r'Name:\s*([^|]+)\s*\|\s*Department:\s*([^|]+)(?:\s*\|\s*Title:\s*([^|]+))?\s*\|\s*Salary:\s*\$([\d,]+)', text_str)
            if match:
                name = match.group(1).strip()
                dept = match.group(2).strip()
                title = match.group(3).strip() if match.group(3) else ''
                salary = match.group(4).strip()
                salaries.append((name, title, dept, salary))
    return salaries