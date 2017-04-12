#!/usr/bin/env bash
# Setting paths
WORKDIR=$HOME/Bench/garrent
G_VENVDIR=$HOME/.virtualenvs/garrent/bin
S_VENVDIR=$HOME/.virtualenvs/sophybot/bin
# Fixed PhantomJS problem
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd $HOME/Bench/garrent
# Update garrent.stock
$G_VENVDIR/python3 run.py stock --cleanup
# Update garrent.sbstock
$G_VENVDIR/python3 run.py sbstock --cleanup
# Go to working dir
cd $HOME/Bench/sophybot
# Update iamsophy.Equity
$S_VENVDIR/python3 run.py update_equity
