#!/bin/bash

BEDTOOLS=/home/ryan/proj/bedtools/bin/bedtools
BEDTOOLS2=/home/ryan/proj/bedtools2/bin/bedtools

echo "BEDTools 2.18+, peaks"
time for i in {1..50}; do $BEDTOOLS2 intersect -a SuHw_Kc_Bushey_2009.bed  -b SuHw_Kc_Bushey_2009.bed -sorted > /dev/null; done
echo
echo
echo "BEDTools 2.17, peaks"
time for i in {1..50}; do $BEDTOOLS intersect -a SuHw_Kc_Bushey_2009.bed  -b SuHw_Kc_Bushey_2009.bed -sorted > /dev/null; done
echo
echo
echo "BEDTools 2.18+, tiny"
time for i in {1..500}; do $BEDTOOLS2 intersect -a a.bed  -b b.bed > /dev/null; done
echo
echo
echo "BEDTools 2.17, tiny"
time for i in {1..500}; do $BEDTOOLS intersect -a a.bed  -b b.bed > /dev/null; done

