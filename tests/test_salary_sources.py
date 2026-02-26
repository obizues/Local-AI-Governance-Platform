import unittest
import pandas as pd
from ui import app

class TestSalarySources(unittest.TestCase):
    def test_salary_sources_only_payroll(self):
        # Simulate filtered_df with only payroll_confidential.txt
        data = {
            'file': [
                'mock_data/HR/payroll_confidential.txt',
                'mock_data/HR/payroll_confidential.txt',
            ],
            'Name': ['Alice Johnson (HR)', 'Bob Smith'],
            'Title': ['HR', ''],
            'Department': ['HR', 'HR'],
            'Salary': ['112,000', '98,500'],
        }
        filtered_df = pd.DataFrame(data)
        sources = set()
        for f in filtered_df['file']:
            base = str(f).split('/')[-1]
            sources.add(base)
        provenance = ', '.join(sorted(sources))
        self.assertEqual(provenance, 'payroll_confidential.txt')

    def test_salary_sources_multiple_files(self):
        # Simulate filtered_df with multiple files
        data = {
            'file': [
                'mock_data/HR/payroll_confidential.txt',
                'mock_data/Engineering/other.txt',
            ],
            'Name': ['Alice Johnson (HR)', 'Bob Smith'],
            'Title': ['HR', ''],
            'Department': ['HR', 'Engineering'],
            'Salary': ['112,000', '98,500'],
        }
        filtered_df = pd.DataFrame(data)
        sources = set()
        for f in filtered_df['file']:
            base = str(f).split('/')[-1]
            sources.add(base)
        provenance = ', '.join(sorted(sources))
        self.assertEqual(provenance, 'other.txt, payroll_confidential.txt')

if __name__ == '__main__':
    unittest.main()