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

    # parser.add_argument('-i',
    #                     '--int',
    #                     help='A named integer argument',
    #                     metavar='\b',
    #                     type=int,
    #                     default=0)

    # parser.add_argument('-f',
    #                     '--file',
    #                     help='A readable file',
    #                     metavar='\b',
    #                     type=argparse.FileType('rt'),
    #                     default=None)

    # parser.add_argument('-t',
    #                     '--true',
    #                     help='A boolean flag',
    #                     action='store_true')

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

    # fastp: fast all-in-one preprocessing for FastQ files (https://github.com/OpenGene/fastp)
    # adapter trimming is disabled (--disable_adapter_trimming) because it doesn't work here
    fastp1 = re.sub("\..*", "", os.path.basename(r1)).replace(".*", "")
    fastp2 = re.sub("\..*", "", os.path.basename(r2)).replace(".*", "")
    if not os.path.exists(f'{outtmp}/{fastp1}.r1.fastp.fq'):
        logger.info("****** Fastp: umi extraction + dedup + qc ******\n")
        cmd = "fastp -i {r1} \
            -I {r2} \
            -o {outtmp}/{output1}.r1.fastp.fq \
            -O {outtmp}/{output2}.r2.fastp.fq \
            --disable_adapter_trimming \
            --length_required 100 \
            --umi \
            --umi_len 16 \
            --umi_loc read2 \
            --umi_prefix UMI \
            --dedup \
            -h {html} \
            -j {json}".format(
            r1=r1,
            r2=r2,
            outtmp=outtmp,
            output1=fastp1,
            output2=fastp2,
            html=f'{sample}.fastp.html',
            json=f'{sample}.fastp.json')  # minimum read length and dedup options
        exec_command(cmd)

    # Cutadapt: trimming of shared sequences in 5' of each reads
    # for read1 (to trim as an internal adapter, because of the stagger N {0,3})CGCTCAGCCTCGAGGTTT
    # for read2 (after 16n-UMI extraction): GCTGCGGAATTCGCGTTT
    if not os.path.exists(f'{outtmp}/{sample}.out.1.fastq'):
        logger.info(
            "****** Cutadapt: trimming of shared sequences in 5' of each read ******\n")
        cmd = f"docker run --rm \
                -v {outtmp}:/outtmp \
                quay.io/biocontainers/cutadapt:4.9--py39hff71179_1 \
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

    # bowtie2 alignment
    if not os.path.exists(f'{sample}.sam'):
        if os.path.exists(f"{os.path.dirname(lib)}/bowtie2_indices/aglib.1.bt2"):
            logger.info("****** Bowtie2: fastq alignment to library ******\n")
            cmd = f"bowtie2 \
                    -p {threads} \
                    -N 0 \
                    --no-1mm-upfront \
                    -q -1 {outtmp}/{sample}.out.1.fastq \
                    -2 {outtmp}/{sample}.out.2.fastq \
                    --no-unal \
                    -x {os.path.dirname(lib)}/bowtie2_indices/aglib \
                    --dovetail \
                    > {sample}.sam \
                    2> >(tee -a {sample}_{log} >&2)"
                    # --dovetail mates  extending "past" each other consider concordant by bowtie2
            exec_command(cmd)
        else:
            print("Bowtie2 indices not found –> Run bowtie2indices.py first")
            sys.exit()

    # Compute counts for each Ag
    if not os.path.exists(f'{sample}.counts.txt'):
        logger.info("****** Computing counts for each candidate Ag ******\n")
        # -F 0x80 removes read2 so that we only have one line per read, for the count.
        cmd = f"samtools view {sample}.sam -F 0x80 | \
            cut -f 3 | \
            sort | \
            uniq -c | \
            awk '{{printf(\"%s\\t%s\\n\", $2, $1)}}' > {sample}.counts.txt"
        exec_command(cmd)


# --------------------------------------------------
if __name__ == '__main__':
    main()
