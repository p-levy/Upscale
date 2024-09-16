#!/bin/bash

cat ${1} | \
 awk '{printf ">"$1"\n"$2"\n"}' \
 > ${2}
