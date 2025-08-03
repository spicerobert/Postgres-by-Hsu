SELECT count(*) AS "筆數"
FROM "台鐵車站資訊"


SELECT count(name) AS "台北車站數"
FROM "台鐵車站資訊"
WHERE "stationAddrTw" LIKE '%臺北%';