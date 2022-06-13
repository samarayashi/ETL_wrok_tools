# 半自動化產出SDM(shared decision making)文件內容  

- 描述：  
    111年度新增許多資料範本需求，因此要依需求內容新增MRT_T_XXX(最終呈現表)和TMP_XXX(中間邏輯過度表)，與此同時亦需要將新增表格內容更新到 SDM上。將SQL語句輸入，此程式輔助產出SDM內容、DDL語句、機敏欄位檢測。

- 使用說明:  
  初始化：將以往SDM的EXCEL匯入DB中供後續使用  
  不論資料庫的表名、欄位名一律保持全大寫  

  - 輸入SQL語句要符合特定pattern`^(insert\s+into\s+.+?)?\(?select.+?from.+\)?`  
  - 若沒給新表名需要手動輸入新表名  
  - 預設欄位名稱、大小、Comment沿用來源欄位，若有多個來源欄位則會選機選擇一個  
  - 多個欄位來源時可以自行給予新欄位名稱，但仍需注意自行注意欄位  
  - 若有decode、concat等使用function的操作時，會在備註欄提示，注意欄位大小是否改變

- 有時要自己重新解構FROM後面的部分  
    程式是利用FROM後面的表格名，和個別欄位是否有指定table，去DB中尋找欄位資訊。  

    例如:原語句是使用由ta, tb組成的臨時表tmp的話，在自己的from後將其拆開為個別表ta a, ta b，欄位的部分則把指定tmp表名的部分去掉，讓程式自己去找相對應的表明。若有ambiguous的狀況再手動標記它是屬於哪張表。

    ```SQL
    select tmp.sno,
            tmp.ftyp, tmp.ciid as ciid, tmp.idn, tmp.brdte, fn_trn_h_char(tmp.name), tmp.hmk,
            tmp.uno, tmp.unock,
            tmp.txcd, tmp.efdte, tmp.seqno, tmp.wage, tmp.limk, tmp.oimk, tmp.eimk, tmp.couid, tmp.dept, tmp.celmk
            ,TO_DATE('#資料日#','YYYYMMDD') AS DATA_EXCH_DATE
    from (select .... a.ftyp ....... from ta a, tb b
    )tmp;
    ```

    改成

    ``` SQL
    select sno,
            a.ftyp, ciid as ciid, idn, brdte, fn_trn_h_char(name), hmk,
            uno, unock,
            txcd, efdte, seqno, wage, limk, oimk, eimk, couid, dept, celmk
            ,TO_DATE('#資料日#','YYYYMMDD') AS DATA_EXCH_DATE
    from ta a, tb b;
    ```

- 程式架構
  - raw_sql.py  
  輸入新表的原始SQL後，將會針對其字面上的文字做分析，抓出每個欄位的屬性。
  - column_info.py  
  把字面上欄位分析的結果，丟回到DB去做查詢，產出新表欄位的詳細內容，並且將之寫回DB中。
  - db.py  
  產生DB connection, cursor等實例供使用
  - sdm.py  
  產出SDM內容、DDL語句、機敏欄位表格
