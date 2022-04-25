CREATE OR REPLACE PACKAGE BODY MX.sync_oracle AS


PROCEDURE A_TA_SYNC (
	fetch_date IN STG_A_TA.data_exch_date%TYPE DEFAULT SYSDATE,
	fetch_limit_in       IN number DEFAULT 100000)
IS
	chk_data number:=0;
	CURSOR  cur_oracle IS
		SELECT /*+ parallel (8) */ SAL_DATES,SAL_DATEE,SAL_TP,SAL_MIN,SAL_MAX,WAGE,WAGE_TYPE,WAGE_DAY,USER,SYSTP,DATETIME,STARTDTE,ENDDTE,WAGE_DAY
		FROM A.TA@T2TO_MX;
	TYPE rec_array IS TABLE OF cur_oracle%ROWTYPE INDEX BY BINARY_INTEGER;
	recs rec_array;
	now_count number := 0;
	start_time number := DBMS_UTILITY.get_time;
BEGIN
	select count(*) into chk_data from MX.STG_A_TA;
	DBMS_OUTPUT.PUT_LINE('Fetch Oracle: A.TA to Tibero: MX.STG_A_TA');
	DBMS_OUTPUT.PUT_LINE('DATA_EXCH_DATE: '||fetch_date);
	IF (chk_data >0) THEN
		execute immediate 'TRUNCATE TABLE MX.STG_A_TA';
		DBMS_OUTPUT.PUT_LINE('Truncate table ('||chk_data||' row dropped)');
	END IF;
	start_time := DBMS_UTILITY.get_time;
	OPEN cur_oracle;
	LOOP
		FETCH cur_oracle BULK COLLECT into recs LIMIT fetch_limit_in;
		EXIT WHEN recs.COUNT = 0;
		now_count := now_count+recs.COUNT;
		FORALL i IN 1 .. recs.COUNT
			INSERT INTO /*+ parallel (8) */ MX.STG_A_TA(SAL_DATES,SAL_DATEE,SAL_TP,SAL_MIN,SAL_MAX,WAGE,WAGE_TYPE,WAGE_DAY,USER,SYSTP,DATETIME,STARTDTE,ENDDTE,WAGE_DAY,DATA_EXCH_DATE)
			VALUES(recs(i).SAL_DATES,recs(i).SAL_DATEE,recs(i).SAL_TP,recs(i).SAL_MIN,recs(i).SAL_MAX,recs(i).WAGE,recs(i).WAGE_TYPE,recs(i).WAGE_DAY,recs(i).USER,recs(i).SYSTP,recs(i).DATETIME,recs(i).STARTDTE,recs(i).ENDDTE,recs(i).WAGE_DAY,fetch_date);
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

PROCEDURE B_TB_SYNC (
	fetch_date IN STG_B_TB.data_exch_date%TYPE DEFAULT SYSDATE,
	fetch_limit_in       IN number DEFAULT 100000)
IS
	chk_data number:=0;
	CURSOR  cur_oracle IS
		SELECT /*+ parallel (8) */ CLASS_ID,CLASSGRP,MINWAGE,MAXWAGE,WAGE_TYPE
		FROM B.TB@T2TO_MX;
	TYPE rec_array IS TABLE OF cur_oracle%ROWTYPE INDEX BY BINARY_INTEGER;
	recs rec_array;
	now_count number := 0;
	start_time number := DBMS_UTILITY.get_time;
BEGIN
	select count(*) into chk_data from MX.STG_B_TB;
	DBMS_OUTPUT.PUT_LINE('Fetch Oracle: B.TB to Tibero: MX.STG_B_TB');
	DBMS_OUTPUT.PUT_LINE('DATA_EXCH_DATE: '||fetch_date);
	IF (chk_data >0) THEN
		execute immediate 'TRUNCATE TABLE MX.STG_B_TB';
		DBMS_OUTPUT.PUT_LINE('Truncate table ('||chk_data||' row dropped)');
	END IF;
	start_time := DBMS_UTILITY.get_time;
	OPEN cur_oracle;
	LOOP
		FETCH cur_oracle BULK COLLECT into recs LIMIT fetch_limit_in;
		EXIT WHEN recs.COUNT = 0;
		now_count := now_count+recs.COUNT;
		FORALL i IN 1 .. recs.COUNT
			INSERT INTO /*+ parallel (8) */ MX.STG_B_TB(CLASS_ID,CLASSGRP,MINWAGE,MAXWAGE,WAGE_TYPE,DATA_EXCH_DATE)
			VALUES(recs(i).CLASS_ID,recs(i).CLASSGRP,recs(i).MINWAGE,recs(i).MAXWAGE,recs(i).WAGE_TYPE,fetch_date);
		DBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');
		DBMS_APPLICATION_INFO.SET_CLIENT_INFO('Insert data into STG_B_TB');
		COMMIT;
	END LOOP;
	COMMIT;
	CLOSE cur_oracle;
	DBMS_OUTPUT.PUT_LINE('Insert '||to_char(now_count)||' row, spend '||to_char((DBMS_UTILITY.GET_TIME - start_time)/100)||'sec');
	DBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');
	DBMS_APPLICATION_INFO.SET_CLIENT_INFO('Finished STG_B_TB');
	COMMIT;
EXCEPTION
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('!!!!! B_TB_SYNC ERROR !!!');
		DBMS_OUTPUT.PUT_LINE( 'error message: ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE || DBMS_UTILITY.FORMAT_ERROR_STACK );
END B_TB_SYNC;



END sync_oracle;