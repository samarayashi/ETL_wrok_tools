--XXX@email.com.tw
--SDM v20210820
--Date: 2022/04/25

select 'stg_ta_tablea' as stg_name, t.target_cnt, s.source_cnt, t.target_cnt - s.source_cnt as diff_cnt
from
	--Target Count
	(select count(*) as target_cnt
	from IA.stg_ta_tablea
	where DATA_EXCH_DATE=TO_DATE('2022-04-25','YYYY-MM-DD')) t

	inner join
	--Source Count
	(select count(*) as source_cnt
	from ta.tablea@T2O_IA) s

	on 1=1;