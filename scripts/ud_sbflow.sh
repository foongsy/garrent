#!/usr/bin/env bash
# Setting paths
WORKDIR=$HOME/Bench/garrent
G_VENVDIR=$HOME/.virtualenvs/garrent/bin
S_VENVDIR=$HOME/.virtualenvs/sophybot/bin
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd $HOME/Bench/garrent
# Update garrent.hk_topten
$G_VENVDIR/python3 run.py sbtop10 `date +'%Y-%m-%d'` `date +'%Y-%m-%d'`
# Update sql database
/usr/bin/mysql -Bse "INSERT INTO iamsophy.sb_topten (code,buy,date,market,sell)
SELECT code,buy,date,market,sell FROM garrent.hk_topten WHERE date = '`date +'%Y-%m-%d'`';"
# Go to working dir
cd $HOME/Bench/sophybot
# Update iamsophy.ccass_player
$S_VENVDIR/python3 run.py update_sbtopten
