#!/usr/bin/env bash
cd $HOME/Bench/garrent
# Update garrent.stock
$HOME/.virtualenvs/garrent/bin/python3 run.py stock --cleanup
# Update garrent.sbstock
$HOME/.virtualenvs/garrent/bin/python3 run.py sbstock --cleanup
cd $HOME/Bench/sophybot
# Update iamsophy.Equity
$HOME/.virtualenvs/sophybot/bin/python3 run.py update_equity
