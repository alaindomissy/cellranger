#!/bin/bash

cellranger count \
  --id=xH09 \
  --sample=xH09 \
  --fastqs=./demofastqs \
  --transcriptome=./refdata-cellranger-hg19-1.2.0 \
  --nopreflight \
  --uiport=3600 \
  --no-exit


