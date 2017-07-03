#
# Copyright (c) 2017 10x Genomics, Inc. All rights reserved.
#
# Environment setup for package cellranger-2.0.0.
# Source this file before running.
#

set SOURCE=($_)
if ( "$SOURCE" != "" ) then
    set SOURCE=`readlink -f "$SOURCE[2]"`
else
    set SOURCE=`readlink -f "$0"`
endif
set DIR=`dirname $SOURCE`

#
# Source user's own environment first.
#
# Note .login is for login shells only.
source ~/.cshrc

#
# Modify the prompt to indicate user is in 10X environment.
#


#
# Set aside environment variables if they may conflict with 10X environment
#

if ( ! $?_TENX_LD_LIBRARY_PATH ) then
    setenv _TENX_LD_LIBRARY_PATH "$LD_LIBRARY_PATH"
    setenv LD_LIBRARY_PATH ""
endif


#
# Unset environment variables if they may conflict with 10X environment
#

if ( $?PYTHONPATH ) then
    unsetenv PYTHONPATH
endif


#
# Add module binary paths to PATH
#

if ( ! $?PATH ) then
    setenv PATH "$DIR/STAR/2.5.1b"
else
    setenv PATH "$DIR/STAR/2.5.1b:$PATH"
endif
setenv PATH "$DIR/anaconda-cr-cs/2.2.0-anaconda-cr-cs-c7/bin:$PATH"
setenv PATH "$DIR/martian-cs/2.1.3/bin:$PATH"
setenv PATH "$DIR/cellranger-cs/2.0.0/bin:$PATH"
setenv PATH "$DIR/cellranger-cs/2.0.0/tenkit/bin:$PATH"
setenv PATH "$DIR/cellranger-cs/2.0.0/tenkit/lib/bin:$PATH"
setenv PATH "$DIR/cellranger-cs/2.0.0/lib/bin:$PATH"
setenv PATH "$DIR/cellranger-tiny-ref/1.2.0:$PATH"
setenv PATH "$DIR/cellranger-tiny-fastq/1.2.0:$PATH"
setenv PATH "$DIR/samtools_new/1.4:$PATH"


#
# Module-specific env vars
#
# martian-cs

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH "$DIR/martian-cs/2.1.3/adapters/python"
else
    setenv PYTHONPATH "$DIR/martian-cs/2.1.3/adapters/python:$PYTHONPATH"
endif
# cellranger-cs
setenv MROFLAGS "--vdrmode=rolling"
setenv LC_ALL "C"
setenv MROPATH "$DIR/cellranger-cs/2.0.0/mro"

if ( ! $?MROPATH ) then
    setenv MROPATH "$DIR/cellranger-cs/2.0.0/tenkit/mro"
else
    setenv MROPATH "$DIR/cellranger-cs/2.0.0/tenkit/mro:$MROPATH"
endif
setenv PYTHONPATH "$DIR/cellranger-cs/2.0.0/lib/python:$PYTHONPATH"
setenv PYTHONPATH "$DIR/cellranger-cs/2.0.0/tenkit/lib/python:$PYTHONPATH"
setenv PYTHONUSERBASE "$DIR/cellranger-cs/2.0.0/lib"

