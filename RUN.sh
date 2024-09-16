#!/bin/bash

# Create Bowtie2 indices
# Optional, only if not done before for this library
python3 bowtie2index.py \
	/Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/proj/upscale/libraries/360RIO136/360RIO136_Lib_v1.0.fasta

# Run pipeline
python3 main.py \
	/Volumes/immuno_share/raw_data/itag/VHIO/360RIO136/Ag_lib_screen/Plasmid_library/AgLib_Lig_1.fastq.gz \
	/Volumes/immuno_share/raw_data/itag/VHIO/360RIO136/Ag_lib_screen/Plasmid_library/AgLib_Lig_2.fastq.gz \
	/Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/proj/upscale/libraries/360RIO136/360RIO136_Lib_v1.0.fasta

# Join counts
Rscript --vanilla join_counts.R /Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/bin/Aglib_screen/out \
	/Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/proj/upscale/libraries/360RIO136/360RIO136_Lib_v1.0.tsv