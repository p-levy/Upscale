#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(data.table))
  
args = commandArgs(trailingOnly=TRUE)

# Usage
if (length(args)==0 | args[1]=="-h" | args[1]=="--help") {
  cat("
How to use:
arg1: path to directory where counts.txt files are located
arg2: path/to/AglibTable

      ")
  quit()
}

dir_counts <- args[1]
ag_lib <- fread(args[2], header = F)
colnames(ag_lib) <- c("Ag.ID", "seq")

# Set WD to path where count files are located
setwd(normalizePath(dir_counts))

# Get a vector containing only the count files from that directory
count_files <- dir(dir_counts)[grep(dir(dir_counts), pattern = ".*\\.counts")]

# create dt that will receive all counts from the individual files (column 1 = ag lib ids)
finalCounts <- ag_lib[,1]

# loop for adding counts from each file
for (file in count_files) {
  countTbl <- fread(file)
  colnames(countTbl) <- c("Ag.ID", gsub(".counts.txt", "", file))
  finalCounts <- finalCounts %>% full_join(countTbl, by = "Ag.ID")
}

# Replace NAs by 0 counts
finalCounts[is.na(finalCounts)] <- 0

# Write final count table
write.table(finalCounts, file = "all.counts.txt", sep = "\t", row.names = F, quote = F)

