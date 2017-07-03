FROM ubuntu:16.04
#FROM python:2.7-slim
#FROM continuumio/miniconda:4.3.11
MAINTAINER adomissy@ucsd.edu

WORKDIR /cellranger

EXPOSE 3600

RUN apt-get update && apt-get install -y nano unzip zip

COPY files /cellranger

RUN tar -xzvf cellranger-2.0.0.tar.gz && rm cellranger-2.0.0.tar.gz \
    mv getdemo getrefdata /cellranger/cellranger-2.0.0

ENV PATH /cellranger/cellranger-2.0.0:/cellranger/bin:/usr/local/bin:/usr/bin:/bin

#ENV REFDATA /cellranger

CMD "/bin/bash"
ENTRYPOINT "/bin/bash"




#%labels
#VERSION 0.0.1
#BUILD_DATE 20170701

#%setup
#mkdir -p $SINGULARITY_ROOTFS/media/mis

#%files
  # cellranger-2.0.0.tar.gz /opt/

#%post
  # wget wget -O cellranger-2.0.0.tar.gz "http://cf.10xgenomics.com/releases/cell-exp/cellranger-2.0.0.tar.gz?Expires=1498884401&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cDovL2NmLjEweGdlbm9taWNzLmNvbS9yZWxlYXNlcy9jZWxsLWV4cC9jZWxscmFuZ2VyLTIuMC4wLnRhci5neiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTQ5ODg4NDQwMX19fV19&Signature=XXAmQ-kR~g~QuQnxU3AU6spcFYmXCSMMp0AUYET1a6gIq~~yaDmbe0vzcQdUtHZkDEo8~QezvKLeCVQ77IaqTaPUZd1rvdVVbmZ6bjy~St3fWcRoMOD1Pml6qpH-t7KG18z~eGnkBdCC8P7LC68grTIKsKfr8ipE1-5JTTntFN39vHpCZKOUgTp1qG6YuKMVOBMcq3Nt9dr3LScRoioPTHulAdFWTcG0V~5HQDgzwWlHiT-LIUL-ndhLBPh~hTbr8kOSbwLssO-hR1VNzvzbC6XA9vjst6CxDYj4cK4snrLZLxgXmwVK9zKqE2VjRpdWZMA-itAeelgjZp9c3x~q3g__&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA"
  # tar -xzvf cellranger-2.0.0.tar.gz
  # rm cellranger-2.0.0.tar.gz
  #cp cellranger-2.0.0.tar.gz $SINGULARITY_ROOTFS/opt/
  #cp refdata/refdata-cellranger-ercc92-1.2.0.tar.gz  $SINGULARITY_ROOTFS/opt/

#%runscript
  #SUBCOMMAND="$1"
  #if [ $SUBCOMMAND = "getrefdata" ]
  #then
  #  /opt/bin/getrefdata $2
  #elif [ $SUBCOMMAND = "getdemo" ]
  #then
  #  /opt/bin/getdemo
  #else
  #  #/opt/cellranger-2.0.0/cellranger $@
  #  #cellranger $@
  #  PREVIOUSPS1=$PS1
  #  PS1="$SINGULARITY_CONTAINER":"$PS1"
  # bash
  # PS1=$PREVIOUSPS1
  #fi

