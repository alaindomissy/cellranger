for i in {1..1000}; do
~/proj/bedtools2/bin/bedtools intersect -a a.bed -b b.bed > /dev/null
done
