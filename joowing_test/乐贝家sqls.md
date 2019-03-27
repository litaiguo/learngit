find_user_by_phone
```sql
SELECT top 1
a.card_id member_id,
ltrim(rtrim(a.card_face)) AS member_no,
a.name ,
a.babybirthday AS birthday,
ltrim(rtrim(telephone)) AS mobile,
vip_type AS level,
case SEX when 'M' then '1' when 'F' then '2' else '3' end AS sex  -- M 男 F 女
FROM
wucrm.vip_main AS a 
WHERE
telephone = '$mobile$' 
and a.card_state='0' 
order by a.startdate desc
```

check_by_phone
```sql
SELECT card_face member_no, 
telephone mobile
FROM dbo.zw_vip_main_list 
where telephone = '$mobile$' 
and reg_flag = 0
```

find_all_user_by_phone
```sql
SELECT 
a.card_id member_id,
ltrim(rtrim(a.card_face)) AS member_no,
a.name ,
a.babybirthday AS birthday,
ltrim(rtrim(telephone)) AS mobile,
vip_type AS level,
case SEX when 'M' then '1' when 'F' then '2' else '3' end AS sex  -- M 男 F 女
FROM
wucrm.vip_main AS a 
WHERE
telephone = '$mobile$' 
and a.card_state='0' 
order by a.startdate desc
```

