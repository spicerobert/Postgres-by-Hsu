SELECT "stationCode",name,"stationAddrTw",日期,進站人數,出站人數
FROM "台鐵車站資訊" LEFT JOIN "每日各站進出站人數" ON "stationCode" = "車站代碼";


SELECT COUNT(*) AS "筆數"
FROM "台鐵車站資訊" LEFT JOIN "每日各站進出站人數" ON "stationCode" = "車站代碼";

SELECT "stationCode",name,"stationAddrTw",日期,進站人數,出站人數
FROM "台鐵車站資訊" LEFT JOIN "每日各站進出站人數" ON "stationCode" = "車站代碼"
WHERE name LIKE '%臺北%';

SELECT "stationCode",name,"stationAddrTw",日期,進站人數,出站人數
FROM "台鐵車站資訊" LEFT JOIN "每日各站進出站人數" ON "stationCode" = "車站代碼"
WHERE "stationAddrTw" LIKE '%臺北市%';