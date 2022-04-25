--XXX@email.com.tw
--SDM v20210820
--Date: 2022/04/25

select *
from
	(
	--Target Records
	select *
	from bas_tb_tableb
	where DATA_EXCH_DATE=TO_DATE('2022-04-25','YYYY-MM-DD')

	union all
	--Source Records
	select ba,bb,bc,bc,bd,be,bf,bg,bh,bi,bj,bk,bl,bm,DATA_EXCH_DATE
	from stg_tb_tableb

	) merge_tmp

--All Columns
group by ba,bb,bc,bc,bd,be,bf,bg,bh,bi,bj,bk,bl,bm,DATA_EXCH_DATE

--Normal = 2
having count(*) <> 2;