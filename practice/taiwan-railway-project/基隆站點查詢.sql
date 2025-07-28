-- 創建台鐵車站資訊表 (如果表格不存在)
CREATE TABLE IF NOT EXISTS "台鐵車站資訊" (
    "stationCode" INTEGER PRIMARY KEY,
    "stationName" VARCHAR(50) NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "stationAddrTw" VARCHAR(200),
    "stationTel" VARCHAR(20),
    "gps" VARCHAR(50),
    "haveBike" CHAR(1)
);

-- 插入基隆地區的站點資料
INSERT INTO "台鐵車站資訊" ("stationCode", "stationName", "name", "stationAddrTw", "stationTel", "gps", "haveBike")
VALUES
    (900, '基隆', '基隆', '基隆市仁愛區港西街5號', '02-24263743', '25.13411 121.73997', 'Y'),
    (910, '三坑', '三坑', '基隆市仁愛區德厚里龍安街 206 號', '02-24230289', '25.12305 121.74202', 'Y'),
    (920, '八堵', '八堵', '基隆市暖暖區八南里八堵路 142 號', '02-24560841', '25.10843 121.72898', 'Y'),
    (930, '七堵', '七堵', '基隆市七堵區長興里東新街 2 號', '02-24553426', '25.09294 121.71415', 'Y'),
    (940, '百福', '百福', '基隆市七堵區堵南里明德三路 1 之 1 號', '02-24528372', '25.07795 121.69379', 'N'),
    (7361, '海科館', '海科館', '基隆市中正區長潭里', '02-24972033', '25.13754 121.79997', 'N'),
    (7390, '暖暖', '暖暖', '基隆市暖暖區暖暖里暖暖街 51 號', '02-24972033', '25.10224 121.74048', 'N')
ON CONFLICT ("stationCode") DO UPDATE
SET
    "stationName" = EXCLUDED."stationName",
    "name" = EXCLUDED."name",
    "stationAddrTw" = EXCLUDED."stationAddrTw",
    "stationTel" = EXCLUDED."stationTel",
    "gps" = EXCLUDED."gps",
    "haveBike" = EXCLUDED."haveBike";

-- 查詢基隆地區的所有站點
SELECT * FROM "台鐵車站資訊" WHERE "stationAddrTw" LIKE '%基隆%';

-- 查詢基隆地區站點數量
SELECT COUNT(*) AS "基隆站點數量" FROM "台鐵車站資訊" WHERE "stationAddrTw" LIKE '%基隆%';

-- 查詢基隆地區提供自行車服務的站點
SELECT * FROM "台鐵車站資訊" WHERE "stationAddrTw" LIKE '%基隆%' AND "haveBike" = 'Y';

-- 查詢基隆地區不提供自行車服務的站點
SELECT * FROM "台鐵車站資訊" WHERE "stationAddrTw" LIKE '%基隆%' AND "haveBike" = 'N';

-- 按區域分組查詢基隆站點數量
SELECT
    SUBSTRING("stationAddrTw" FROM '基隆市([^區]+)區') AS "區域",
    COUNT(*) AS "站點數量"
FROM "台鐵車站資訊"
WHERE "stationAddrTw" LIKE '%基隆市%'
GROUP BY SUBSTRING("stationAddrTw" FROM '基隆市([^區]+)區')
ORDER BY COUNT(*) DESC;