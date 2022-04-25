# 加密資料表

- 目的  
    對來源表格的身分證、姓名做加密，使之能在開發區做使用。

- 流程  
  1. 將各系統原始資料表倒入副本表格  
  2. 將副本資料表中身分證與姓名加密

## 將原始資料倒入副本表格

- 利用oracle hint: `/*+ parallel (2) */`
- 利用`bulk collect`搭配 `insert all`
- 利用`DBMS_APPLICATION_INFO.SET_MODULE`來監看轉檔狀況
- 詳細請參考資料夾中的SQL語句說明、與DBMS_APPLICATION_INFO使用說明

## 加密副本表格

- 將人名的中間幾個字替代掉
- idn_token為原身分證和加密後身分證的對應轉換表
- 利用left join連接轉換表，把對應到的身分證做加密
- 身分證的轉換情況如下：  
  
|  原表   | 轉換表  | 結果 |
|  ----  | ----  | --- |
| NULL  |NULL    |  NULL|
| 有值  | 有對應 | 加密後結果|
|有值 | 無對應 | 能表No_match的不重複字串|

```SQL
decode(NVL(t1.idn_token, ori.idn),
  t1.idn_token, t1.idn_token
  null, null
  ori.idn, 'no_match'
  )
```
