#!/usr/bin/env bash
# Setting paths
WORKDIR=$HOME/Bench/garrent
G_VENVDIR=$HOME/.virtualenvs/garrent/bin
S_VENVDIR=$HOME/.virtualenvs/sophybot/bin
# Go to working dir
cd $HOME/Bench/sophybot
# Update iamsophy.ccass_player
$S_VENVDIR/python3 run.py ccass_hdgc `date +'%Y-%m-%d' --date='yesterday'` `date +'%Y-%m-%d' --date='yesterday'` --playerid=A00003
$S_VENVDIR/python3 run.py ccass_hdgc `date +'%Y-%m-%d' --date='yesterday'` `date +'%Y-%m-%d' --date='yesterday'` --playerid=A00004
$S_VENVDIR/python3 run.py update_sbweekly
