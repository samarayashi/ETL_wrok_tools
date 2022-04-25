--XXX@email.com.tw
--SDM v20210820
--Date: 2022/04/25

select count(*), merge_tmp.*
from
	(
	--Target Records
	select *
	from IA.stg_tb_tableb
	where DATA_EXCH_DATE=TO_DATE('2022-04-25','YYYY-MM-DD')

	union all
	--Source Records
	select bb,bc,bc,bd,be,bf,bg,bh,bi,bj,bk,bl,bm,TO_DATE('2022-04-25', 'YYYY-MM-DD') as DATA_EXCH_DATE
	from tb.tableb@T2O_IA

	) merge_tmp

--All Columns
group by bb,bc,bc,bd,be,bf,bg,bh,bi,bj,bk,bl,bm,DATA_EXCH_DATE

--Normal = 2
having count(*) <> 2;