#!/usr/bin/env bash
# Setting paths
WORKDIR=${HOME}/garrent
G_VENVDIR=${HOME}/.virtualenvs/garrent/bin
# Fixed PhantomJS problem
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd $WORKDIR
# Update garrent.stock
${G_VENVDIR}/python3 run.py stock --cleanup
# Update garrent.sbstock
${G_VENVDIR}/python3 run.py sbstock --cleanup