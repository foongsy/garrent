#!/usr/bin/env bash
# Setting paths
WORKDIR=${HOME}/garrent
G_VENVDIR=${HOME}/.virtualenvs/garrent/bin
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd ${WORKDIR}
# Update garrent.ccass_player
${G_VENVDIR}/python3 run.py ccassplayer --cleanup
# Update garrent.ccass_snapshot garrent.ccass_details
${G_VENVDIR}/python3 run.py q_ccass `date +'%Y-%m-%d' --date='yesterday'` `date +'%Y-%m-%d' --date='yesterday'`
