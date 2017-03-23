select s.date as s_date, t.date, s.holding - t.holding as changes, s.date - interval 1 day as yday
from sb_holding s,
  (select date, holding from sb_holding where code = '00001') as t
where s.code = '00001' HAVING yday = t.date;

SELECT a.*, b.pholding FROM sb_holding a LEFT JOIN
(
  SELECT code, date + INTERVAL 1 DAY AS nextday, holding AS pholding FROM sb_holding
) AS b
ON a.code = b.code AND a.date = b.nextday
WHERE a.code = '00939'

-- CCASS changes, only update Tuesdays to Fridays

UPDATE sb_holding a INNER JOIN
(
  SELECT code, date + INTERVAL 1 DAY AS nextday, holding AS pholding FROM sb_holding
) AS b
ON a.code = b.code AND a.date = b.nextday
SET a.changes = a.holding - b.pholding

-- CCASS changes, handle non-consecutive closet day

SELECT a.*,b.date as b_date, b.holding as b_holding, DATEDIFF(a.date,b.date) as daysdiff FROM sb_holding a INNER JOIN sb_holding b
ON a.code = b.code
WHERE a.date > b.date AND b.changes IS NULL AND daysdiff =
(
  SELECT DATEDIFF(a.date,b.date)
  FROM sb_holding a INNER JOIN sb_holding b
  ON a.code = b.code AND a.date > b.date AND b.changes IS NULL
)
