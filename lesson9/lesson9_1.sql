SELECT count(*) AS "筆數"
FROM "台鐵車站資訊"


SELECT count(name) AS "台北車站數"
FROM "台鐵車站資訊"
WHERE "stationAddrTw" LIKE '%臺北%';

SELECT *
FROM "每日各站進出站人數" LEFT JOIN "台鐵車站資訊" ON "每日各站進出站人數"."車站代碼" =  "台鐵車站資訊"."stationCode"
WHERE "stationName" = '基隆'

/*
 * 全省各站點2022年進站總人數
 */

SELECT "name" AS 站名,COUNT("name") AS 筆數,AVG("進站人數") AS "進站人數"
FROM "每日各站進出站人數" LEFT JOIN "台鐵車站資訊" ON "車站代碼" = "stationCode"
WHERE "日期" BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY "name"

SELECT "name" AS 站名,date_part('year',"日期") AS "年份",COUNT("name") AS 筆數,AVG("進站人數") AS "進站人數"
FROM "每日各站進出站人數" LEFT JOIN "台鐵車站資訊" ON "車站代碼" = "stationCode"
WHERE "日期" BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY "name","年份"

SELECT "name" AS 站名,date_part('year',"日期") AS "年份",COUNT("name") AS 筆數,AVG("進站人數") AS "進站人數"
FROM "每日各站進出站人數" LEFT JOIN "台鐵車站資訊" ON "車站代碼" = "stationCode"
WHERE "name" = '基隆'
GROUP BY "name","年份"
ORDER BY "進站人數" DESC;

/*
 * 全省各站點2022年進站總人數大於5佰萬人的站點
 */

SELECT
    t."stationName" AS "車站名稱",
    SUM(p."進站人數") AS "2022年進站總人數"
FROM "每日各站進出站人數" p
LEFT JOIN "台鐵車站資訊" t ON p."車站代碼" = t."stationCode"
WHERE DATE_PART('year', p."日期") = 2022
GROUP BY t."stationCode", t."stationName"
HAVING SUM(p."進站人數") > 5000000
ORDER BY SUM(p."進站人數") DESC;


/*
*基隆火車站2020,2021,2022,每年進站人數
*/


/*
*隆火車站,臺北火車站2020,2021,2022,每年進站人數
*/

/*
*查詢 2022 年平均每日進站人數超過 2 萬人的站點
*/
