#!/usr/bin/env python3
"""
Generate comprehensive list of all possible Hispanic full name combinations.
"""

import csv
import random
from datetime import datetime

def load_names_from_file(filename):
    """Load names from a text file, skipping comments and empty lines."""
    names = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    names.append(line)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return names

def load_names_from_csv(filename):
    """Load names from CSV file."""
    names = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'name' in row:
                    names.append(row['name'])
                elif 'surname' in row:
                    names.append(row['surname'])
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return names

def generate_comprehensive_names():
    """Generate comprehensive list of Hispanic full names."""
    print("Generating comprehensive Hispanic full names...")
    
    # Load first names from multiple sources
    first_names = []
    
    # From our text file
    first_names.extend(load_names_from_file('common_hispanic_first_names.txt'))
    
    # From our CSV file
    first_names.extend(load_names_from_csv('common_hispanic_first_names.csv'))
    
    # Remove duplicates and sort
    first_names = sorted(list(set(first_names)))
    
    # Load last names from multiple sources
    last_names = []
    
    # From our text file
    last_names.extend(load_names_from_file('common_hispanic_last_names.txt'))
    
    # From our CSV file
    last_names.extend(load_names_from_csv('common_hispanic_last_names.csv'))
    
    # Remove duplicates and sort
    last_names = sorted(list(set(last_names)))
    
    print(f"Found {len(first_names)} unique first names")
    print(f"Found {len(last_names)} unique last names")
    print(f"Total possible combinations: {len(first_names) * len(last_names):,}")
    
    # Generate all combinations
    full_names = []
    for first_name in first_names:
        for last_name in last_names:
            full_names.append(f"{first_name} {last_name}")
    
    print(f"Generated {len(full_names):,} full name combinations")
    
    return full_names, first_names, last_names

def save_comprehensive_list(full_names, first_names, last_names):
    """Save the comprehensive list to files."""
    
    # Save all full names to a text file
    with open('comprehensive_hispanic_full_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Hispanic Full Names\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n")
        f.write(f"# Total combinations: {len(full_names):,}\n")
        f.write(f"# First names: {len(first_names)}\n")
        f.write(f"# Last names: {len(last_names)}\n")
        f.write("#\n")
        f.write("# All possible combinations of Hispanic first and last names\n")
        f.write("# Perfect for comprehensive MCP testing\n")
        f.write("#\n\n")
        
        for i, name in enumerate(full_names, 1):
            f.write(f"{name}\n")
    
    # Save a sample of 1000 names for quick testing
    sample_names = random.sample(full_names, min(1000, len(full_names)))
    with open('hispanic_names_sample_1000.txt', 'w', encoding='utf-8') as f:
        f.write("# Sample of 1000 Hispanic Full Names for Testing\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n")
        f.write("# Random sample from comprehensive list\n")
        f.write("#\n\n")
        
        for name in sample_names:
            f.write(f"{name}\n")
    
    # Save first names list
    with open('comprehensive_hispanic_first_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Hispanic First Names\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n")
        f.write(f"# Total first names: {len(first_names)}\n")
        f.write("#\n\n")
        
        for name in first_names:
            f.write(f"{name}\n")
    
    # Save last names list
    with open('comprehensive_hispanic_last_names.txt', 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Hispanic Last Names\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n")
        f.write(f"# Total last names: {len(last_names)}\n")
        f.write("#\n\n")
        
        for name in last_names:
            f.write(f"{name}\n")
    
    # Save statistics
    with open('hispanic_names_statistics.txt', 'w', encoding='utf-8') as f:
        f.write("# Hispanic Names Statistics\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n")
        f.write("#\n")
        f.write(f"Total first names: {len(first_names)}\n")
        f.write(f"Total last names: {len(last_names)}\n")
        f.write(f"Total full name combinations: {len(full_names):,}\n")
        f.write(f"Sample size (1000): {min(1000, len(full_names))}\n")
        f.write("#\n")
        f.write("Files generated:\n")
        f.write("- comprehensive_hispanic_full_names.txt (all combinations)\n")
        f.write("- hispanic_names_sample_1000.txt (1000 random samples)\n")
        f.write("- comprehensive_hispanic_first_names.txt (all first names)\n")
        f.write("- comprehensive_hispanic_last_names.txt (all last names)\n")
        f.write("- hispanic_names_statistics.txt (this file)\n")

def main():
    """Main function to generate comprehensive Hispanic names."""
    print("=== Comprehensive Hispanic Names Generator ===")
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Generate all combinations
    full_names, first_names, last_names = generate_comprehensive_names()
    
    # Save to files
    print("\nSaving comprehensive lists...")
    save_comprehensive_list(full_names, first_names, last_names)
    
    print(f"\n✅ Generation complete!")
    print(f"📊 Generated {len(full_names):,} full name combinations")
    print(f"📁 Files created:")
    print(f"   - comprehensive_hispanic_full_names.txt")
    print(f"   - hispanic_names_sample_1000.txt")
    print(f"   - comprehensive_hispanic_first_names.txt")
    print(f"   - comprehensive_hispanic_last_names.txt")
    print(f"   - hispanic_names_statistics.txt")
    
    print(f"\n🎯 Ready for comprehensive MCP testing!")

if __name__ == "__main__":
    main()