find_user_by_member_no
```sql
SELECT top 1 
a.card_id member_id,
ltrim(rtrim(a.card_face)) AS member_no,
a.name ,
a.babybirthday AS birthday,
ltrim(rtrim(telephone)) AS mobile,
vip_type AS level,
case SEX when 'M' then '1' when 'F' then '2' else '3' end AS sex  -- M 男 F 女
FROM
wucrm.vip_main AS a 
WHERE
a.card_face='$member_no$'
and a.card_state='0'
```
create_user
```sql
declare @member_no varchar(30)  --会员编号 

select top 1 @member_no = card_face
 FROM
dbo.vip_main AS a
WHERE
telephone= '$user.mobile$'
and a.card_state='0' 
order by a.startdate desc 
   
if @member_no is null
begin
   select top 1 @member_no = card_face
   FROM
   dbo.zw_vip_main_list AS a
   WHERE
   telephone= '$user.mobile$'
   and a.flag=1
   if @member_no is null
   begin
     set  @member_no=  '$user.member_no$'
     insert into zw_vip_main_list(
     card_face,
     name,
     telephone,
     sex,
     birthday,
     organ,
     vip_type,
     createdate,
     flag,
     $user.guide_no.nil? ? '': "referee_card, "$
     reg_flag
     )
    values('$user.member_no$',       
       '$user.name$',
       '$user.mobile$',
       case '$user.sex$' when '1' then 'M' when '2' then 'F'  else '' end,
       '$user.birthday.try(&:to_s)$',
       '$user.referee_shop$',
       $user.level.nil? ? "'01'," : "'" + user.level + "',"$
       getdate(),         
       2,
       $user.guide_no.nil? ? '': "'" + user.guide_no + "',"$
       0
       )
    end
end
select @member_no member_no,@member_no member_id
```
modify_user
```sql
insert into zw_vip_main_list(
card_face,
organ,
name,
telephone,
sex,
birthday,
vip_type,
createdate,
flag,
referee_card,
reg_flag
)
values(
'$user.member_no$', 
'$user.referee_shop$',
'$user.name$',
'$user.mobile$',      
case '$user.sex$' when '1' then 'M' when '2' then 'F'  else '' end,
'$user.birthday.try(&:to_s)$',
'$user.level$',
getdate(),         
2,
'$user.guide_no$' ,
1
)
```
modify_level
```sql
insert into zw_vip_main_list(
card_face,
organ,
name,
telephone,
sex,
birthday,
vip_type,
createdate,
flag,
referee_card,
reg_flag
)
values(
'$user.member_no$', 
'$user.referee_shop$',
'$user.name$',
'$user.mobile$',      
case '$user.sex$' when '1' then 'M' when '2' then 'F'  else '' end,
'$user.birthday.try(&:to_s)$',
'$user.level$',
getdate(),         
2,
'$user.guide_no$' ,
1
)
```
find_exist_phones
```sql
select telephone AS mobile from vip_main 
where telephone in ('$mobiles.join("', '")$') 

```
find_score
```sql
SELECT Sum(score) score FROM (
SELECT CONVERT(INTEGER,SUM(available_integral)) score
   FROM wucrm.guest_integral a 
   JOIN wucrm.vip_main b on a.guest_id=b.guest_id
  WHERE b.card_face='$member_no$' AND (a.organ!='0000' OR shop_type!=1) 
UNION all
select CONVERT(INTEGER,sum(sum_integral*state)) score 
   from wucrm.account_integral_tmp 
   WHERE card_face='$member_no$') a
```
modify_score
```sql
EXEC wucrm.up_insert_account_integral 
replace(replace(replace(convert(VARCHAR(19),getdate(),120),'-',''),':',''),' ',''),
'$score_detail.member_no$',
'$score_detail.score.abs.to_s$',
'$score_detail.description$',
'$score_detail.score > 0 ? '1': '-1'$', 
CONVERT(varchar(8), GETDATE(), 108)
```
find_score_details
```sql
select LEFT(busdate,10)+' '+LEFT(acc_time,8) created_at,
       convert(float, sum_integral*state) score,
       resume description
   from wucrm.account_integral
  where card_face = '$member_no$'
    and LEFT(busdate,10)+' '+LEFT(acc_time,8) >= '$begin_time.strftime('%F %T')$'
    and LEFT(busdate,10)+' '+LEFT(acc_time,8) <= '$end_time.strftime('%F %T')$'
UNION ALL
select LEFT(busdate,10)+' '+LEFT(acc_time,8) created_at,
       convert(float, sum_integral*state) score,
       resume description
   from wucrm.account_integral_tmp
  where card_face = '$member_no$'
    and LEFT(busdate,10)+' '+LEFT(acc_time,8) >= '$begin_time.strftime('%F %T')$'
    and LEFT(busdate,10)+' '+LEFT(acc_time,8) <= '$end_time.strftime('%F %T')$'
```
find_prices
```sql
DECLARE @tmp_table TABLE(
    product_code VARCHAR(32),
    shop_code VARCHAR(30),
    original_price FLOAT,
    member_price FLOAT,
    price  FLOAT
)

INSERT INTO @tmp_table(shop_code, product_code,original_price,member_price,price)
SELECT
a.organ shop_code,
a.code  product_code,
convert(float, max(a.price)) original_price,
convert(float, max(a.memprice)) member_price,
convert(float, max(a.memprice)) price
FROM dbo.comm_shop a 
WHERE a.code in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
  AND a.deleted='N'
group by a.organ ,a.code

DECLARE @tmp_table_spec TABLE(
    product_code VARCHAR(32),  
    shop_code VARCHAR(30),
    original_price FLOAT,
    member_price FLOAT,
    spec_price  FLOAT
)
INSERT INTO @tmp_table_spec(shop_code, product_code,spec_price)
SELECT
b.organ shop_code,
b.code product_code,
convert(float, max(b.spec_price)) spec_price
FROM dbo.pop_info b 
WHERE b.code in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
AND b.startdate<=GETDATE() AND b.enddate>=GETDATE()
AND b.deleted='N'
group by b.organ ,b.code

UPDATE tt
   SET tt.price=tts.spec_price
  FROM @tmp_table tt
  JOIN @tmp_table_spec tts ON tt.shop_code=tts.shop_code AND tt.product_code=tts.product_code

SELECT 
product_code code,
shop_code,
original_price,
member_price,
price
FROM @tmp_table  a
ORDER BY a.product_code,a.shop_code
```
find_stocks
```sql
SELECT
(CASE WHEN organ='0999' THEN '0999' else organ END) shop_code,
code,
convert(int, sum(amount) * $rat$) stock
FROM
dbo.cur_stock
where code in ('$codes.join("', '")$') 
group by organ,code
```
find_member_order_histories
```
select a.*,order_total from 
(SELECT
a.cardid AS member_no,
a.organ+'_'+convert(varchar(10),a.selldate,120)+'_'+rtrim(a.posid)+'_'+rtrim(a.receipt) AS order_no,
a.organ AS shop_code,
a.organ+'_'+convert(varchar(10),a.selldate,120)+'_'+rtrim(a.posid)+'_'+rtrim(a.receipt)+convert(varchar(20),a.nd1) AS order_item_no,
a.code,
convert(float,a.price) AS price,
convert(int, a.amount) AS num,
convert(float,a.sum_sell) AS total,
convert(varchar(10),a.selldate,120) + ' ' + convert(varchar(8),a.selltime) oper_time
FROM
dbo.sell_waste_day a
          where convert(varchar(10),a.selldate,120) + ' ' + convert(varchar(8),a.selltime) >= convert(varchar(19),'$begin_time.strftime('%F %T')$',120)
            and convert(varchar(10),a.selldate,120) + ' ' + convert(varchar(8),a.selltime) <= convert(varchar(19),'$end_time.strftime('%F %T')$',120)
            and cardid= '$member_no$') a
inner join 
(select a.organ+'_'+convert(varchar(10),a.selldate,120)+'_'+rtrim(a.posid)+'_'+rtrim(a.receipt)  order_no,
                convert(float, sum(sum_sell)) order_total                
           from  sell_waste_day a
          where convert(varchar(10),a.selldate,120) + ' ' + convert(varchar(8),a.selltime) >= convert(varchar(19),'$begin_time.strftime('%F %T')$',120)
            and convert(varchar(10),a.selldate,120) + ' ' + convert(varchar(8),a.selltime) <= convert(varchar(19),'$end_time.strftime('%F %T')$',120)
            and cardid= '$member_no$' 
 group by a.organ+'_'+convert(varchar(10),a.selldate,120)+'_'+rtrim(a.posid)+'_'+rtrim(a.receipt)) b on a.order_no=b.order_no
```
find_order_by_order_no
```sql
```
find_order_by_condition
```sql
```
create_order
```sql
--创建订单接口
--1、先把韩冰传过来的订单数据存入内存临时表
DECLARE @tmp_table TABLE(
id                 int NOT NULL IDENTITY(1,1),
freight            numeric(18,2),
organ              char(4),
selldate           datetime,
receipt            varchar(20),
cardface           varchar(16),
barcode            varchar(18),
price              numeric(18,2),
amount             numeric(18,2),
sum_sell           numeric(18,2),
posid              varchar(10) COLLATE Chinese_PRC_CI_AS NULL DEFAULT ((9999)),
delivery_method   tinyint,
zw_order_no        varchar(20),
receid             varchar(20)
)

begin
insert into @tmp_table
(organ, selldate, zw_order_no, freight, cardface, barcode, price, amount, sum_sell, posid, delivery_method, receipt, receid) 
values
$order.order_items.map{ |i| "('" + order.shop_code + "', getdate(), '" + order.order_no + "', '" + order.freight + "', '" + order.member_no + "', '" + (i.item_type == 'coupon' ? '2900005000020' : i.code) + "', '" + (i.item_type == 'coupon' ? '1' : "%0.2f" % i.price) + "', '" + (i.item_type == 'coupon' ? "%0.2f" % (i.price * i.num) : i.num.to_s) + "', '" + "%0.2f" % (i.price * i.num) + "', 9999, '" +  order.delivery_method.to_s + "', '" + i.proof_code.to_s + "', '" + (order.guide_no || '66666') + "')"}.join(', ')$
end

UPDATE tt
   SET tt.price = (CASE WHEN tt.freight>0 THEN ROUND((tt.price+tt.freight/tt.amount),2) ELSE  tt.price END ),tt.sum_sell=(tt.sum_sell+tt.freight)
  FROM @tmp_table tt
 WHERE id=1

declare @zw_order_no varchar(30)  --订单编号 
 select @zw_order_no=zw_order_no
   FROM dbo.zw_sell_waste_day AS a
  WHERE a.zw_order_no= '$order.order_no$'

if @zw_order_no is null
begin
  begin tran T1
    insert into zw_sell_waste_day
          (organ, selldate, receipt, cardface, barcode, price, amount, sum_sell, posid, delivery_method, zw_order_no, receid) 
    SELECT organ, selldate, receipt, cardface, barcode, price, amount, sum_sell, posid, delivery_method, zw_order_no, receid
      FROM @tmp_table
  commit tran T1
  SELECT 'OK'  AS  return_code
end
ELSE   
  SELECT 'This order already exists. Do not create it repeatedly'  AS  return_code;

/*
declare @zw_order_no varchar(30)  --订单编号 

select @zw_order_no=zw_order_no
 FROM
dbo.zw_sell_waste_day AS a
WHERE
a.zw_order_no= '$order.order_no$'

if @zw_order_no is null
begin

insert into zw_sell_waste_day
(organ, selldate, zw_order_no, cardface, barcode, price, amount, sum_sell, posid, delivery_method, receipt, receid) values
$order.order_items.map{ |i| "('" + order.shop_code + "', getdate(), '" + order.order_no + "', '" + order.member_no + "', '" + (i.item_type == 'coupon' ? '2900005000020' : i.code) + "', '" + (i.item_type == 'coupon' ? '1' : "%0.2f" % i.price) + "', '" + (i.item_type == 'coupon' ? "%0.2f" % (i.price * i.num) : i.num.to_s) + "', '" + "%0.2f" % (i.price * i.num) + "', 9999, '" +  order.delivery_method.to_s + "', '" + i.proof_code.to_s + "', '" + (order.guide_no || '66666') + "')"}.join(', ')$
SELECT 'OK'  AS  return_code
end
ELSE   SELECT '该订单线下库已存在，请勿重复创建'  AS  return_code;
*/
```
