# 專案小工具

## 備註

- DB與開發文件相關內容皆已替換過內容，僅保留形式供程式測試使用。
- 資料夾內有各自詳細的說明

## 工具清單  

1. SDM producer  
  依據SQL語句，產出需要使用的Table DDL、撈出機敏欄位、產出shared decision making文件內容
2. Produce multi session mrt  
  利用程式輔助產出informatica中含有多段session的workflow
3. 利用對照表進行資料加密  
  撰寫plsql，從原系統傾倒資料後最身分證、姓名做加密，並將SQL語句批次產出
4. DB fake data producer  
  撈取column的meta後，利用程式產出測試資料，以檢驗轉檔效能
5. 轉檔UT SQL  
  利用SQL驗證STG、BAS階段轉檔內容正確性，將語句批次產出
  