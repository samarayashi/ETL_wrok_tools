-----TA_TABLEA_ENCRYPT------
insert into mx.TA_TABLEA_ENCRYPT(ENAME,IDN,SEQNO,FUNDTYPE,APNO,CHKVERSION,CHECKYYMM,PAYYM,PORCSTAT,CHGTYPE,PROCDE,EBDTE)
select '測試'||substr(ori.ENAME,3) as ENAME,decode(nvl(t1.idn_token, ori.IDN), t1.idn_token,t1.idn_token,null,null,ori.IDN, 'no_match') as IDN,ori.SEQNO,ori.FUNDTYPE,ori.APNO,ori.CHKVERSION,ori.CHECKYYMM,ori.PAYYM,ori.PORCSTAT,ori.CHGTYPE,ori.PROCDE,ori.EBDTE
	from mx.STG_TA_TABLEA ori
	left join MD.TOKEN_IDN t1 on ori.IDN = t1.idn;
commit;


-----TB_TABLEB_ENCRYPT------
insert into mx.TB_TABLEB_ENCRYPT(NAME,UBNO,MONTH,MLSEQ,VERNO,IDN_11,ACNO,RTAMT,AMT_VU,BILLKIND,PUBSCD,TXCD_L,EFDTE_L,WAGE_PL,RATE_L,IDTYPE,BIRTHDT,UBNOCK,JMARK,DEPT,SPACE6,PIID,FMK)
select '測試'||substr(ori.NAME,3) as NAME,ori.UBNO,ori.MONTH,ori.MLSEQ,ori.VERNO,ori.IDN_11,ori.ACNO,ori.RTAMT,ori.AMT_VU,ori.BILLKIND,ori.PUBSCD,ori.TXCD_L,ori.EFDTE_L,ori.WAGE_PL,ori.RATE_L,ori.IDTYPE,ori.BIRTHDT,ori.UBNOCK,ori.JMARK,ori.DEPT,ori.SPACE6,ori.PIID,ori.FMK
	from mx.STG_TB_TABLEB ori
		where month>='202001';
commit;


