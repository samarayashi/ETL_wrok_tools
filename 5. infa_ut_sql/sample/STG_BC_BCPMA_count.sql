--XXX@cht.com.tw
--SDM v20210610
--Date: 2021/06/18

select 
'STG_BC_BCPMA' as tbl --table name
,t.target_cnt
,s.source_cnt
,t.target_cnt-s.source_cnt as diff_cnt from 
(
	--Target Count
    select count(*) as target_cnt 
    from MX.STG_BC_BCPMA
    where DATA_EXCH_DATE=TO_DATE('2021-06-17','YYYY-MM-DD')
) t 
inner join (
	--Source Count
    select count(*) as source_cnt
	from BLIADM.BCPMA@MXlink
) s 
on 1=1
;