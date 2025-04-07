#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import csv

def check_seqtk(seqtk_path):
    """Check if seqtk exists at the specified path and is executable."""
    if os.path.isfile(seqtk_path) and os.access(seqtk_path, os.X_OK):
        print(f"seqtk found at {seqtk_path}.")
    else:
        print(f"seqtk not found at {seqtk_path}. Installing...")
        install_seqtk()

def install_seqtk():
    """Install seqtk if it does not exist."""
    subprocess.check_call(['git', 'clone', 'https://github.com/lh3/seqtk.git'])
    os.chdir('seqtk')
    subprocess.check_call(['make'])
    print("seqtk installed successfully.")

def parse_arguments():
    """Parse command line arguments."""
    if len(sys.argv) < 5:
        print("Usage: script.py <gene_content_tab.txt_path> <faa.all_path> <cluster_numbers_file> <output_path> [seqtk_path]")
        sys.exit(1)
    
    gene_content_tab_path = sys.argv[1]
    faa_all_path = sys.argv[2]
    cluster_numbers_file = sys.argv[3]
    output_path = sys.argv[4]
    
    seqtk_path = sys.argv[5] if len(sys.argv) > 5 else 'seqtk'  # Default to 'seqtk' if not specified
    
    return gene_content_tab_path, faa_all_path, cluster_numbers_file, output_path, seqtk_path

def read_cluster_numbers(cluster_numbers_file):
    """Read cluster numbers from a file."""
    with open(cluster_numbers_file, 'r') as f:
        cluster_numbers = [int(line.strip()) for line in f if line.strip().isdigit()]
    return cluster_numbers

def process_gene_content_tab(gene_content_tab_path, faa_all_path, cluster_numbers, output_path, seqtk_path):
    """Process the gene content tab file."""
    with open(gene_content_tab_path, newline='') as file:
        tabl2 = list(csv.reader(file, delimiter="\t"))  # Clusters with locus tags

    for row in tabl2:
        cluster_id = int(row[0])
        if cluster_id not in cluster_numbers:
            continue
        
        # Write list of gene IDs to a temporary file
        list_file_path = os.path.join(output_path, 'list.txt')
        with open(list_file_path, 'w') as list_file:
            for gene in row[1:]:
                list_file.write(f"{gene}\n")
        
        # Run seqtk command
        output_faa = os.path.join(output_path, f"{cluster_id}.faa")
        seqtk_command = f"{seqtk_path} subseq {faa_all_path} {list_file_path} > {output_faa}"
        os.system(seqtk_command)
        
        # Clean up the temporary list file
        os.remove(list_file_path)
        print(f"Output written to: {output_faa}")

def main():
    gene_content_tab_path, faa_all_path, cluster_numbers_file, output_path, seqtk_path = parse_arguments()
    check_seqtk(seqtk_path)  # Check if seqtk is available or install it
    cluster_numbers = read_cluster_numbers(cluster_numbers_file)
    process_gene_content_tab(gene_content_tab_path, faa_all_path, cluster_numbers, output_path, seqtk_path)

if __name__ == "__main__":
    main()
