SELECT p."日期",
       t."stationName" AS 車站,
       p."進站人數",
       p."出站人數"
FROM public."每日各站進出站人數" p
JOIN public."台鐵車站資訊" t
  ON p."車站代碼" = t."stationCode"
WHERE p."日期" = DATE '2023-01-01'
  AND t."stationName" = '基隆';

