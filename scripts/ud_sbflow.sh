#!/usr/bin/env bash
# Setting paths
WORKDIR=${HOME}/garrent
G_VENVDIR=${HOME}/.virtualenvs/garrent/bin
MYSQL_BIN=/usr/bin/mysql
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd ${WORKDIR}
# Update garrent.hk_topten
${G_VENVDIR}/python3 run.py sbtop10 `date +'%Y-%m-%d'` `date +'%Y-%m-%d'`