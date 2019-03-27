["find_user_by_phone"]
```sql
SELECT top 1
a.card_no AS member_no,
a.vip_name AS name,
a.birthday ,
'$mobile$' AS mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$mobile$' or a.vip_tel = '$mobile$')
and a.card_status='0' 
and a.card_no not like '66%'
order by a.oper_date desc
```
["find_all_user_by_phone"]
```sql
select 
a.card_no AS member_no,
a.vip_name AS name,
a.birthday ,
'$mobile$' AS mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$mobile$' or a.vip_tel = '$mobile$')
and a.card_status='0'
and a.card_no not like '66%'
order by a.oper_date desc
```
["find_user_by_member_no"]
```sql
SELECT top 1
a.card_no AS member_no,
a.vip_name AS name,
a.birthday ,
case when len(a.mobile)=11 then a.mobile else a.vip_tel end mobile,
case a.vip_sex when '男' then '1' when '女' then '2' else '3' end AS sex  -- 男 女
FROM
dbo.t_rm_vip_info AS a
WHERE
a.card_no='$member_no$'
and a.card_status='0'
```
["create_user"]
```sql
declare @member_no varchar(30)  --会员编号

select top 1 @member_no = card_no
 FROM
dbo.t_rm_vip_info AS a
WHERE
(a.mobile = '$user.mobile$' or a.vip_tel = '$user.mobile$')
and a.card_status='0'
and a.card_no not like '66%'
order by a.oper_date desc

if @member_no is null
  begin

set  @member_no=  '$user.member_no$'
insert into t_rm_vip_info(
card_id,
card_no,
card_type,
vip_name,
vip_sex,
card_status,
oper_date,
vip_start_date,
vip_end_date,
sav_start_date ,
sav_end_date ,
birthday,
mobile,
oper_id,
$user.referee_shop ? "branch_no, ": '' $
use_num )
values(@member_no,
       @member_no,
       '0',
       convert(varchar(8),'$user.name$'),
       case '$user.sex$' when '1' then '男' when '2' then '女'  else '' end,
        '0',
       getdate(),
       getdate(),
        '2020-01-01',
         getdate(),
        '2020-01-01',
       '$user.birthday.try(&:to_s)$',
       '$user.mobile$' ,
       $user.guide_no ? "'" + user.guide_no + "'," : "'0000',"$ 
       $user.referee_shop ? "'" + user.referee_shop + "'," : ''$
       99999
       );
insert into t_rm_vip_motherhood_identity(
card_id,
baby_sex,
baby_birthday_date )
values(
@member_no,
case '$user.sex$' when '1' then '1' when '2' then '2'  else '3' end,
'$user.birthday.try(&:to_s)$')
end
select @member_no member_no
```
["modify_user"]
```sql
update t_rm_vip_info
   set vip_name = LEFT('$user.name$',4),
       birthday = '$user.birthday.try(&:to_s)$',
       $user.referee_shop ? "branch_no = '" + user.referee_shop + "'," : ''$
       vip_sex= case '$user.sex$' when '1' then '男' when '2' then '女'  else '' end,
       modify_date = getdate()
 where card_no = '$user.member_no$'
```
["find_exist_phones"]
```sql
select case when isnull(mobile,'')='' then vip_tel else mobile end AS mobile from t_rm_vip_info
where mobile in ('$mobiles.join("', '")$') or vip_tel in ('$mobiles.join("', '")$')
and card_no not like '66%'
```
["find_score"]
```sql
select convert(float, now_acc_num) score
  from t_rm_vip_info
 where card_no = '$member_no$'
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
 where card_no = '$score_detail.member_no$'
begin
  insert into t_rm_vip_acclist(
    card_id,
    card_no,
    card_type,
    branch_no,
    oper_type,
    acc_num,
    oper_des,
    oper_id,
    ope_date,
    memo
  ) values (
    @card_id,
    @card_no,
    @card_type,
    '000101',
    '$score_detail.score > 0 ? '0' : '1'$',
    '$score_detail.score.abs.to_s$',
    LEFT('$score_detail.description$',100),
    '1001',
    '$score_detail.created_at.strftime('%F %T')$',
    '$score_detail.score > 0 ? 'App增加积分' : 'App扣减积分'$'
  )
   $score_detail.score < 0 ? "update t_rm_vip_info set now_acc_num = @jf + " + score_detail.score.to_s + ", dec_num = dec_num + " + score_detail.score.abs.to_s + " where card_no = '" + score_detail.member_no + "'" : ''$
end
```
["find_score_details"]
```sql
select card_no member_no,
       ope_date created_at,
       case when oper_type = 1 then convert(float, 0 - abs(acc_num)) else convert(float, acc_num) end score,
       case when oper_des is null then memo else oper_des end description
   from t_rm_vip_acclist
  where card_no = '$member_no$'
    and ope_date >= '$begin_time.strftime('%F %T')$'
    and ope_date <= '$end_time.strftime('%F %T')$'
```
["find_prices"]
```sql
select code,
       shop_code,
       max(original_price) as original_price,
       max(member_price) as member_price,
       convert(float, max(price)) as price
  from (
    select replace(ltrim(rtrim(pr.item_no)), CHAR(10), '') code,
           ltrim(rtrim(pr.branch_no)) shop_code,
           convert(float, pr.sale_price) original_price,
           convert(float,case when pr.vip_price=0 then pr.sale_price else  pr.vip_price end) member_price,
           convert(float,case when pl.price is null then case when pr.vip_price=0 then pr.sale_price else pr.vip_price end else pl.price end) price
      from t_pc_branch_price pr
 left join t_bd_item_info i
        on pr.item_no = i.item_no 
 left join (select pl.*,pm.oper_branch,
                   case when pm.stop_date is null then pl.end_date else pm.stop_date end stop_date
             from  t_rm_plan_master pm inner join t_rm_plan_flow pl on pm.plan_no=pl.plan_no) pl
        on pr.item_no = pl.item_no
       and (pl.oper_branch='ALL' or pl.branch_no like '%|' + pr.branch_no + '|%')
       and pl.begin_date < getdate()
       and pl.end_date > getdate()
       and pl.stop_date > getdate()
       and pl.rule_no = 'PSI'
	   and (pl.limit_vip is null or pl.limit_vip =0 or pl.limit_vip >10)  
     where pr.item_no in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
       and pr.sale_price > 0 
       and i.status='1'
  ) p
group by code, shop_code
```
["find_stocks"]
```sql
SELECT
ltrim(rtrim(kc.item_no)) code,
kc.branch_no shop_code,
convert(int, sum(kc.stock_qty) * $rat$) stock
FROM
dbo.t_im_branch_stock AS kc
inner join t_bd_item_info b ON kc.item_no = b.item_no
where kc.item_no in ('$codes.join("', '")$') 
and b.status='1' 
group by ltrim(rtrim(kc.item_no)) , kc.branch_no
```
["find_member_order_histories"]
```sql
select a.*,order_total from
(select card_no member_no,
                ltrim(rtrim(flow_no)) order_no,
                branch_no  shop_code,
                ltrim(rtrim(flow_no)) + ltrim(rtrim(flow_id)) order_item_no,
                ltrim(rtrim(item_no)) code,
                convert(float, sale_price) price,
                convert(int, sale_qnty) num,
                convert(float,Sale_money) total,
                oper_date oper_time
           from  t_rm_saleflow c
          where oper_date >= '$begin_time.strftime('%F %T')$'
            and oper_date <= '$end_time.strftime('%F %T')$'
            and card_no= '$member_no$') a
inner join
(select ltrim(rtrim(flow_no)) order_no,
                convert(float, sum(Sale_money)) order_total
           from  t_rm_saleflow c
          where oper_date >= '$begin_time.strftime('%F %T')$'
            and oper_date <= '$end_time.strftime('%F %T')$'
            and card_no= '$member_no$'
 group by ltrim(rtrim(flow_no))) b on a.order_no=b.order_no
```
["find_order_by_order_no"]
```sql
select a.*,order_total from
(select card_no member_no,
                ltrim(rtrim(flow_no)) order_no,
                branch_no  shop_code,
                ltrim(rtrim(flow_no)) + ltrim(rtrim(flow_id)) order_item_no,
                ltrim(rtrim(item_no)) code,
                convert(float, sale_price) price,
                convert(int, sale_qnty) num,
                convert(float,Sale_money) total,
                oper_date oper_time
           from  t_rm_saleflow
          where ltrim(rtrim(flow_no)) = '$order_no$'
            and branch_no = '$shop_code$') a
inner join
(select ltrim(rtrim(flow_no)) order_no,
                convert(float, sum(Sale_money)) order_total
           from  t_rm_saleflow
          where ltrim(rtrim(flow_no)) = '$order_no$'
            and branch_no = '$shop_code$'
 group by ltrim(rtrim(flow_no))) b on a.order_no=b.order_no
```
["find_order_by_condition"]
```sql
select * from
(select s.card_no member_no,
                ltrim(rtrim(flow_no)) order_no,
                s.branch_no  shop_code,
                s.oper_date oper_time,
                convert(float, sum(Sale_money)) total
           from  t_rm_saleflow s
  left join t_rm_vip_info v on s.card_id = v.card_id
  where s.oper_date >= '$condition.begin_time.strftime('%F %T')$'
    and s.oper_date <= '$condition.end_time.strftime('%F %T')$'
    $condition.shop_code ? "and s.branch_no = '" + condition.shop_code + "'" : ''$
    $condition.tail ? "and s.flow_no like '%" + condition.tail + "'" : ''$
    $condition.member_no ? "and s.card_no = '" + condition.member_no + "'" : ''$
    $condition.phone ? "and (v.mobile = '" + condition.phone + "' or v.vip_tel = '" + condition.phone + "')" : ''$
    GROUP BY s.card_no, ltrim(rtrim(flow_no)), s.branch_no, s.oper_date) a 
    $condition.total ? "where total > " + (condition.total - 1).to_s + " and total < " + (condition.total + 1).to_s : ''$
    order by oper_time desc
```
["find_orders_by_order_nos"]
```sql
select ltrim(rtrim(flow_no)) order_no,
       branch_no  shop_code,
       convert(float, sum(Sale_money)) order_total
from  t_rm_saleflow
where ltrim(rtrim(flow_no)) in ('$order_nos.join("', '")$')
$ (shop_code.nil? || shop_code == '') ? '': "and branch_no = '" + shop_code + "'" $
 group by ltrim(rtrim(flow_no)),branch_no
```
["create_order"]
```sql
--创建订单接口
--1、先把韩冰传过来的订单数据存入内存临时表
DECLARE @tmp_table TABLE(
  id                  int NOT NULL IDENTITY(1,1),
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
  memo                nvarchar(255),
  freight             numeric(18,2)
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


-- 把运费平摊到第一个商品的价格上去
UPDATE tt
   SET tt.price = (CASE WHEN tt.freight>0 THEN ROUND((tt.price+tt.freight/tt.real_qty),2) ELSE  tt.price END )
  FROM @tmp_table tt
 WHERE id=1

-- 把微商城提货方式为6（自动完成）的订单处理成物流单
UPDATE tt
   SET tt.deal_type = (CASE WHEN tt.deal_type='6' THEN '1' ELSE  tt.deal_type END )
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
                            INSERT INTO dbo.t_order_bill_weixin
                            (
                            [sheet_no],
                            [orderman],[ordertel],
                            [item_no],
                            [item_size],
                            [price],[oper_date],[real_qty],
                            [openid],
                            [branch_no],[shopid],
                            [IsDownload],[branch_name],[item_name],[unit_name],
                            [address],
                            [type_name],[ver],[pay_type],
                            [deal_type],[card_id],
                            [paystatus],[status_upflag],
                            [memo],[dealtime]
                            )
                            select     
                            a.sheet_no,a.orderman,a.ordertel,a.item_no,'',a.price,a.oper_date,a.real_qty,'',a.branch_no,a.branch_no,'0','','','',
                            a.address,'','2','2',a.deal_type,a.card_id,'1',NULL,a.memo,@dealtime    
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
SELECT 
a.sheet_no code,
case when a.IsDownload ='0'  then 'init' when a.IsDownload ='2'  then 'cancel' else 'finished' end state,
b.oper_date shopping_time
FROM [dbo].[t_order_bill_weixin] a
LEFT JOIN  dbo.t_rm_payflow  b  ON a.sheet_no=b.remark
where  a.sheet_no in ($codes$)
GROUP BY a.sheet_no,a.IsDownload,b.oper_date
;
```
["cancel_order"]
```sql
DECLARE @state char(1)
DECLARE @s INT

SET @s=0

SELECT
  @state=a.IsDownload
FROM
dbo.t_order_bill_weixin AS a
WHERE
a.sheet_no= '$proof_code$'
GROUP BY a.sheet_no,a.IsDownload

IF @state is NOT NULL
  BEGIN
    IF  @state='0'
      BEGIN 
      SET ANSI_WARNINGS  OFF
        UPDATE a
           SET a.IsDownload='2',status_upflag='1',memo=memo+'-c'
          FROM dbo.t_order_bill_weixin  AS a
         WHERE a.sheet_no='$proof_code$'
      SET ANSI_WARNINGS  ON
        SELECT 'OK'  AS  return_code

      END 
    ELSE
      SELECT CASE WHEN @state='1' THEN '订单已被门店下载处理，不允许取消' 
                  WHEN @state='2' THEN '订单之前已被取消，请勿重复操作' 
           ELSE  '订单当前为未知状态，不能取消' END AS  return_code 
  END 
ELSE 
  SELECT '找不到对应的订单' AS  return_code
```
["modify_order_member_no"]
```sql
DECLARE @new_member_no  VARCHAR(32)

SELECT @new_member_no=a.card_id 
  FROM dbo.t_rm_vip_info  a
 WHERE a.card_id='$new_member_no$'

IF @new_member_no IS NOT NULL
BEGIN
  UPDATE 
    dbo.t_order_bill_weixin
  SET 
    card_id='$new_member_no$' 
  WHERE 
    card_id='$old_member_no$'
  AND IsDownload='0'
END
```
["check_member_no_exists"]
```sql
DECLARE @card_id VARCHAR(32)

SELECT @card_id=card_id 
  FROM dbo.t_rm_vip_info
 WHERE card_id='$member_no$'
   AND card_status='0'

IF @card_id IS NOT NULL
SELECT 'ok'  AS result
ELSE 
SELECT '会员不存在'  AS result
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
SELECT @gift_type_existed=a.gift_type_id
  from [dbo].[t_rm_gift_type] AS a
 WHERE a.gift_type_id=@gift_type
    

IF @gift_type_existed is NOT NULL
    BEGIN
        INSERT INTO t_rm_gift_certificate
        (
        [giftcert_no],[gift_type],[gift_money],
        [oper_id],[oper_date],[status],
        [begin_date],[end_date],
        [send_branch],
        [card_id]
        )
        VALUES
        (
        @giftcert_no,@gift_type,'$price.to_s$',
        '1001',getdate(),'1',
        '$valid_from.to_s$ 00:00:00.000','$valid_to.to_s$ 23:59:59.997',
        '000',
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
    SET status='2',pay_oper='1001',pay_date=GETDATE(),memo='致维订单_'+'$order_no$'+'_用券'
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
   AND (a.status='1' OR a.status='9')

IF  @giftcert_no_exist IS NOT null
  BEGIN
    UPDATE t_rm_gift_certificate
    SET status='9',memo1='券锁定时间:'+ CONVERT(VARCHAR(19),GETDATE(),120)
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
   AND (a.status='1' OR a.status='9')

IF  @giftcert_no_exist IS NOT null
  BEGIN
    UPDATE t_rm_gift_certificate
    SET status='1',memo1='券解锁时间:'+ CONVERT(VARCHAR(19),GETDATE(),120)
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
rtrim(a.gift_type) AS serial_no,
CASE a.status 
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status, 
a.begin_date valid_from, 
a.end_date valid_to, 
a.pay_date used_at, 
a.oper_date created_at,

rtrim(b.gift_type_name) AS 'name',
CASE b.type_flag WHEN '0' THEN '通用券'  
                 WHEN '1' THEN '品类券'  
                 WHEN '2' THEN '品牌券'  
                 WHEN '3' THEN '单品券'  
                 ELSE '其它未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a 
INNER JOIN t_rm_gift_type b on a.gift_type=b.gift_type_id AND a.card_id=@card_id
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
rtrim(a.gift_type) AS serial_no,
CASE a.status 
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status, 
a.begin_date valid_from, 
a.end_date valid_to, 
a.pay_date used_at, 
a.oper_date created_at,

rtrim(b.gift_type_name) AS 'name',
CASE b.type_flag WHEN '0' THEN '通用券'  
                 WHEN '1' THEN '品类券'  
                 WHEN '2' THEN '品牌券'  
                 WHEN '3' THEN '单品券'  
                 ELSE '其它未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a 
INNER JOIN t_rm_gift_type b on a.gift_type=b.gift_type_id AND a.card_id=@card_id
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
rtrim(a.gift_type) AS serial_no, 
CASE a.status 
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status, 
a.begin_date valid_from, 
a.end_date valid_to, 
a.pay_date used_at, 
a.oper_date created_at,

rtrim(b.gift_type_name) AS 'name',
CASE b.type_flag WHEN '0' THEN '通用券'  
                 WHEN '1' THEN '品类券'  
                 WHEN '2' THEN '品牌券'  
                 WHEN '3' THEN '单品券'  
                 ELSE '其它未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a 
INNER JOIN t_rm_gift_type b on a.gift_type=b.gift_type_id AND a.giftcert_no=@giftcert_no;
```
["find_coupon_by_code"]
```sql
DECLARE @giftcert_no     char(20) --优惠券号
    SET @giftcert_no='$code$'

SELECT 
rtrim(a.card_id) AS member_no, 
rtrim(a.giftcert_no) AS id, 
rtrim(a.giftcert_no) AS code,
rtrim(a.gift_type) AS serial_no, 
CASE a.status 
  WHEN '1' THEN 'activated'
ELSE 'unactivated' END AS status, 
a.begin_date valid_from, 
a.end_date valid_to, 
a.pay_date used_at, 
a.oper_date created_at,

rtrim(b.gift_type_name) AS 'name',
CASE b.type_flag WHEN '0' THEN '通用券'  
                 WHEN '1' THEN '品类券'  
                 WHEN '2' THEN '品牌券'  
                 WHEN '3' THEN '单品券'  
                 ELSE '其它未知类型的券' END AS 'desc'
 FROM t_rm_gift_certificate  a 
INNER JOIN t_rm_gift_type b on a.gift_type=b.gift_type_id AND a.giftcert_no=@giftcert_no;
```
["modify_coupon_member_no"]
```sql
UPDATE t_rm_gift_certificate
   SET card_id='$new_member_no$'
 WHERE card_id='$old_member_no$';
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
   set $user.guide_no.nil? ? '' : "oper_id=convert(varchar(4),'" + user.guide_no + "')," $
       oper_date_gi= getdate(),
     modify_date = getdate()
 where card_no = '$user.member_no$' 
   AND (oper_id IS NULL OR oper_id='0000')

end
```
["modify_register_user_referee_shop"]
```sql
update t_rm_vip_info
   set $user.referee_shop ? "branch_no = '" + user.referee_shop + "'," : ''$
       modify_date = getdate()
 where card_no = '$user.member_no$'
```
["delay_coupon"]
```sql

UPDATE a
SET a.end_date='$end_date$ 23:59:59.997'
FROM t_rm_gift_certificate AS a
WHERE a.giftcert_no='$code$'

```
["find_value_of_offline_cards"]
```sql
SELECT rvs.card_id AS card_no, CONVERT(FLOAT,SUM(CASE WHEN oper_type='4' THEN cast(consum_amt as DECIMAL(12,4)) WHEN oper_type='5' THEN -1*cast(consum_amt as DECIMAL(12,4)) ELSE 0.0000 END)) AS total
  FROM [dbo].[t_rm_vip_savelist] rvs
  JOIN (
        SELECT rvs.card_id
          FROM [dbo].[t_rm_vip_savelist] rvs
          JOIN [dbo].[t_rm_vip_info] rvi ON rvs.card_id=rvi.card_id
         WHERE (rvi.mobile='$phone$' OR rvi.vip_tel='$phone$')
         AND rvi.card_status='0'
         GROUP BY rvs.card_id
        ) dx ON rvs.card_id=dx.card_id
GROUP BY rvs.card_id
```
["offline_card_details"]
```sql
SELECT
rvs.card_id AS member_no,
bbi.branch_name shop_name,
rvs.ope_date oper_date,
CONVERT(FLOAT,(CASE WHEN rvs.oper_type='5' THEN -1*cast(rvs.consum_amt as DECIMAL(12,4)) ELSE cast(rvs.consum_amt as DECIMAL(12,4)) END )) AS num,
rvs.oper_des AS description,
rvs.flow_no AS order_no
  FROM [dbo].[t_rm_vip_savelist] rvs
INNER JOIN [dbo].[t_rm_vip_info] rvi  ON rvs.card_id=rvi.card_id
INNER JOIN dbo.t_bd_branch_info bbi ON rvs.branch_no=bbi.branch_no
WHERE rvs.oper_type IN ('4','5')
  AND rvs.card_id='$member_no$'
  AND rvs.ope_date>='$begin_date.strftime('%F %T')$'
  AND rvs.ope_date<='$end_date.strftime('%F %T')$'
```
["find_service_card_remain"]
```sql

  SELECT
vs.server_name as service,
vs.ret_num as num,
vs.volid_date as time,
vs.cust_no as card_no,
vs.sheet_no as code, 
case sf.stored_flag when '0' then 0 else 1 end as if_time
FROM
t_rm_vip_stored vs
INNER JOIN 
t_rm_vip_stored_flow sf 
ON vs.server_no=sf.server_no 
WHERE
(vs.tel_no='$phone$' or vs.cust_no='$phone$')
AND vs.volid_date>=GETDATE()
AND ((sf.stored_flag=0 and vs.ret_num>0)
OR sf.stored_flag<>0)

```
["service_card_details"]
```sql

  SELECT
oper_date,
vs.memo AS description,
tot_num AS num,
datediff( MONTH, oper_date, volid_date ) AS MONTH,
sheet_no AS code,
bi.branch_name 
FROM
t_rm_vip_stored AS vs
INNER JOIN t_bd_branch_info AS bi ON vs.branch_no= bi.branch_no 
WHERE
vs.sheet_no= '$code$' 
AND oper_date BETWEEN '$begin_date.strftime('%F %T')$'
AND '$end_date.strftime('%F %T')$'
UNION ALL
SELECT
ss.oper_date,
ss.memo AS description,
ss.consum_count*- 1 AS num,
0 AS MONTH,
ss.sheet_no AS code,
bi.branch_name 
FROM
t_rm_vip_stored_saleflow AS ss
INNER JOIN t_bd_branch_info bi ON ss.branch_no= bi.branch_no 
WHERE
ss.sheet_no= '$code$' 
AND oper_date BETWEEN '$begin_date.strftime('%F %T')$'
AND '$end_date.strftime('%F %T')$'

```
