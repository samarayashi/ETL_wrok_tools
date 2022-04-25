# 產出CSV測試資料

- `SELECT * FROM ALL_TAB_COLUMNS`抓出TABLE的meta-data
- 將meta-data存成CSV讓程式讀取
- 可以將所有欄位都產出測試資料，或是隨機挑幾欄產出
- not null欄位必定會產出
- 依據欄位資料型態、長度決定，要調入的值

|資料型態| 輸出結果|
|---|----|
|char, varchar| min(最大長度,10)的隨機字串|
|number| 小隨最大長度的隨機字串|
|date| 當天日期|
