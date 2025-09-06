#!/usr/bin/env python3
"""
Script to extract Hispanic/Latino names and surnames from the popular names dataset
and organize them into readable formats.
"""

import csv
import os

# Hispanic/Latino country codes
HISPANIC_COUNTRIES = {
    'ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 
    'HN', 'PY', 'SV', 'NI', 'CR', 'PR', 'UY', 'PA', 'GQ'
}

def extract_hispanic_names():
    """Extract Hispanic/Latino names from the dataset."""
    
    # Extract first names
    first_names = set()
    with open('common-forenames-by-country.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        print('First names file headers:', reader.fieldnames)
        for row in reader:
            country_key = 'Country' if 'Country' in row else '\ufeffCountry'
            if row[country_key] in HISPANIC_COUNTRIES:
                # Add both localized and romanized names
                if row['Localized Name']:
                    first_names.add(row['Localized Name'].strip())
                if row['Romanized Name']:
                    first_names.add(row['Romanized Name'].strip())
    
    # Extract surnames
    surnames = set()
    with open('common-surnames-by-country.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        print('Surnames file headers:', reader.fieldnames)
        for row in reader:
            country_key = 'Country' if 'Country' in row else '\ufeffCountry'
            if row[country_key] in HISPANIC_COUNTRIES:
                # Add both localized and romanized names
                if row['Localized Name']:
                    surnames.add(row['Localized Name'].strip())
                if row['Romanized Name']:
                    surnames.add(row['Romanized Name'].strip())
    
    # Write first names to file
    with open('organized/hispanic_first_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic/Latino First Names\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        for name in sorted(first_names):
            f.write(f"{name}\n")
    
    # Write surnames to file
    with open('organized/hispanic_surnames.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic/Latino Surnames\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        for name in sorted(surnames):
            f.write(f"{name}\n")
    
    # Write combined file with full names
    with open('organized/hispanic_full_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic/Latino Full Names (First Name + Surname)\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        for first_name in sorted(first_names)[:100]:  # Limit for readability
            for surname in sorted(surnames)[:50]:  # Limit for readability
                f.write(f"{first_name} {surname}\n")
    
    print(f"Extracted {len(first_names)} unique first names")
    print(f"Extracted {len(surnames)} unique surnames")
    print("Files saved to hispanic_names_data/organized/")

if __name__ == "__main__":
    extract_hispanic_names()