CREATE OR REPLACE PACKAGE BODY MX.sync_oracle AS


PROCEDURE A_TA_SYNC (
	fetch_date IN STG_A_TA.data_exch_date%TYPE DEFAULT SYSDATE,
	fetch_limit_in       IN number DEFAULT 100000)
IS
	-- 之後確認原資料有幾筆使用
	chk_data number:=0;
	
	-- /*+ parallel (2) */  => oracle特有的Hint提示，可優化效能
	-- 所有欲從oracle拉過來的欄位
	CURSOR  cur_oracle IS
		SELECT /*+ parallel (8) */ SAL_DATES,SAL_DATEE,SAL_TP,SAL_MIN,SAL_MAX,WAGE,WAGE_TYPE,WAGE_DAY,USER,SYSTP,DATETIME,STARTDTE,ENDDTE,WAGE_DAY
		FROM A.TA@T2TO_MX;
	
	-- 省略自另型態TYPE rec_table IS RECORD(columns...);
	-- 直接以cursor的ROWTYPE，作為陣列內的指定物件型態
	TYPE rec_array IS TABLE OF cur_oracle%ROWTYPE INDEX BY BINARY_INTEGER;
	recs rec_array;
	now_count number := 0;
	start_time number := DBMS_UTILITY.get_time;
BEGIN
	-- 若原附表本格已有資料將其truncate
	select count(*) into chk_data from MX.STG_A_TA;
	DBMS_OUTPUT.PUT_LINE('Fetch Oracle: A.TA to Tibero: MX.STG_A_TA');
	DBMS_OUTPUT.PUT_LINE('DATA_EXCH_DATE: '||fetch_date);
	IF (chk_data >0) THEN
		execute immediate 'TRUNCATE TABLE MX.STG_A_TA';
		DBMS_OUTPUT.PUT_LINE('Truncate table ('||chk_data||' row dropped)');
	END IF;
	-- 紀錄轉檔時間
	start_time := DBMS_UTILITY.get_time;
	OPEN cur_oracle;
	
	--利用 BULK COLLECT 搭配 FORALL 將資料批次寫入表格
	LOOP
		FETCH cur_oracle BULK COLLECT into recs LIMIT fetch_limit_in;
		
		-- EXIT WHEN cur_oracle%NOTFOUND;=>%NOTFOUND為游標屬性，一筆一筆row來看，在bulk collect的狀況下不適用
		-- 假設fetch_limit設1000筆，但資料只剩600筆，那在check是否有第601筆時cur_oracle%NOTFOUND就會成立，導致這600筆都沒被寫入
		EXIT WHEN recs.COUNT = 0;
		now_count := now_count+recs.COUNT;
		FORALL i IN 1 .. recs.COUNT
			INSERT INTO /*+ parallel (8) */ MX.STG_A_TA(SAL_DATES,SAL_DATEE,SAL_TP,SAL_MIN,SAL_MAX,WAGE,WAGE_TYPE,WAGE_DAY,USER,SYSTP,DATETIME,STARTDTE,ENDDTE,WAGE_DAY,DATA_EXCH_DATE)
			VALUES(recs(i).SAL_DATES,recs(i).SAL_DATEE,recs(i).SAL_TP,recs(i).SAL_MIN,recs(i).SAL_MAX,recs(i).WAGE,recs(i).WAGE_TYPE,recs(i).WAGE_DAY,recs(i).USER,recs(i).SYSTP,recs(i).DATETIME,recs(i).STARTDTE,recs(i).ENDDTE,recs(i).WAGE_DAY,fetch_date);
		-- 將執行狀態寫入session的狀態中，讓SQL statement還正在執行中時，可以藉由查看session狀態的內容，來觀察其運行狀況
		DBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');
		DBMS_APPLICATION_INFO.SET_CLIENT_INFO('Insert data into STG_A_TA');
		COMMIT;
	END LOOP;
	COMMIT;
	CLOSE cur_oracle;
	DBMS_OUTPUT.PUT_LINE('Insert '||to_char(now_count)||' row, spend '||to_char((DBMS_UTILITY.GET_TIME - start_time)/100)||'sec');
	DBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');
	DBMS_APPLICATION_INFO.SET_CLIENT_INFO('Finished STG_A_TA');
	COMMIT;
EXCEPTION
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('!!!!! A_TA_SYNC ERROR !!!');
		DBMS_OUTPUT.PUT_LINE( 'error message: ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE || DBMS_UTILITY.FORMAT_ERROR_STACK );
END A_TA_SYNC;

END sync_oracle;