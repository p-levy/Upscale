#!/usr/bin/env python3
"""
Author : Pierre Levy <levy.pierre@yahoo.fr>
Date   : 2024-09-13
Purpose: Bowtie2 indexing for Ag lib
"""

import argparse
import subprocess
import os
import sys
import logging

# --------------------------------------------------


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Ag library screen processing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('lib',
                        metavar='str',
                        help='fasta file containing library ag sequences')
    
    parser.add_argument('-l',
                        '--log',
                        help='Name of the log file',
                        metavar='\b',
                        type=str,
                        default='log.txt')

    return parser.parse_args()

    # --------------------------------------------------


def exec_command(cmd):
    logger = logging.getLogger()
    logger.info(f'{cmd}\n')
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, executable='/bin/bash')
    output, error = p.communicate()
    if p.returncode != 0:
        for line in output.decode("utf-8").split("\n") if output else "":
            logger.error(line.rstrip())
        for line in error.decode("utf-8").split("\n") if error else "":
            logger.error(line.rstrip())
        sys.exit()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    lib = os.path.abspath(args.lib)
    log = args.log
    
    # create output directory out and set as current wd
    if not os.path.exists(f'{os.path.dirname(lib)}/bowtie2_indices'):
        os.mkdir(f'{os.path.dirname(lib)}/bowtie2_indices') # create dir
    
    # Create log file
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG,
                        handlers=[
                        logging.FileHandler(f'{os.path.dirname(lib)}/bowtie2_indices/indexing_{log}'),
                        logging.StreamHandler() # these 2 handlers allow 1) to have the log file created and 2) to stream to the terminal
                        ])

    logger = logging.getLogger() # creates logger to add entries to the log

    # bowtie2 indexing (if not done before)
    if not os.path.exists(f"{os.path.dirname(lib)}/bowtie2_indices/aglib.1.bt2"):
        logger.info("****** Bowtie2: library fasta indexing ******\n\n")
        cmd = f"bowtie2-build {lib} {os.path.dirname(lib)}/bowtie2_indices/aglib"
        exec_command(cmd)


# --------------------------------------------------
if __name__ == '__main__':
    main()
