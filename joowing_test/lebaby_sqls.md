["find_user_by_phone"]
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
["find_user_by_member_no"]
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
["create_user"]
```sql

declare @member_no varchar(30)  --会员编号 

select top 1 @member_no = card_face
 FROM
dbo.vip_main AS a
WHERE
telephone= '$user.mobile$'
and a.card_state='0' 
   
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
       '01',
       getdate(),         
       2,
       $user.guide_no.nil? ? '': "'" + user.guide_no + "',"$
       0
       )
    end
end
select @member_no member_no,@member_no member_id

```
["modify_user"]
```sql

DECLARE @user_level  VARCHAR(2)
SET @user_level='$user.level$'

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
case @user_level when '1' then '01' else @user_level end,
getdate(),         
2,
'$user.guide_no$' ,
1
)

```
["find_exist_phones"]
```sql
select telephone AS mobile from wucrm.vip_main 
where telephone in ('$mobiles.join("', '")$') 
```
["find_score"]
```sql

SELECT Sum(score) score FROM (
SELECT CONVERT(INTEGER,SUM(available_integral)) score
   FROM wucrm.guest_integral a 
   JOIN wucrm.vip_main b on a.guest_id=b.guest_id
  WHERE b.card_face='$member_no$' 
UNION all
select CONVERT(INTEGER,sum(sum_integral*state)) score 
   from wucrm.account_integral_tmp 
   WHERE card_face='$member_no$') a

```
["modify_score"]
```sql

EXEC wucrm.up_insert_account_integral
replace(replace(replace(convert(VARCHAR(19),getdate(),120),'-',''),':',''),' ',''),
    '$score_detail.member_no$',
    '$score_detail.score.abs.to_s$',
    '线上积分变更',
    '$score_detail.score > 0 ? '1': '-1'$',
    CONVERT(varchar(8), GETDATE(), 108)
```
["find_score_details"]
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
["find_prices"]
```sql
SELECT a.* ,isnull(b.spec_price,a.member_price) price_area FROM 
(SELECT
a.organ shop_code,
a.code  as code,
convert(float, max(a.price)) original_price,
convert(float, max(a.memprice)) member_price
FROM wuerp.comm_shop a
WHERE a.deleted='N' 
and a.code in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
group by a.organ ,a.code ) a
LEFT JOIN 
(SELECT
b.organ shop_code,
b.code as code,
convert(float, max(b.spec_price)) spec_price
FROM wuerp.pop_info b 
WHERE b.startdate<=GETDATE() AND b.enddate>=GETDATE()
AND b.deleted='N' 
and b.code in ('$codes.map{ |code| code + "', '" + code + "' + CHAR(10)" }.join(", '")$)
group by b.organ ,b.code ) b on a.shop_code=b.shop_code AND a.code=b.code
```
["find_stocks"]
```sql
SELECT
(CASE WHEN organ='0999' THEN '1024' else organ END) shop_code,
code,
convert(int, sum(amount) * $rat$) stock
FROM
wuerp.cur_stock
where code in ('$codes.join("', '")$') 
group by organ,code
```
["find_member_order_histories"]
```sql
EXEC wuerp.zw_find_member_order_histories '$member_no$','$begin_time.strftime('%F %T')$','$end_time.strftime('%F %T')$'
```
["create_order"]
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
$order.order_items.map{ |i| "('" + order.shop_code + "', getdate(), '" + order.order_no + "', '" + order.freight.to_s + "', '" + order.member_no + "', '" + (i.item_type == 'coupon' ? '2900005000020' : i.code) + "', '" + (i.item_type == 'coupon' ? '1' : "%0.2f" % i.price) + "', '" + (i.item_type == 'coupon' ? "%0.2f" % (i.price * i.num) : i.num.to_s) + "', '" + "%0.2f" % (i.price * i.num) + "', 9999, '" +  order.delivery_method.to_s + "', '" + i.proof_code.to_s + "', '" + (order.guide_no || '66666') + "')"}.join(', ')$
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
```
["find_all_user_by_phone"]
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
["check_by_phone"]
```sql
SELECT card_face, telephone FROM dbo.zw_vip_main_list where telephone = '$mobile$' and reg_flag = 0;
```
["find_service_card_remain"]
```sql
SELECT rtrim(a.card_face)  AS card_no,b.name AS service, CONVERT(FLOAT,sum(a.acc_bala*a.state)) AS num,rtrim(a.code) code 
from wucrm.account_deposit_num a 
inner join wucrm.commodity b on a.code=b.code 
INNER JOIN wucrm.vip_main c ON a.card_face=c.card_face
WHERE c.telephone='$phone$'
GROUP BY rtrim(a.card_face),b.name,rtrim(a.code)
```
["service_card_details"]
```sql
select  rtrim(a.organ_id) shop_code,c.name shop_name,rtrim(a.card_face) member_no, 
a.busdate oper_date,rtrim(a.code) code,b.name description ,a.acc_bala*a.state num 
from wucrm.account_deposit_num a 
inner join wucrm.commodity b on a.code=b.code 
inner join wumaster.organ c on a.organ_id=c.organ
where a.card_face='$member_no$' 
and a.busdate >='$begin_date.strftime('%F %T')$' 
and a.busdate <='$end_date.strftime('%F %T')$'
and a.code='$code$'
```
["modify_level"]
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
["find_value_of_offline_cards"]
```sql
SELECT va.card_id AS card_no,sum(cash_bala) AS total FROM token_acc ta INNER JOIN vip_main va ON ta.card_id = va.card_id WHERE va.telephone = '$phone$' GROUP BY va.card_id
```
["offline_card_details"]
```sql
select card_face as member_no, o.name as shop_name, CONVERT(varchar(100), busdate, 23)+' '+CONVERT(varchar(100), bustime, 24) as oper_date, case when ad.state='1' then sum_cash else -1*sum_cash end as num, resume as description, organ_id+'_'+CONVERT(varchar(100), busdate, 23)+'_'+posid+'_'+billid as order_no from account_deposit ad left join wumaster.organ o on ad.organ_id=o.organ  where ad.card_face='$member_no$' AND ad.busdate>='$begin_date.strftime('%F %T')$' AND ad.busdate<='$end_date.strftime('%F %T')$' AND sum_cash<>0 
```
