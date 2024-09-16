#!/bin/bash

cat "/Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/proj/upscale/libraries/360RIO136/360RIO136_Lib_v1.0.tsv" | \
 awk '{printf ">"$1"\n"$2"\n"}' \
 > /Users/plevy/Library/CloudStorage/OneDrive-VHIO/labagros/pierre/proj/upscale/libraries/360RIO136/360RIO136_Lib_v1.0.fasta

# cat "TXT3_InSilicoVCV_VHIO136_hsSubPool04_[hsTRBC1_RQR8]_20220217_095808.txt" | \
#  awk '{printf ">"$1"\n"$2"\n"}' \
#  >> TCR_lib_RIO136_AAV.fasta
