import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load chunked documents

# Special handling: if payroll_confidential.txt is present, split into one row per employee
doc_chunks_path = os.path.join(os.path.dirname(__file__), 'document_chunks.csv')
df = pd.read_csv(doc_chunks_path)

# Patch department/sensitivity for onboarding files
onboarding_files = [
    ('hr_onboarding.md', 'HR', 'internal'),
    ('technology_onboarding.md', 'Technology', 'confidential')
]
for fname, dept, sens in onboarding_files:
	idx = df['file'].astype(str).str.lower().str.contains(fname)
	if idx.any():
		df.loc[idx, 'department'] = dept
		df.loc[idx, 'sensitivity'] = sens
		# Optionally set version
		df.loc[idx, 'version'] = 1.0

payroll_idx = df['file'].astype(str).str.contains('payroll_confidential.txt', case=False, na=False)
if payroll_idx.any():
	payroll_row = df[payroll_idx].iloc[0]
	payroll_text = payroll_row['text']
	# If the chunked text is missing salary lines, read the file directly
	if not isinstance(payroll_text, str) or 'Name:' not in payroll_text:
		payroll_file_path = os.path.join(os.path.dirname(__file__), 'payroll_confidential.txt')
		if os.path.exists(payroll_file_path):
			with open(payroll_file_path, 'r', encoding='utf-8') as f:
				payroll_text = f.read()
	# Robustly split salary block into one row per employee
	import re
	# Split on 'Name:' and reconstruct each line
	split_lines = re.split(r'(Name:)', payroll_text)
	employee_lines = []
	for i in range(1, len(split_lines), 2):
		line = split_lines[i] + split_lines[i+1] if (i+1) < len(split_lines) else split_lines[i]
		# Only keep lines that look like salary records
		if re.search(r'\$[\d,]+', line):
			employee_lines.append(line.strip())
	# Create a new DataFrame for each employee
	payroll_rows = []
	for line in employee_lines:
		new_row = payroll_row.copy()
		new_row['text'] = line
		payroll_rows.append(new_row)
	# Remove the original payroll row and add the new ones
	df = df[~payroll_idx]
	df = pd.concat([df, pd.DataFrame(payroll_rows)], ignore_index=True)
	payroll_debug = df[df['file'].astype(str).str.contains('payroll_confidential.txt', case=False, na=False)][['file','text']]
	print('DEBUG: payroll_confidential.txt rows after split:')
	print(payroll_debug.to_string(index=False))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
embeddings = np.array(embeddings).astype('float32')


# Create FAISS index
if not isinstance(embeddings, np.ndarray):
    embeddings = np.array(embeddings).astype('float32')
if embeddings.ndim == 1:
    embeddings = embeddings.reshape(1, -1)
index = faiss.IndexFlatL2(embeddings.shape[1])
# Ensure embeddings is contiguous float32 (n, d)
if not embeddings.flags['C_CONTIGUOUS']:
	embeddings = np.ascontiguousarray(embeddings, dtype='float32')
if embeddings.ndim != 2:
	raise ValueError(f"Embeddings must be 2D (n, d), got shape {embeddings.shape}")
print(f"DEBUG: embeddings type={type(embeddings)}, shape={embeddings.shape}, dtype={embeddings.dtype}")
index.add(embeddings)

# Save index and metadata

# Save index and metadata (overwrite old metadata)
data_dir = os.path.join(os.path.dirname(__file__), '../vector_db')
faiss.write_index(index, os.path.join(data_dir, 'faiss_index.bin'))
# Save metadata DataFrame to CSV
meta_path = os.path.join(data_dir, 'metadata.csv')
df.to_csv(meta_path, index=False)

print(f"Stored {len(df)} embeddings in FAISS index at {data_dir}.")
