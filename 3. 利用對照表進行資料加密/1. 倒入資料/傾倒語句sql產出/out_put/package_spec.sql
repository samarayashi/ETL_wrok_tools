CREATE OR REPLACE PACKAGE MX.sync_oracle AS
	PROCEDURE A_TA_SYNC(fetch_date IN STG_A_TA.data_exch_date%TYPE DEFAULT SYSDATE,fetch_limit_in IN number DEFAULT 100000);
	PROCEDURE B_TB_SYNC(fetch_date IN STG_B_TB.data_exch_date%TYPE DEFAULT SYSDATE,fetch_limit_in IN number DEFAULT 100000);
END sync_oracle;