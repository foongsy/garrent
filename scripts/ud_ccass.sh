#!/usr/bin/env bash
# Setting paths
WORKDIR=$HOME/Bench/garrent
G_VENVDIR=$HOME/.virtualenvs/garrent/bin
S_VENVDIR=$HOME/.virtualenvs/sophybot/bin
# Go to working dir
cd $HOME/Bench/garrent
# Update garrent.ccass_player
$G_VENVDIR/python3 run.py ccassplayer --cleanup
# Update iamsophy.ccass_player
$S_VENVDIR/python3 run.py ccass_player
# Update garrent.ccass_snapshot garrent.ccass_details
$G_VENVDIR/python3 run.py q_ccass `date +'%Y-%m-%d' --date='yesterday'` `date +'%Y-%m-%d' --date='yesterday'`