# Garrent

Garrent is a personal project of mine to scrap and analyse data from [HKEX](http://www.hkexnews.hk) includes stock list, CCASS, SHHK/SZHK connect, and etc. The script worked fine in late 2018, however due to some changes made by HKEX, some script might not work anymore.

This project was a precedent of a  Wechat Mini Program developed internally by "YY港股圈" (YY Hong Kong Stock Circle, wechat ID: Victoria-hk-stocks). However due to the rapid change of market conditions and sentiment, the project was never launched.

The goal of releasing this personal project is to:
- As a part of my personal portfolio
- For interested parties who would like to work on the area without having to work from ground up.

## Background

Garrent was originally the data backend of a bigger project, therefore it does not come with a front-end GUI. The output of garrent is a whole bunch of processed data lying on database. I might consider releasing the front end, which is an unfinished conversational UI to the data, sometime in the future.

Although Garrent does not handle trading data (i.e. stock OHLCV data), the data being taken in is considerably numerous for a personal project. Data size of 200-300MB are collected per day approximately. Historical data is available for a year so inital database size would be at least 10GB, without counting the indices. MySQL database optimization knowledege is therefore essential, I recommend O'reilly's *[High Performance MySQL: Optimization, Backups, and Replication](https://www.goodreads.com/book/show/18759121-high-performance-mysql)* as a start.

To use this code, understanding of HKEX data structure is as important as coding skills. The project intended to cover following data scrapping:
- Stock List*
- CCASS Participant List
- Daily shortsell data (from [http://www.analystz.hk](https://www.analystz.hk/short/short-selling-turnover-filter.php))
- CCASS Holding List
- Southbound top 10 list
- Disclosure Interests

*To the date of writing this document, due to web site layout changes, the data scrapping marked with (\*) no longer works.*

Furthermore, since the data being scrapped is numerous, Garrent uses [RQ](https://python-rq.org/docs/) to manage data scrapping task queue.

### Prerequisites

- Python 3
- MySQL compliant, recommended using [Percona](https://www.percona.com/)
- [Redis](https://redis.io/) 
- [PhantomJS](http://phantomjs.org/)

### Configuration

To get Garrent working, different cron jobs are required for data scrapping, data cleansing and data mining. This part will guide through setup step by step.

**1. Database Path**

Both `./garrent/database.py` and `./garrent/pw_models.py` have to be modified to reflect database path. The reason of using *[pymysql](https://pymysql.readthedocs.io/en/latest/)* and *[peewee](http://docs.peewee-orm.com/en/latest/)* at the same time are due to some legacy development issue. However peewee is preferred for future development, if any.

**2. Command-line script**

*run.py* is the core command line script for most functions. It uses [click](https://click.palletsprojects.com/en/master/) as simple commandline interface. General usage should be:
```
./run.py [command] [options]
```
Supported commands are listed as following.

1) `status`

2) `initdb`

3) `cleanup`

4) `stock`

5) `ccassplayer`

6) `buyback`

7) `q_buyback`

8) `q_shareholder`

9) `q_ccass`

10) `sbtop10`

11) `sbstock`

12) `failed`

13) `sbholding`

**3. Cron Jobs**

There are 3 shell scripts to do the data scrapping and cleansing:
- `./garrent/scripts/ud_equity.sh`
    - Update equity list
- `./garrent/scripts/ud_sbflow.sh`
    - Update Southbound Top 10 stock lists
- `./garrent/scripts/ud_ccass.sh`
    - Update CCASS players and holdings

The scripts should be ran one by one between 00:00:00 HKT and 06:00:00 HKT after trading day to avoid trading hour lagging. RQ  workers should be set no more than 3 or you might face IP ban from HKEX.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/garrent/tags). 

## Authors

* **Henry Fong** - *Initial work* - [foongsy](https://github.com/foongsy)

See also the list of [contributors](contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
