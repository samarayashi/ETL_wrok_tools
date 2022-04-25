# 利用SQL驗證STG、BAS階段轉檔資料正確性

## 驗證內容

1. 總筆數
   - 利用`count`
2. 資料內容是否相同
   - 利用`group by`或`minus`
     - 將所有欄位`group by`起來後若`count(*)<>2`，則可能有資料不一致或資料重複的問題
     - 只利用`miuns`無法檢查資料是否重複

## 程式內容

1. CSV讀取來源表、目標表、欄位名稱
2. 序列化所讀取的資訊
3. 利用f-string做樣板字串
4. 將SQL內容寫出

## 補充

1. 樣板字串可以使用`string.Template`這個class  
   參考:  
    - [Official doc](https://docs.python.org/3/library/string.html#template-strings)
    - [String Template Class in Python](https://www.geeksforgeeks.org/template-class-in-python/)
2. 注意Blob型態不可以被`group by`
