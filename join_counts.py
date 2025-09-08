#!/usr/bin/env python3
"""
Author : Pierre Levy <levy.pierre@yahoo.fr>
Date   : 2024-09-13
Purpose: Join counts from multiple samples into a single table
"""

import sys
import os
import glob
import argparse


def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Join counts from multiple samples into a single table',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dir_counts',
                        metavar='str',
                        help='Path to directory where counts.txt files are located')

    parser.add_argument('ag_lib',
                        metavar='str', 
                        help='Path to Ag library table (TSV format)')

    return parser.parse_args()


def read_ag_lib(ag_lib_path):
    """Read the antigen library file and return list of Ag IDs"""
    ag_ids = []
    try:
        with open(ag_lib_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    ag_id = line.split('\t')[0]
                    ag_ids.append(ag_id)
    except FileNotFoundError:
        print(f"Error: Ag library file '{ag_lib_path}' not found")
        sys.exit(1)
    return ag_ids


def read_counts_file(file_path):
    """Read a counts file and return dictionary of {ag_id: count}"""
    counts = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        ag_id = parts[0]
                        count = int(parts[1])
                        counts[ag_id] = count
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: Error reading {file_path}: {e}")
    return counts


def main():
    """Main function"""
    args = get_args()
    
    # Check if directory exists
    if not os.path.isdir(args.dir_counts):
        print(f"Error: Directory '{args.dir_counts}' not found")
        sys.exit(1)
    
    # Read Ag library
    ag_ids = read_ag_lib(args.ag_lib)
    if not ag_ids:
        print("Error: No Ag IDs found in library file")
        sys.exit(1)
    
    # Find all .counts files in the directory
    counts_pattern = os.path.join(args.dir_counts, "*.counts.txt")
    count_files = glob.glob(counts_pattern)
    
    if not count_files:
        # Try without .txt extension
        counts_pattern = os.path.join(args.dir_counts, "*.counts")
        count_files = glob.glob(counts_pattern)
    
    if not count_files:
        print(f"Error: No .counts or .counts.txt files found in '{args.dir_counts}'")
        sys.exit(1)
    
    print(f"Found {len(count_files)} count files")
    
    # Initialize final counts dictionary
    final_counts = {ag_id: {} for ag_id in ag_ids}
    sample_names = []
    
    # Process each count file
    for file_path in sorted(count_files):
        file_name = os.path.basename(file_path)
        # Extract sample name by removing .counts.txt or .counts extension
        sample_name = file_name.replace('.counts.txt', '').replace('.counts', '')
        sample_names.append(sample_name)
        
        print(f"Processing {file_name} -> {sample_name}")
        
        # Read counts from this file
        file_counts = read_counts_file(file_path)
        
        # Add counts to final table
        for ag_id in ag_ids:
            final_counts[ag_id][sample_name] = file_counts.get(ag_id, 0)
    
    # Write output file
    output_path = os.path.join(args.dir_counts, "all.counts.txt")
    
    with open(output_path, 'w') as f:
        # Write header
        header = ['Ag.ID'] + sample_names
        f.write('\t'.join(header) + '\n')
        
        # Write data
        for ag_id in ag_ids:
            row = [ag_id]
            for sample_name in sample_names:
                count = final_counts[ag_id].get(sample_name, 0)
                row.append(str(count))
            f.write('\t'.join(row) + '\n')
    
    print(f"Output written to: {output_path}")


if __name__ == '__main__':
    main()
