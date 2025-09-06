#!/usr/bin/env python3
"""
Simple script to extract Hispanic/Latino names and surnames.
"""

import csv

# Hispanic/Latino country codes
HISPANIC_COUNTRIES = {'ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 
                      'HN', 'PY', 'SV', 'NI', 'CR', 'PR', 'UY', 'PA', 'GQ'}

def main():
    # Extract first names
    first_names = set()
    with open('common-forenames-by-country.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country_key = 'Country' if 'Country' in row else '\ufeffCountry'
            if row[country_key] in HISPANIC_COUNTRIES:
                if row['Localized Name']:
                    first_names.add(row['Localized Name'].strip())
                if row['Romanized Name']:
                    first_names.add(row['Romanized Name'].strip())
    
    # Extract surnames
    surnames = set()
    with open('common-surnames-by-country.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country_key = 'Country' if 'Country' in row else '\ufeffCountry'
            if row[country_key] in HISPANIC_COUNTRIES:
                if row['Localized Name']:
                    surnames.add(row['Localized Name'].strip())
                if row['Romanized Name']:
                    surnames.add(row['Romanized Name'].strip())
    
    # Save first names
    with open('organized/hispanic_first_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic/Latino First Names\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        for name in sorted(first_names):
            f.write(f"{name}\n")
    
    # Save surnames
    with open('organized/hispanic_surnames.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic/Latino Surnames\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        for name in sorted(surnames):
            f.write(f"{name}\n")
    
    # Save sample full names
    with open('organized/hispanic_full_names_sample.txt', 'w', encoding='utf-8') as f:
        f.write("# Sample Hispanic/Latino Full Names\n")
        f.write("# (First Name + Surname)\n")
        f.write("# Extracted from popular-names-by-country-dataset\n\n")
        names_list = list(first_names)[:50]
        surnames_list = list(surnames)[:30]
        for first_name in names_list:
            for surname in surnames_list:
                f.write(f"{first_name} {surname}\n")
    
    print(f"Extracted {len(first_names)} unique first names")
    print(f"Extracted {len(surnames)} unique surnames")
    print("Files saved to hispanic_names_data/organized/")

if __name__ == "__main__":
    main()