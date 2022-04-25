# 程式輔助產出informatica底層XML：TMP表格模板

## 目的描述

  Informatica以XML儲存轉檔設定，因此若可以直接產出XML檔，就可以免去使用GUI工具繁瑣的操作流程。在GUI中拉出TMP表格轉檔流程的樣板，利用程式修改並且替換XML中的內容，將產出XML半成品匯入informatica做使用。

## 實作內容

  基本上它做了三件事情

  1. 將SQL內容轉換成想要的樣子  
     - 清除多餘注釋
     - 將替換上informatica內部使用參數
     - 將對不到的欄位補上NULL，使select內容和table可以對應
  2. 填入資料，修改XML中該tag的屬性  
     - 開發紀錄comment
     - SQL Query語句，撈取轉檔資料
     - pre-SQL動作，例如是否truncate
     - post-SQL動作，例如merge、update
  3. 以取代的方式，替換樣板字串  
     - 並非改變GUI中預設可以操作的屬性，而是利用infa是依據名稱讀取物件的特性。
     - 以mapping為例: 只要把樣板中mapping name，改成實際存在的目標mapping name，匯入XML時infa就會去讀取該實際存在的mapping。
     - 因為mapping、session、workflow一層層疊上來不確定會動到XML中哪些部分，有哪些設定會一起牽動，因此以替換字串的方式進行
     - mapping name, session name, workflow name，infa內部調用物件的名稱皆以此方式處理

## 使用說明

產出XML

- template放在source資料夾中
- 在source中丟入指定格式CSV
- 產出的XML匯入infa後，需要刪除沒用到樣板session與其相關的設定
  
單獨產出SQL  

- utils.tmp_null_filled中放入指定格式CSV
- `python -m utils.tmp_null_filled.null_filled`
