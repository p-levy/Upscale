# Antigen-Library Screen Analysis

⚠️ **Docker required** 🐳

## Generate Ag lib fasta file and bowtie2 indices

### Ag lib fasta
Usage: 
`./convert_lib_to_fasta.sh library.tsv library.fasta` <br>
where `library.tsv` contains two columns, without header, where column 1 is the Ag unique IDs and column 2 the Ag sequences.

### Bowtie2 indices

Usage: 
`./bowtie2index.py library.fasta` <br>

## Run pipeline

Usage for **one sample**: 
```./main.py read1.fastq read2.fastq library.fasta``` <br>
Options: <br>
`-l --log` name of log file (default: `log.txt`) <br>
`-o --out` output folder (default: `out`) <br>
`-t --threads` number of cpus to use, for `cutdadapt` and `bowtie2` steps (default: `4`)

Usage for **multiple sample**: <br>
```bash
paste samples.read1.txt samples.read2.txt | xargs -n 2 -P 1 bash -c 'python3 main.py "$0" "$1" library.fasta -t 12'
```
Where `samples.read1.txt` and `samples.read2.txt` are lists of paired read1 and read2 fastq files, respectively.
```
$ cat samples.read1.txt
/path/to/sample1.R1.fastq.gz
/path/to/sample2.R1.fastq.gz
/path/to/sample3.R1.fastq.gz
/path/to/sample4.R1.fastq.gz
...
```
and
```
$ cat samples.read2.txt
/path/to/sample1.R2.fastq.gz
/path/to/sample2.R2.fastq.gz
/path/to/sample3.R2.fastq.gz
/path/to/sample4.R2.fastq.gz
...
```
## Join counts

Make one single count table for all samples
Usage: `./join_counts.R out library.tsv`
where `out` is the output directory containing the count files for each sample ending with `.count` and `library.tsv` contains the Ag unique IDs in column 1.