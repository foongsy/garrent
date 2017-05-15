#!/usr/bin/env bash
# Setting paths
WORKDIR=$HOME/Bench/garrent
G_VENVDIR=$HOME/.virtualenvs/garrent/bin
S_VENVDIR=$HOME/.virtualenvs/sophybot/bin
export QT_QPA_PLATFORM=offscreen
# Go to working dir
cd $HOME/Bench/garrent
# Update garrent.ccass_player
$G_VENVDIR/python3 run.py ccassplayer --cleanup
# Update garrent.ccass_snapshot garrent.ccass_details
$G_VENVDIR/python3 run.py q_ccass `date +'%Y-%m-%d' --date='yesterday'` `date +'%Y-%m-%d' --date='yesterday'`
# Go to working dir
cd $HOME/Bench/sophybot
# Update iamsophy.ccass_player
$S_VENVDIR/python3 run.py ccass_player
# Copy data from garrent to iamsophy
/usr/bin/mysql/mysql -Bse "INSERT INTO iamsophy.ccass_summary (code, date, total_players, named_investors, unamed_investors, total_in_ccass, total_outstanding)
 SELECT code, date, players_total, named_investors, unnamed_investors, total_in_ccass, total_outstanding FROM garrent.ccass_snapshot WHERE date = '`date +'%Y-%m-%d' --date='yesterday'`';
 INSERT INTO iamsophy.ccass_detail (code, date, player_id, holding)
 SELECT code, date, player_id, holding FROM garrent.ccass_details WHERE date = '`date +'%Y-%m-%d' --date='yesterday'`';"
# INSERT INTO iamsophy.ccass_summary (code, date, total_players, named_investors, unamed_investors, total_in_ccass, total_outstanding)
#    SELECT code, date, players_total, named_investors, unnamed_investors, total_in_ccass, total_outstanding FROM garrent.ccass_snapshot;
# INSERT INTO iamsophy.ccass_detail (code, date, player_id, holding)
#    SELECT code, date, player_id, holding FROM garrent.ccass_details;
