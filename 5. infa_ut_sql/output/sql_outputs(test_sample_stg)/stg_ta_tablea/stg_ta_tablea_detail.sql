--XXX@email.com.tw
--SDM v20210820
--Date: 2022/04/25

select count(*), merge_tmp.*
from
	(
	--Target Records
	select *
	from IA.stg_ta_tablea
	where DATA_EXCH_DATE=TO_DATE('2022-04-25','YYYY-MM-DD')

	union all
	--Source Records
	select a,b,c,d,e,f,g,h,i,j,k,l,TO_DATE('2022-04-25', 'YYYY-MM-DD') as DATA_EXCH_DATE
	from ta.tablea@T2O_IA

	) merge_tmp

--All Columns
group by a,b,c,d,e,f,g,h,i,j,k,l,DATA_EXCH_DATE

--Normal = 2
having count(*) <> 2;