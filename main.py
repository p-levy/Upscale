#!/usr/bin/env python3
"""
Author : Pierre Levy <levy.pierre@yahoo.fr>
Date   : 2024-09-13
Purpose: Ag	 library screen processing
"""

import argparse
import subprocess
import os
import re
import logging
import sys


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Ag library screen processing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('r1',
                        metavar='str',
                        help='fastq(.gz) read 1')

    parser.add_argument('r2',
                        metavar='str',
                        help='fastq(.gz) read 2')

    parser.add_argument('lib',
                        metavar='str',
                        help='fasta file containing library Ag sequences')

    parser.add_argument('-l',
                        '--log',
                        help='Name of the log file',
                        metavar='\b',
                        type=str,
                        default='log.txt')

    parser.add_argument('-o',
                        '--out',
                        help='Output dir name',
                        metavar='\b',
                        type=str,
                        default='out')

    parser.add_argument('-t',
                        '--threads',
                        help='Number of threads for certain steps',
                        metavar='\b',
                        type=str,
                        default='4')

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
    r1 = os.path.abspath(args.r1)
    r2 = os.path.abspath(args.r2)
    lib = os.path.abspath(args.lib)
    log = args.log
    out = args.out
    threads = args.threads

    # Sample name
    sample = re.sub("_1\.f.*q*", "", os.path.basename(r1))

    # create output directory out and set as current wd
    if not os.path.exists(f'{os.getcwd()}/{out}'):
        os.mkdir(f'{os.getcwd()}/{out}')  # create dir
    outdir = f'{os.getcwd()}/{out}'  # create outdir variable
    os.chdir(outdir)  # set as new wd (uncomment if desired)

    # create tmp_output directory tmp within output dir
    if not os.path.exists(f'{outdir}/tmp'):
        os.mkdir(f'{outdir}/tmp')  # create dir
    outtmp = f'{outdir}/tmp'  # create outtmp variable

    # Create log file
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG,
                        handlers=[
                            logging.FileHandler(f'{sample}_{log}'),
                            # these 2 handlers allow 1) to have the log file created and 2) to stream to the terminal
                            logging.StreamHandler()
                        ])

    logger = logging.getLogger()  # creates logger to add entries to the log

    # fastp: fast all-in-one preprocessing for FastQ files (Docker version)
    fastp1 = re.sub("\..*", "", os.path.basename(r1)).replace(".*", "")
    fastp2 = re.sub("\..*", "", os.path.basename(r2)).replace(".*", "")
    if not os.path.exists(f'{outtmp}/{fastp1}.r1.fastp.fq'):
        logger.info("****** Fastp (Docker): umi extraction + dedup + qc ******\n")
        cmd = f"docker run --rm -v {os.path.dirname(r1)}:/data -v {outtmp}:/outtmp quay.io/biocontainers/fastp:1.0.1--heae3180_0 fastp "
        cmd += f"-i /data/{os.path.basename(r1)} "
        cmd += f"-I /data/{os.path.basename(r2)} "
        cmd += f"-o /outtmp/{fastp1}.r1.fastp.fq "
        cmd += f"-O /outtmp/{fastp2}.r2.fastp.fq "
        cmd += "--disable_adapter_trimming "
        cmd += "--length_required 100 "
        cmd += "--umi "
        cmd += "--umi_len 16 "
        cmd += "--umi_loc read2 "
        cmd += "--umi_prefix UMI "
        cmd += "--dedup "
        cmd += f"-h /outtmp/{sample}.fastp.html "
        cmd += f"-j /outtmp/{sample}.fastp.json"
        exec_command(cmd)

    # Cutadapt: trimming of shared sequences in 5' of each reads
    # for read1 (to trim as an internal adapter, because of the stagger N {0,3})CGCTCAGCCTCGAGGTTT
    # for read2 (after 16n-UMI extraction): GCTGCGGAATTCGCGTTT
    if not os.path.exists(f'{outtmp}/{sample}.out.1.fastq'):
        logger.info(
            "****** Cutadapt: trimming of shared sequences in 5' of each read ******\n")
        cmd = f"docker run --rm \
                -v {outtmp}:/outtmp \
                quay.io/biocontainers/cutadapt:5.1--py310h1fe012e_0 \
                cutadapt \
                -g CGCTCAGCCTCGAGGTTT \
                -G GCTGCGGAATTCGCGTTT \
                -o /outtmp/{sample}.out.1.fastq \
                -p /outtmp/{sample}.out.2.fastq \
                outtmp/{fastp1}.r1.fastp.fq \
                outtmp/{fastp2}.r2.fastp.fq \
                --cores={threads} \
                && rm -rf /outtmp/{fastp1}.r1.fastp.fq \
                outtmp/{fastp2}.r2.fastp.fq"
        logger = logging.getLogger()
        logger.info(cmd)
        logfile = open(f"{sample}_{log}", "a")
        p = subprocess.Popen(cmd, shell=True, stdout=logfile,
                            stderr=subprocess.STDOUT, executable='/bin/bash')
        output, error = p.communicate()
        if p.returncode != 0:
            for line in output.decode("utf-8").split("\n") if output else "":
                    logger.error(line.rstrip())
            for line in error.decode("utf-8").split("\n") if error else "":
                logger.error(line.rstrip())
            sys.exit()

    # bowtie2 alignment (Docker version)
    if not os.path.exists(f'{sample}.sam'):
        if os.path.exists(f"{os.path.dirname(lib)}/bowtie2_indices/aglib.1.bt2"):
            logger.info("****** Bowtie2 (Docker): fastq alignment to library ******\n")
            # Mount outtmp and bowtie2_indices
            cmd = f"docker run --rm -v {outtmp}:/outtmp -v {os.path.dirname(lib)}/bowtie2_indices:/indices quay.io/biocontainers/bowtie2:2.5.4--he96a11b_6 bowtie2 "
            cmd += f"-p {threads} "
            cmd += "-N 0 "
            cmd += "--no-1mm-upfront "
            cmd += f"-q -1 /outtmp/{sample}.out.1.fastq -2 /outtmp/{sample}.out.2.fastq "
            cmd += "--no-unal "
            cmd += "--dovetail "
            cmd += "-x /indices/aglib "
            cmd += f"> {outtmp}/{sample}.sam 2>> {outtmp}/{sample}_{log}"
            exec_command(cmd)
            # Move .sam file to current directory
            if os.path.exists(f"{outtmp}/{sample}.sam"):
                os.rename(f"{outtmp}/{sample}.sam", f"{sample}.sam")
        else:
            print("Bowtie2 indices not found –> Run bowtie2indices.py first")
            sys.exit()

    # Compute counts for each Ag (Docker version)
    if not os.path.exists(f'{sample}.counts.txt'):
        logger.info("****** Computing counts for each candidate Ag (Docker) ******\n")
        # Use samtools via Docker, mount current dir
        cmd = f"docker run --rm -v {os.getcwd()}:/data quay.io/biocontainers/samtools:1.22.1--h96c455f_0 samtools view /data/{sample}.sam -F 0x80 "
        cmd += f"| cut -f 3 | sort | uniq -c | awk '{{printf(\"%s\\t%s\\n\", $2, $1)}}' > {sample}.counts.txt"
        exec_command(cmd)


# --------------------------------------------------
if __name__ == '__main__':
    main()
