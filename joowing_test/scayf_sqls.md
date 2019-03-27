["open_new_cards"]
```sql
declare @i int 
declare @n int
declare @l int
declare @member_no varchar(20) 
declare @h varchar(10)
declare @max varchar(20)

set @h='B'
set @l=100000
set @n= $number$
select @max = max(card_id) from  dbo.t_rm_vip_info where card_id like @h+'%' and len(card_id)=len(@l)+len(@h)
if @max is null 
begin
  set @max = convert(varchar(10),@l)
end 
else
begin
  set @max = substring(@max,len(@h)+1,len(@l))
end
set @i=1
while @i <=@n  
  BEGIN
    set @member_no=@h+convert(varchar(10),convert(int,@max)+@i)
    insert into t_rm_vip_info(
    card_id,
    card_no,
    card_type,
    vip_name,
    branch_no,
    birthday,
    vip_start_date,
    vip_end_date,
    sav_start_date ,
    sav_end_date ,
    use_num,
    card_status,
    oper_date,
    oper_id )
    values(@member_no,
           @member_no,
           '10',
           '预开卡',
           '0000',
           '1990-01-01',
           '1990-01-01',
           '2030-01-01',
           '1990-01-01',
           '2030-01-01',
            99999,
            '0',
           '1990-01-01',
           '1001'
           )
    set @i=@i+1
  end
select @member_no member_id
```
["find_max_member_no"]
```sql
DECLARE @h VARCHAR(8) 
SET @h='$prefix$'

SELECT MAX(Card_id) FROM [dbo].[t_rm_vip_info]
WHERE card_id LIKE @h+'%'
```
["find_user_by_phone"]
```sql
SELECT top 1
a.card_id AS member_no,
a.card_no AS member_id,
a.vip_name AS name,
CONVERT(VARCHAR(10),a.birthday,120) birthday,
'$mobile$' AS mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$mobile$' or a.vip_tel = '$mobile$')
and a.card_status='0' 
and a.card_type in ('10','5','wx')
order by a.now_acc_num desc,a.oper_date desc
```
["find_all_user_by_phone"]
```sql
select
a.card_id AS member_no,
a.card_no AS member_id,
a.vip_name AS name,
CONVERT(VARCHAR(10),a.birthday,120) birthday,
'$mobile$' AS mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$mobile$' or a.vip_tel = '$mobile$')
and a.card_status='0'
and a.card_type in ('10','5','wx')
order by a.now_acc_num desc,a.oper_date desc
```
["find_user_by_member_no"]
```sql
SELECT top 1
a.card_id AS member_no,
a.card_no AS member_id,
a.vip_name AS name,
CONVERT(VARCHAR(10),a.birthday,120) birthday,
case when len(a.mobile)=11 then a.mobile else a.vip_tel end mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
a.card_id='$member_no$'
and a.card_status='0'
and a.card_type in ('10','5','wx')
```
["create_user"]
```sql
declare @member_no varchar(30)  --会员编号

select top 1 @member_no = card_id
 FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$user.mobile$' or a.vip_tel = '$user.mobile$')
and a.card_status='0'
and a.card_type in ('10','5','wx')
order by a.now_acc_num desc,a.oper_date desc

if @member_no is null
  begin
    set  @member_no=  '$user.member_no$'
	
    select top 1 @member_no = card_id  FROM
    dbo.t_rm_vip_info AS a
    where card_id=@member_no and a.mobile is null
    
    if @member_no is not null
      begin
        update t_rm_vip_info 
           set
        vip_name=convert(varchar(8),'$user.name$'),
        vip_sex= case '$user.sex$' when '1' then '男' when '2' then '女'  else '' end,
        oper_date=getdate(),
        vip_start_date=getdate(),
        sav_start_date=getdate(),
        birthday='$user.birthday.try(&:to_s)$',
        $user.address ? "vip_add=convert(varchar(80),'" + user.address + "')," : ''$
        mobile='$user.mobile$'
        where card_id = @member_no
      end
  end
select @member_no member_no,@member_no member_id
```
["modify_user"]
```sql
update t_rm_vip_info
   set vip_name=convert(varchar(8),'$user.name$'),
       birthday = '$user.birthday.try(&:to_s)$',
       $user.address ? "vip_add=convert(varchar(80),'" + user.address + "')," : ''$
       vip_sex= case '$user.sex$' when '1' then '男' when '2' then '女'  else '' end,
       modify_date = getdate()
 where card_id = '$user.member_no$'
```
["modify_register_user_guide_no"]
```sql
declare @guide_no varchar(32)  --写入的导购工号

select top 1 @guide_no = a.sale_id
 FROM
dbo.t_rm_saleman AS a
WHERE a.sale_id='$user.guide_no$'

if @guide_no is not null
begin

update t_rm_vip_info   
   set $user.guide_no.nil? ? '' : "oper_id=convert(varchar(4),'" + user.guide_no + "')," + "sale_id=convert(varchar(4),'" + user.guide_no + "')," $
     modify_date = getdate()
 where card_id = '$user.member_no$' 
   AND (sale_id IS NULL OR sale_id='');

end
```
["modify_register_user_referee_shop"]
```sql
update t_rm_vip_info
   set $user.referee_shop ? "branch_no= left('" + user.referee_shop + "',4)," : ''$
       modify_date = getdate()
 where card_id = '$user.member_no$'
```
["find_exist_phones"]
```sql
select case when isnull(mobile,'')='' then vip_tel else mobile end AS mobile from t_rm_vip_info
where mobile in ('$mobiles.join("', '")$') or vip_tel in ('$mobiles.join("', '")$')
```
["find_score"]
```sql
select convert(float, now_acc_num) score
  from t_rm_vip_info
 where card_id = '$member_no$'
```
["modify_score"]
```sql
declare @jf float
declare @card_id varchar(30)
declare @card_no varchar(30)
declare @card_type varchar(10)
select top 1 @jf = convert(float, now_acc_num),
       @card_id = card_id,
       @card_no = card_no,
       @card_type = card_type
  from t_rm_vip_info
 where card_id = '$score_detail.member_no$'
begin
  insert into t_rm_vip_acclist(
    card_id,
    card_no,
    card_type,
    branch_no,
    oper_type,
    db_flag,
    acc_num,
    oper_des,
    oper_id,
    ope_date,
    memo
  ) values (
    @card_id,
    @card_no,
    @card_type,
    '0000',
    '$score_detail.score > 0 ? '2' : '1'$',
    '$score_detail.score > 0 ? '1' : '-1'$',
    '$score_detail.score.abs.to_s$',
    convert(varchar(60),'$score_detail.description$'),
    '1001',
    '$score_detail.created_at.strftime('%F %T')$',
    '$score_detail.score > 0 ? 'App增加积分' : 'App扣减积分'$'
  )
end
```
["find_score_details"]
```sql
select card_id member_no,
       ope_date created_at,
       case when oper_type = 1 then convert(float, 0 - abs(acc_num)) else convert(float, acc_num) end score,
       case when oper_des is null then memo else oper_des end description
   from t_rm_vip_acclist
  where card_id = '$member_no$'
    and ope_date >= '$begin_time.strftime('%F %T')$'
    and ope_date <= '$end_time.strftime('%F %T')$'
```
["find_prices"]
```sql
select code,
       case when len(ltrim(rtrim(shop_code))) = 4 then ltrim(rtrim(shop_code)) + '01' else ltrim(rtrim(shop_code)) end  shop_code,
       max(original_price) as original_price,
       max(member_price) as member_price,
       convert(float, max(price)) as price
  from (
    select replace(ltrim(rtrim(i.item_no)), CHAR(10), '') code,
           ltrim(rtrim(pr.branch_no)) shop_code,
           convert(float, pr.sale_price) original_price,
           convert(float,case when pr.vip_price=0 then pr.sale_price else pr.vip_price end) member_price,
           convert(float,case when pl.price is null then case when pr.vip_price=0 then pr.sale_price else pr.vip_price end else pl.price end) price
      from t_pc_branch_price pr
 left join t_bd_item_info i   on pr.item_no = i.item_no
 left join (select a.plan_no,a.begin_date,a.end_date,a.rule_no,b.rule_val item_no,c.rule_val price, d.branch_no,
                   case when a.stop_date is null then a.end_date else a.stop_date end stop_date,
            row_number() over (partition by d.branch_no,b.rule_val order by a.oper_date desc) rn
              from  t_rm_plan_master a 
              inner join dbo.t_rm_plan_detail b on a.plan_no=b.plan_no and b.rule_para='ITEM1' 
              inner join dbo.t_rm_plan_detail c on b.plan_no=c.plan_no and c.rule_para='R1' and b.row_id=c.row_id 
              inner join dbo.t_rm_plan_branch d on a.plan_no=d.plan_no) pl
        on pr.item_no = pl.item_no and pr.branch_no=pl.branch_no
       and pl.begin_date < getdate() and pl.end_date > getdate()
       and pl.stop_date > getdate()
       and pl.rule_no = 'PS' 
       and rn=1
     where i.item_no in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
       and pr.sale_price > 0
       and i.status='1'
  ) p
  group by code, shop_code
```
["find_stocks"]
```sql
select code,
       shop_code,
       max(stock) as stock
  from (
      select replace(ltrim(rtrim(i.item_no)), CHAR(10), '') code,
             case when len(ltrim(rtrim(s.branch_no))) = 4 then ltrim(rtrim(s.branch_no)) + '01' else ltrim(rtrim(s.branch_no)) end shop_code,
             convert(int, s.stock_qty * $rat$) stock
         from t_im_branch_stock s, t_bd_item_info i
        where s.item_no = i.item_no and i.status='1'
             and i.item_no in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
  ) pss
group by code, shop_code
```
["find_member_order_histories"]
```sql
select a.*,order_total from
(select card_id member_no,
                rtrim(flow_no) order_no,
                branch_no  shop_code,
                rtrim(flow_no) + rtrim(flow_id) order_item_no,
                rtrim(item_no) code,
                convert(float, sale_price) price,
                convert(int, case sell_way  when 'B' then -1*sale_qnty else sale_qnty end) num,
                convert(float,case sell_way  when 'B' then -1*sale_money else sale_money end ) total,
                oper_date oper_time
           from  t_rm_saleflow c
          where oper_date >= '$begin_time.strftime('%F %T')$'
            and oper_date <= '$end_time.strftime('%F %T')$'
            and card_id= '$member_no$') a
inner join
(select rtrim(flow_no) order_no,
                convert(float, sum(case sell_way  when 'B' then -1*sale_money else sale_money end)) order_total
           from  t_rm_saleflow c
          where oper_date >= '$begin_time.strftime('%F %T')$'
            and oper_date <= '$end_time.strftime('%F %T')$'
            and card_id= '$member_no$'
 group by rtrim(flow_no)) b on a.order_no=b.order_no
```
["find_order_by_order_no"]
```sql
select a.*,order_total from
(select card_id member_no,
                rtrim(flow_no) order_no,
                branch_no  shop_code,
                rtrim(flow_no) + rtrim(flow_id) order_item_no,
                rtrim(item_no) code,
                convert(float, sale_price) price,
                convert(int, case sell_way  when 'B' then -1*sale_qnty else sale_qnty end) num,
                convert(float,case sell_way  when 'B' then -1*sale_money else sale_money end ) total,
                oper_date oper_time
           from  t_rm_saleflow
          where rtrim(flow_no) = '$order_no$'
            and branch_no = '$shop_code$') a
inner join
(select rtrim(flow_no) order_no,
                convert(float, sum(case sell_way  when 'B' then -1*sale_money else sale_money end)) order_total
           from  t_rm_saleflow
          where rtrim(flow_no) = '$order_no$'
            and branch_no = '$shop_code$'
 group by rtrim(flow_no)) b on a.order_no=b.order_no
```
["add_coupon"]
```sql
DECLARE @giftcert_no     varchar(32) --优惠券号
DECLARE @gift_type       varchar(4) --优惠券类型
DECLARE @gift_type_existed     varchar(4)
DECLARE @raiseErrorCode nvarchar(16)

SET @giftcert_no='$code$'
SET @gift_type='$serial_no$'
SET @raiseErrorCode = CONVERT(nvarchar(64),'50005')


--为了判断券类型编号在线下库是否已经存在，防止创建出券类型有误的数据
SELECT @gift_type_existed=a.cert_code
  from [dbo].[t_rm_giftcert_baseinfo] AS a
 WHERE a.cert_code=@gift_type


IF @gift_type_existed is NOT NULL
    BEGIN
        INSERT INTO t_rm_gift_certificate
        (
        [giftcert_no],[gift_type],[gift_money],
        [oper_id],[oper_date],[status],
        [begin_date],[end_date],
        [send_branch],cert_code,
        [card_id]
        )
        VALUES
        (
        @giftcert_no,'0',
        '$price.to_s$',
        '1001',getdate(),'1',
        '$valid_from.to_s$ 00:00:00.000','$valid_to.to_s$ 23:59:59.997',
        '0000',@gift_type,
        '$member_no$'
        )
        SELECT @giftcert_no
    END
ELSE
  RAISERROR('%s INVALID ID: The serial_no does not exist. Send coupons failure!',16,1, @raiseErrorCode);
```
["use_coupon"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
DECLARE @giftcert_no_exist     char(20) --优惠券号

SET @giftcert_no='$code$'

SELECT @giftcert_no_exist=a.giftcert_no
  FROM t_rm_gift_certificate a
 WHERE a.giftcert_no=@giftcert_no
  AND (a.status='1' OR a.status='9')


IF  @giftcert_no_exist IS NOT null
  BEGIN
    UPDATE t_rm_gift_certificate
    SET status='3',pay_oper='1001',pay_date=GETDATE(),memo='致维订单_'+'$order_no$'+'_用券'
    WHERE giftcert_no=@giftcert_no
    SELECT 1
  END
ELSE
  SELECT 0
```
["lock_coupon"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
DECLARE @giftcert_no_exist     char(20) --优惠券号

SET @giftcert_no='$code$'

SELECT @giftcert_no_exist=a.giftcert_no
  FROM t_rm_gift_certificate a
 WHERE a.giftcert_no=@giftcert_no
   AND (a.status='1' OR a.status='2')

IF  @giftcert_no_exist IS NOT null
  BEGIN
    UPDATE t_rm_gift_certificate
    SET status='2',memo='券锁定时间:'+ CONVERT(VARCHAR(19),GETDATE(),120)
    WHERE giftcert_no=@giftcert_no
    SELECT 1
  END
ELSE
  SELECT 0
```
["unlock_coupon"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
DECLARE @giftcert_no_exist     char(20) --优惠券号

SET @giftcert_no='$code$'

SELECT @giftcert_no_exist=a.giftcert_no
  FROM t_rm_gift_certificate a
 WHERE a.giftcert_no=@giftcert_no
   AND (a.status='1' OR a.status='2')

IF  @giftcert_no_exist IS NOT null
  BEGIN
    UPDATE t_rm_gift_certificate
    SET status='1',memo='券解锁时间:'+ CONVERT(VARCHAR(19),GETDATE(),120)
    WHERE giftcert_no=@giftcert_no
  END
ELSE
  SELECT '此优惠券线下不存在或不是可用状态，券解锁失败！'  AS  return_code
```
["find_coupons_by_member"]
```sql
DECLARE @card_id     varchar(20) --会员号
    SET @card_id='$member_no$'

SELECT
rtrim(a.card_id) AS member_no,
rtrim(a.giftcert_no) AS id,
rtrim(a.giftcert_no) AS code,
rtrim(a.cert_code) AS serial_no,
CASE a.status
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status,
a.begin_date valid_from,
a.end_date valid_to,
a.pay_date used_at,
a.oper_date created_at,

rtrim(b.memo) AS 'name',
CASE b.limit_goodstype WHEN 'I' THEN '单品券'  WHEN 'C' THEN '品类券'  WHEN 'B' THEN '品牌券' ELSE '未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a
INNER JOIN t_rm_giftcert_baseinfo b on a.cert_code=b.cert_code AND a.card_id=@card_id
ORDER BY a.oper_date ASC;
```
["find_usable_coupons_by_member"]
```sql
DECLARE @card_id     varchar(20) --会员号
    SET @card_id='$member_no$'

SELECT
rtrim(a.card_id) AS member_no,
rtrim(a.giftcert_no) AS id,
rtrim(a.giftcert_no) AS code,
rtrim(a.cert_code) AS serial_no,
CASE a.status
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status,
a.begin_date valid_from,
a.end_date valid_to,
a.pay_date used_at,
a.oper_date created_at,

rtrim(b.memo) AS 'name',
CASE b.limit_goodstype WHEN 'I' THEN '单品券'  WHEN 'C' THEN '品类券'  WHEN 'B' THEN '品牌券' ELSE '未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a
INNER JOIN t_rm_giftcert_baseinfo b on a.cert_code=b.cert_code AND a.card_id=@card_id
WHERE a.status='1' AND a.end_date>getdate()
ORDER BY a.end_date ASC,a.oper_date ASC;
```
["find_coupon_by_id"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
    SET @giftcert_no='$id$'

SELECT
rtrim(a.card_id) AS member_no,
rtrim(a.giftcert_no) AS id,
rtrim(a.giftcert_no) AS code,
rtrim(a.cert_code) AS serial_no,
CASE a.status
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status,
a.begin_date valid_from,
a.end_date valid_to,
a.pay_date used_at,
a.oper_date created_at,

rtrim(b.memo) AS 'name',
CASE b.limit_goodstype WHEN 'I' THEN '单品券'  WHEN 'C' THEN '品类券'  WHEN 'B' THEN '品牌券' ELSE '未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a
INNER JOIN t_rm_giftcert_baseinfo b on a.cert_code=b.cert_code AND a.giftcert_no=@giftcert_no;
```
["find_coupon_by_code"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
    SET @giftcert_no='$code$'

SELECT
rtrim(a.card_id) AS member_no,
rtrim(a.giftcert_no) AS id,
rtrim(a.giftcert_no) AS code,
rtrim(a.cert_code) AS serial_no,
CASE a.status
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status,
a.begin_date valid_from,
a.end_date valid_to,
a.pay_date used_at,
a.oper_date created_at,

rtrim(b.memo) AS 'name',
CASE b.limit_goodstype WHEN 'I' THEN '单品券'  WHEN 'C' THEN '品类券'  WHEN 'B' THEN '品牌券' ELSE '未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a
INNER JOIN t_rm_giftcert_baseinfo b on a.cert_code=b.cert_code AND a.giftcert_no=@giftcert_no;
```
["modify_coupon_member_no"]
```sql
UPDATE t_rm_gift_certificate
   SET card_id='$new_member_no$'
 WHERE card_id='$old_member_no$';
```
["modify_level"]
```sql
update t_rm_vip_info
set card_type = '$user.level$'
where card_id = '$user.member_no$'
```
["create_order"]
```sql
--创建订单接口
--1、先把韩冰传过来的订单数据存入内存临时表
DECLARE @tmp_table TABLE(
  id                  int NOT NULL IDENTITY(1,1),
  freight             numeric(18,2),
  sheet_no            nvarchar(50),
  orderman            nvarchar(50),
  ordertel            nvarchar(50),
  item_no             nvarchar(50),
  price               numeric(16,4),
  oper_date           datetime,    
  real_qty            numeric(16,4),
  branch_no           nvarchar(50),
  address             varchar(200), 
  deal_type           nvarchar(4),  
  card_id             nvarchar(50),
  memo                nvarchar(255)
)

DECLARE @sheet_no            nvarchar(50) --订单号（致维提货券号）。校验线下是否已经存在，不能一笔订单多次创建到线下库 
DECLARE @zw_item_no_num      INT 
DECLARE @sh_item_no_num      INT
DECLARE @price_s_num         INT 
DECLARE @real_qty_num        INT 
DECLARE @branch_no           nvarchar(50)  --门店编号必须线下库存在
DECLARE @card_id             nvarchar(50)  --校验下单会员号线上是否存在
DECLARE @deal_type           nvarchar(4)  


DECLARE @dealtime     datetime
SET @dealtime=CONVERT(VARCHAR(24),GETDATE(),121)


$order.order_items.map{ |i| "INSERT INTO @tmp_table(sheet_no, orderman, ordertel, item_no, price, oper_date, real_qty, branch_no, address, deal_type, card_id, freight, memo) VALUES ('#{i.proof_code}', '#{order.address ? order.address[:receiver].to_s : order.member_name.to_s}', '#{order.address ? order.address[:phone].to_s : order.phone.to_s}', '#{i.code}', '#{i.price.to_s}', '#{order.trade_time.try { |t| Time.parse(t).strftime('%Y-%m-%d %H:%M:%S') } }', '#{i.num.to_s}', '#{order.shop_code}', '#{order.address && order.address[:address].to_s}', '#{order.delivery_method == 2 ? 0.to_s : order.delivery_method.to_s}', '#{order.member_no}', '#{order.freight.to_s}', '#{order.order_no}')"}.join("\n")$

-- 把运费摊到第一个商品价格上
UPDATE tt
   SET tt.price = (CASE WHEN tt.freight>0 THEN ROUND((tt.price+tt.freight/tt.real_qty),2) ELSE  tt.price END )
  FROM @tmp_table tt
 WHERE id=1

-- 把微商城提货方式为6（自动完成）的订单处理成物流单
UPDATE tt
    SET tt.deal_type = (CASE WHEN tt.deal_type = '6' THEN '1' ELSE tt.deal_type END)
  FROM @tmp_table tt

--为了判断订单号是否已经存在，防止重复创建
SELECT @sheet_no=a.sheet_no FROM dbo.t_order_bill_weixin a
INNER JOIN 
(
SELECT DISTINCT b.sheet_no
  from @tmp_table AS b
) dx on dx.sheet_no=a.sheet_no

--为了判断订单商品线下库是否已经存在
SELECT @zw_item_no_num=count(b.item_no),@sh_item_no_num=count(c.item_no) 
  FROM
(
SELECT DISTINCT a.item_no
  from @tmp_table AS a
) b 
LEFT JOIN dbo.t_bd_item_info  c on c.item_no=b.item_no

--为了判断订单商品是否价格都大于等于0
SELECT @price_s_num=COUNT(1)
  FROM @tmp_table AS a
 WHERE CONVERT(FLOAT,a.price)<0

--为了判断订单项商品数量是否大于0
SELECT @real_qty_num=COUNT(1)
  FROM @tmp_table AS a
 WHERE CONVERT(FLOAT,a.real_qty)<=0

--为了判断取货方式是否为自提或物流
SELECT @deal_type=(CASE WHEN (dx.deal_type='1' OR dx.deal_type='0') THEN 'Y' ELSE 'N' END ) FROM 
(
SELECT DISTINCT b.deal_type
  from @tmp_table AS b
) dx 

--为了判断下单门店在线下库是存在的
SELECT @branch_no=a.branch_no FROM dbo.t_bd_branch_info a
INNER JOIN 
(
SELECT DISTINCT b.branch_no
  from @tmp_table AS b
) dx on dx.branch_no=a.branch_no

--为了判断订单下单会员号线下库是否存在
SELECT @card_id=a.card_id FROM dbo.t_rm_vip_info a
INNER JOIN
(
SELECT DISTINCT b.card_id
  from @tmp_table AS b
) dx  ON a.card_id=dx.card_id



IF @sheet_no is NULL
  BEGIN
    IF @zw_item_no_num=@sh_item_no_num
      BEGIN
        IF @price_s_num=0
          BEGIN
            IF @real_qty_num=0
              BEGIN
                IF @branch_no is NOT NULL
                  BEGIN
                    IF @card_id is NOT NULL
                      BEGIN
                        IF @deal_type='Y'
                          BEGIN
                            begin tran T1
                            INSERT INTO [dbo].[t_order_bill_weixin]
                            (
                            [sheet_no],[orderman],[ordertel],[item_no],
                            [item_size],
                            [price],[oper_date],[real_qty],
                            [openid],
                            [branch_no],[shopid],
                            [IsDownload],[pay_type],[status],
                            [deal_type],
                            [source_id],
                            [send_address],[memo],
                            [modify_oper],[item_name],
                            [address],
                            [ver],
                            [card_id],
                            [paystatus],[status_upflag],[dealtime]
                            )
                            select     
                            a.sheet_no,a.orderman,a.ordertel,a.item_no,
                            '',
                            a.price,a.oper_date,a.real_qty,
                            '',
                            LEFT(a.branch_no,4),LEFT(a.branch_no,4),
                            '0','2','0',
                            a.deal_type,
                            '',
                            a.address,a.memo,
                            '','',
                            a.address,
                            '2',
                            a.card_id,
                            '1','',@dealtime    
                            from @tmp_table AS a    
                            commit tran T1
                            SELECT 'OK'  AS  return_code
                          END
                        ELSE 
                          SELECT '订单取货方式不符合要求' AS  return_code
                      END
                    ELSE 
                      SELECT '订单下单会员号线下库不存在' AS  return_code
                  END
                ELSE 
                  SELECT '订单下单门店不存在' AS  return_code
              END
            ELSE 
              SELECT '有商品数量不是正数' AS  return_code
          END
        ELSE 
          SELECT '有商品价格小于0' AS  return_code
      END 
    ELSE
      SELECT '有商品在线下库不存在'  AS  return_code
  END
ELSE 
  SELECT '该订单线下库已存在，请勿重复创建'  AS  return_code
```
["find_order_state_by_proof_codes"]
```sql
select 
a.sheet_no code,
case when a.IsDownload ='0' and a.status='0' then 'init' when a.IsDownload ='1' and a.status='2' then 'cancel' else 'finished' end state,
b.oper_date shopping_time
from  dbo.t_order_bill_weixin  a
LEFT JOIN  dbo.t_rm_payflow  b  ON a.source_id=b.flow_no
where  a.sheet_no in ($codes$)
GROUP BY a.sheet_no,a.IsDownload,a.status,b.oper_date;
```
["cancel_order"]
```sql
DECLARE @state char(1)
DECLARE @s INT

SET @s=0

SELECT
  @state=a.status
FROM
dbo.t_order_bill_weixin AS a
WHERE
a.sheet_no= '$proof_code$'
GROUP BY a.sheet_no,a.status

IF @state is NOT NULL
  BEGIN
    IF  @state='0'
      BEGIN 
      SET ANSI_WARNINGS  OFF
        UPDATE a
           SET a.IsDownload='1',a.status='2',a.status_upflag='1',a.memo=memo+'-c'
          FROM dbo.t_order_bill_weixin  AS a
         WHERE a.sheet_no='$proof_code$'
      SET ANSI_WARNINGS  ON

        SELECT 'OK'  AS  return_code

      END 
    ELSE
      SELECT CASE WHEN @state='1' THEN '订单已在门店提货，不允许取消' 
                  WHEN @state='2' THEN '订单之前已被取消，请勿重复操作' 
           ELSE  '订单当前为未知状态，不能取消' END AS  return_code 
  END 
ELSE 
  SELECT '找不到对应的订单' AS  return_code
```
["modify_order_member_no"]
```sql
DECLARE @new_member_no  VARCHAR(64)

SELECT @new_member_no=a.card_id FROM  dbo.t_rm_vip_info  a
WHERE  a.card_id='$new_member_no$'

IF @new_member_no IS NOT NULL
BEGIN
  UPDATE 
    dbo.t_order_bill_weixin
  SET 
    card_id='$new_member_no$' 
  WHERE 
    card_id='$old_member_no$'
  AND IsDownload='0'
  AND status='0'
END
```
["check_member_no_exists"]
```sql
DECLARE @ss VARCHAR(64)

SELECT @ss=card_id 
  FROM dbo.t_rm_vip_info
 WHERE card_id='$member_no$'
   AND card_status='0'

IF @ss IS NOT NULL
BEGIN 
SELECT 'ok'  AS result
END 
ELSE 
SELECT '会员不存在'  AS result
```
