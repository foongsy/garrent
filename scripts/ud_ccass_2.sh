#!/usr/bin/env bash

/usr/bin/mysql -Bse "INSERT INTO iamsophy.ccass_summary (code, date, total_players, named_investors, unamed_investors, total_in_ccass, total_outstanding)
 SELECT code, date, players_total, named_investors, unnamed_investors, total_in_ccass, total_outstanding FROM garrent.ccass_snapshot WHERE date = '`date +'%Y-%m-%d' --date='yesterday'`';
 INSERT INTO iamsophy.ccass_detail (code, date, player_id, holding)
 SELECT code, date, player_id, holding FROM garrent.ccass_details WHERE date = '`date +'%Y-%m-%d' --date='yesterday'`';"
