import pybedtools
from pybedtools.contrib import classifier

gff = pybedtools.example_bedtool('classifier_annotations.gff')


def bed_generator():
    for line in open(gff.fn):
        if line.startswith('# chr2L'):
            yield pybedtools.create_interval_from_list(line[2:].strip().split('\t'))

bed = pybedtools.BedTool(bed_generator()).saveas()
gff = gff.sort()

mult = classifier.MultiClassifier(bed=bed, annotations=gff, genome='dm3', sample_name='sample')
non = classifier.Classifier(bed=bed, annotations=gff)

mult.classify()
non.classify()
