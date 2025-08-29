#!/usr/bin/env python3
"""
Process detainee list and convert to CSV format.
"""

import csv
import sys
from typing import List, Tuple

def parse_detainee_line(line: str) -> Tuple[str, str, str]:
    """
    Parse a detainee line and return (first_name, middle_name, last_name).
    
    The format in the file is:
    - First column: first name
    - Middle columns: middle names (0 or more)
    - Last column: last name
    
    If there's only one name part, it's considered the last name.
    If there are two name parts, they're first and last names.
    If there are three or more, the first is first name, last is last name,
    and everything in between is combined as middle name.
    """
    parts = line.strip().split('\t')
    
    # Remove empty parts
    parts = [part for part in parts if part.strip()]
    
    if not parts:
        return "", "", ""
    
    if len(parts) == 1:
        # Only one name part - treat as last name
        return "", "", parts[0]
    
    elif len(parts) == 2:
        # Two name parts - first and last
        return parts[0], "", parts[1]
    
    else:
        # Three or more name parts
        first_name = parts[0]
        last_name = parts[-1]
        middle_names = parts[1:-1]
        middle_name = " ".join(middle_names) if middle_names else ""
        
        return first_name, middle_name, last_name

def process_detainee_file(input_file: str, output_file: str):
    """
    Process the detainee file and create a CSV.
    """
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        writer = csv.writer(outfile)
        writer.writerow(['first_name', 'middle_name', 'last_name'])  # Header
        
        for line_num, line in enumerate(infile, 1):
            if line.strip():  # Skip empty lines
                try:
                    first, middle, last = parse_detainee_line(line)
                    writer.writerow([first, middle, last])
                except Exception as e:
                    print(f"Error processing line {line_num}: {line.strip()}")
                    print(f"Error: {e}")
                    continue

def main():
    if len(sys.argv) != 3:
        print("Usage: python process_detainees.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Processing {input_file} -> {output_file}")
    process_detainee_file(input_file, output_file)
    print("Processing complete!")

if __name__ == "__main__":
    main()