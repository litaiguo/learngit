from os.path import join

from  pymongo import MongoClient

def genAllOrgsOfSqls(org_codes):

    for org_code in org_codes:
        print (org_code)
        agent = collection.find_one({'org_code': org_code})
        if (agent is None):
            print ("org_code 是"+org_code+"的商户MongoDB上不存在，请人工核对！！！")
        else:
            orgcode = agent['org_code']
            dbConfig = agent['database_config']
            dbDefault = dbConfig['default']
            username = dbDefault['username']
            password = dbDefault['password']
            host = dbDefault['host']
            port = dbDefault['port']
            database = dbDefault['database']

            sqls = agent['sqls']
            with open(join(orgSqlsDirName, "{0}_sqls.md".format(org_code)), "w", encoding="utf-8") as sql_file:
                # sql_file.write('```sql\n')
                # sql_file.write("shopDbInformation")
                # sql_file.write('\n')
                # sql_file.write("org_code:"+orgcode)
                # sql_file.write('\n')
                # sql_file.write("host:"+host)
                # sql_file.write('\n')
                # sql_file.write("port:"+str(port))
                # sql_file.write('\n')
                # sql_file.write("username:"+username)
                # sql_file.write('\n')
                # sql_file.write("password:"+password)
                # sql_file.write('\n')
                # sql_file.write("database:"+database)
                # sql_file.write('\n')
                # sql_file.write('```\n')

                for interfaceName, sqlContent in sqls.items():
                    print(interfaceName + "start写入")
                    sql_file.write("[\""+interfaceName+"\"]")
                    sql_file.write('\n')
                    sql_file.write('```sql\n')
                    sql_file.write(sqlContent)
                    sql_file.write('\n')
                    sql_file.write('```\n')
                    print (interfaceName + "end写入")

org_codes_test = [
    "scayf"
]

# org_codes = [
#     "aier",
#     "aitiantian",
#     "aiwa",
#     "aiying",
#     "aiyingfang",
#     "babybear",
#     "babycare",
#     "babycountry",
#     "babyfocus",
#     "bearhouse",
#     "beibei",
#     "byjy",
#     "chenbaby",
#     "clbabytiandi",
#     "congcong",
#     "czqcyy",
#     "dd",
#     "dreamstart",
#     "dtaiyingfang",
#     "eastbaby",
#     "fabeiniu",
#     "fqyaya",
#     "fzjiabeiai",
#     "greentoys",
#     "growgarden",
#     "haoshijie",
#     "happyxybb",
#     "harneybaby",
#     "heartlove",
#     "hefeijyl",
#     "jdb",
#     "jiajia",
#     "jialibaby",
#     "jinbaby",
#     "jinyaolan",
#     "jodafengche",
#     "keai",
#     "kkqq",
#     "lebaby",
#     "lebao",
#     "leyaya",
#     "loveangel",
#     "loveheart",
#     "lshibaby",
#     "lyjy",
#     "lzgoodboy",
#     "lzyyb",
#     "mamabb",
#     "mamalove",
#     "mamibaobei",
#     "muyingfang",
#     "muyingyuan",
#     "ndabd",
#     "ptbabyplan",
#     "pxayf",
#     "pyfujiababy",
#     "qwmykj",
#     "rsxyzj",
#     "rxwayy",
#     "shengyi",
#     "smhybb",
#     "subujyl",
#     "sunnybaby",
#     "sxqzf",
#     "tianyibaby",
#     "wanpf",
#     "wlmami",
#     "wxmyf",
#     "xinrenlei",
#     "xzbym",
#     "xzmmbb",
#     "yaerbaby",
#     "ybfcbb",
#     "ygyj",
#     "yingyuan",
#     "yingyuansu",
#     "youyimy",
#     "yujiababy",
#     "yybb",
#     "yyplan",
#     "zgprettybaby"
# ]

# 测试mongo
# mc = MongoClient('192.168.10.202', 27017)

# 线上mongo
mc = MongoClient('222.73.36.230', 40000)
db = mc.crm_production
collection = db.database_agents


orgSqlsDirName = "D:\joowing_git\learngit\joowing_test"


# 插入all sqls
# insert_allSqls(fileName)


# genAllOrgsOfSqls(org_codes)
genAllOrgsOfSqls(org_codes_test)
