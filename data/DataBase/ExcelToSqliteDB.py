"""
用于将 excel 文件转为 sqlite3 数据库文件
生成过程存在很多人为干预
"""
import xlrd, re, sqlite3,copy, pprint
from OntologyConstruction import TaoCan_DB_slots, \
    LiuLiang_DB_slots,WLAN_DB_slots,Card_DB_slots
from OntologyConstruction import MultiTerminal_DB_slots
from OntologyConstruction import Overseas_DB_slots

def excel_reader_TAOCAN():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('套餐业务')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []

    Default_DataItemValues = {
        "子业务":None,
        "主业务":None,
        "产品介绍":None,
        "计费方式": None,
        "功能费": None,
        "套餐内容_国内主叫":None,
        "套餐内容_国内短信":None,
        "套餐内容_国内彩信":None,
        "套餐内容_国内流量":None,
        "套餐内容_WLAN流量":None,
        "套餐内容_其他功能":None,
        "适用品牌": "全球通、动感地带、神州行",
        "超出处理_国内主叫":"0.19元/分钟，不收取漫游费",
        "超出处理_国内短信": "全球通、动感地带、神州行5元卡为0.1元/条；神州行升级版标准卡、畅听卡、家园卡为0.15元/条",
        "超出处理_国内彩信": "0.3元/条",
        "超出处理_国内流量": "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）",
        "超出处理_WLAN流量": "0.01元/MB",
        "超出处理_WLAN时长": "0.01元/分钟计费。单个账号每月500元封顶，每月限40GB流量",
        "结转规则_国内主叫": "套餐内语音资源当月有效，未用完部分不累计到下月。",
        "结转规则_国内短信": "套餐内短信资源当月有效，未用完部分不累计到下月。",
        "结转规则_国内流量": "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
        "结转规则_WLAN流量": "不可结转分享",
        "结转规则_WLAN时长": "不可结转分享",
        "结转规则_赠送流量": "赠送的套外国内流量，套餐内所有流量用尽后方可使用，且不结转，可分享",
        "是否全国接听免费": "是",
        "是否包含港澳台地区": "不包含港澳台",
        "能否结转滚存": "能",
        "能否分享": "能",
        "能否转赠": "能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用限制":None,
        "使用有效期":None,
        "使用方式设置":None,
        "封顶规则": "套餐遵循500元、15G双封顶限制",
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "互斥业务": None,
        "开通客户限制": "北京移动全球通、动感地带、神州行升级版标准卡、畅听卡、家园卡、5元卡",
        "累次叠加规则": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "是否到期自动取消": "是",
        "能否变更或取消": "该套餐可以变更或取消",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "取消变更生效规则": "当月变更/取消，下月生效",
        "变更方式": None
    }
    slot_excel_column_id={
        "子业务": 0,
        "主业务": 1,
        "产品介绍": 2,
        "计费方式": 3,
        "适用品牌": 4,
        "功能费": 5,
        "套餐内容_国内主叫": 6,
        "套餐内容_国内短信": 7,
        "套餐内容_国内彩信": 8,
        "套餐内容_国内流量": 9,
        "套餐内容_WLAN流量": 13,
        "套餐内容_其他功能": 15,
        "超出处理_国内主叫": 16,
        "超出处理_国内短信": 17,
        "超出处理_国内彩信": 18,
        "超出处理_国内流量": 19,
        "超出处理_WLAN流量": 21,
        "超出处理_WLAN时长": 22,
        "结转规则_国内主叫": 23,
        "结转规则_国内短信": 24,
        "结转规则_国内流量": 26,
        "结转规则_WLAN流量": 28,
        "结转规则_WLAN时长": 29,
        "结转规则_赠送流量": 30,
        "是否全国接听免费": 31,
        "是否包含港澳台地区": 32,
        "能否结转滚存": 33,
        "能否分享": 34,
        "能否转赠": 36,
        "流量分享方式": 35,
        "流量转赠方式": 37,
        "转户转品牌管理": 38,
        "停机销号管理": 39,
        "赠送优惠活动": 40,
        "使用限制": 41,
        "使用有效期": 42,
        "使用方式设置": 43,
        "封顶规则": 44,
        "限速说明": 45,
        "受理时间": 46,
        "互斥业务": 47,
        "开通客户限制": 48,
        "累次叠加规则": 49,
        "开通方式": 50,
        "开通生效规则": 51,
        "是否到期自动取消": 53,
        "能否变更或取消": 54,
        "取消方式": 55,
        "取消变更生效规则": 56,
        "变更方式": 57
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        if table_values[0] == "":
            PrimaryItem = table_values

        for slot in Default_DataItemValues:
            if table_values[slot_excel_column_id[slot]] != "":
                DataItem[slot] = table_values[slot_excel_column_id[slot]]
            elif PrimaryItem[slot_excel_column_id[slot]] != "":
                DataItem[slot] = PrimaryItem[slot_excel_column_id[slot]]
            else:
                DataItem[slot] = Default_DataItemValues[slot]
        DataItem["结转规则"] = "套餐内语音短信资源当月有效，未用完部分不累计到下月。当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转"
        DataItem["超出处理"] = "国内主叫0.19元/分钟，不收取漫游费，套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）"
        temp_str = "包含"
        for s in ["套餐内容_国内主叫", "套餐内容_国内短信", "套餐内容_国内彩信",
                  "套餐内容_国内流量", "套餐内容_WLAN流量", "套餐内容_其他功能"]:
            if DataItem[s] !=None:
                if s == "套餐内容_其他功能":
                    temp_str += "%s，" % (DataItem[s])
                else:
                    temp_str += "%s%s，" %(s[5:], DataItem[s])
        temp_str = temp_str[:-1]
        DataItem["套餐内容"] = temp_str
        if DataItem["子业务"] != None:
            DataItem["主业务"] = None
            DataItem["计费方式"] = "%s，套餐内语音资源用尽后，国内主叫0.19元/分钟，不收取漫游费，流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后以此类推" %(DataItem["功能费"])
            if DataItem["产品介绍"] == None:
                DataItem["产品介绍"] = "%s: %s，套餐%s, 全国接电话免费，套餐内资源不包含港澳台" %(DataItem["子业务"], DataItem["功能费"], temp_str)
            if re.match(r"^KT.*",DataItem["开通方式"]):
                DataItem["变更方式"] = re.sub(r"^KT", "BG", DataItem["开通方式"])
        DataBaseList.append(copy.deepcopy(DataItem))

        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList

def extract_TAOCAN():
    """
    读取流量业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE 套餐("
    for slot in TaoCan_DB_slots:
        if slot in ["功能费", "套餐内容_国内主叫", "套餐内容_国内流量"]:
            exec_create_command += "%s NUMERIC," % slot
        else:
            exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_TAOCAN():
        # print(data)
        if data["功能费"]:
            m = re.match(r"(\d+).*", data["功能费"])
            data["功能费"] = int(m.group(1))
        if data["套餐内容_国内主叫"]:
            m = re.match(r"(\d+).*", data["套餐内容_国内主叫"])
            data["套餐内容_国内主叫"] = int(m.group(1))
        if data["套餐内容_国内流量"]:
            m = re.match(r"(\d+)(MB|GB)", data["套餐内容_国内流量"])
            if m.group(2) == 'MB':
                data["套餐内容_国内流量"] = int(m.group(1))
            else:
                data["套餐内容_国内流量"] = int(m.group(1)) * 1024



        exec_insert_command = "INSERT INTO 套餐(" +\
            ",".join([slot for slot in TaoCan_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in TaoCan_DB_slots:
            if slot in ["功能费", "套餐内容_国内主叫", "套餐内容_国内流量"]:
                if data[slot]  == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += str(data[slot])+','
            else:
                if data[slot] == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()

def excel_reader_LIULIANG():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('流量业务')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []
    Default_DataItemValues = {
        "子业务":None,
        "主业务":None,
        "产品介绍":None,
        "计费方式": None,
        "功能费": None,
        "套餐内容_国内流量":None,
        "套餐内容_定向视频流量":None,
        "套餐内容_夜间闲时流量":None,
        "套餐内容_其他功能": None,
        "适用品牌": "全球通、动感地带、神州行",
        "超出处理_国内主叫":"0.19元/分钟，不收取漫游费",
        "超出处理_国内短信": "全球通、动感地带、神州行5元卡为0.1元/条；神州行升级版标准卡、畅听卡、家园卡为0.15元/条",
        "超出处理_国内彩信": "0.3元/条",
        "超出处理_国内流量": "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）",
        "结转规则_国内流量": "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
        "是否包含港澳台地区": "不包含港澳台",
        "能否结转滚存": "能",
        "能否分享": "能",
        "能否转赠": "能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用限制":None,
        "使用有效期":None,
        "使用方式设置":None,
        "封顶规则": "套餐遵循500元、15G双封顶限制",
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "互斥业务": None,
        "开通客户限制": "北京移动全球通、动感地带、神州行升级版标准卡、畅听卡、家园卡、5元卡",
        "累次叠加规则": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "是否到期自动取消": "是",
        "能否变更或取消": "该套餐可以变更或取消",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "取消变更生效规则": "当月变更/取消，下月生效",
        "变更方式": None
    }
    slot_excel_column_id={
        "子业务": 0,
        "主业务": 1,
        "产品介绍": 2,
        "计费方式": 3,
        "适用品牌": 4,
        "功能费": 5,
        "套餐内容_国内流量": 9,
        "套餐内容_定向视频流量":11,
        "套餐内容_夜间闲时流量":12,
        "套餐内容_其他功能": 15,
        "超出处理_国内流量": 19,
        "结转规则_国内流量": 26,
        "是否包含港澳台地区": 32,
        "能否结转滚存": 33,
        "能否分享": 34,
        "能否转赠": 36,
        "流量分享方式": 35,
        "流量转赠方式": 37,
        "转户转品牌管理": 38,
        "停机销号管理": 39,
        "赠送优惠活动": 40,
        "使用限制": 41,
        "使用有效期": 42,
        "使用方式设置": 43,
        "封顶规则": 44,
        "限速说明": 45,
        "受理时间": 46,
        "互斥业务": 47,
        "开通客户限制": 48,
        "累次叠加规则": 49,
        "开通方式": 50,
        "开通生效规则": 51,
        "是否到期自动取消": 53,
        "能否变更或取消": 54,
        "取消方式": 55,
        "取消变更生效规则": 56,
        "变更方式": 57
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        if table_values[0] == "":
            PrimaryItem = table_values

        for slot in Default_DataItemValues:
            if slot in LiuLiang_DB_slots:
                if table_values[slot_excel_column_id[slot]] != "":
                    DataItem[slot] = table_values[slot_excel_column_id[slot]]
                elif PrimaryItem[slot_excel_column_id[slot]] != "":
                    DataItem[slot] = PrimaryItem[slot_excel_column_id[slot]]
                else:
                    DataItem[slot] = Default_DataItemValues[slot]
        DataItem["结转规则"] = "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转"
        DataItem["超出处理"] = "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）"
        temp_str = "包含"
        for s in ["套餐内容_国内流量", "套餐内容_其他功能"]:
            if DataItem[s] !=None:
                if s == "套餐内容_其他功能":
                    temp_str += "%s，" % (DataItem[s])
                else:
                    temp_str += "%s%s，" %(s[5:], DataItem[s])
        temp_str = temp_str[:-1]
        DataItem["套餐内容"] = temp_str
        if DataItem["子业务"] != None:
            DataItem["主业务"] = None
            DataItem["计费方式"] = "%s，套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后以此类推" %(DataItem["功能费"])
            if DataItem["产品介绍"] == None:
                DataItem["产品介绍"] = "%s: %s，套餐%s, 流量不收取漫游费，不包含港澳台" %(DataItem["子业务"], DataItem["功能费"], temp_str)
            if re.match(r"^KT.*",DataItem["开通方式"]):
                DataItem["变更方式"] = re.sub(r"^KT", "BG", DataItem["开通方式"])
        DataBaseList.append(copy.deepcopy(DataItem))

        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList

def extract_LIULIANG():
    """
    读取流量业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE 流量("
    for slot in LiuLiang_DB_slots:
        if slot in ["功能费",  "套餐内容_国内流量"]:
            exec_create_command += "%s NUMERIC," % slot
        else:
            exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_LIULIANG():
        print(data)
        if data["功能费"]:
            if data["功能费"] == "免费":
                data["功能费"] = 0
            else:
                m = re.match(r"(\d+).*", data["功能费"])
                data["功能费"] = int(m.group(1))
        if data["套餐内容_国内流量"]:
            m = re.match(r"(\d+)(MB|GB)", data["套餐内容_国内流量"])
            if m.group(2) == 'MB':
                data["套餐内容_国内流量"] = int(m.group(1))
            else:
                data["套餐内容_国内流量"] = int(m.group(1)) * 1024

        exec_insert_command = "INSERT INTO 流量 (" +\
            ",".join([slot for slot in LiuLiang_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in LiuLiang_DB_slots:
            if slot in ["功能费",  "套餐内容_国内流量"]:
                if data[slot]  == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += str(data[slot])+','
            else:
                if data[slot] == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()

def excel_reader_WLAN():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('WLAN业务')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []
    Default_DataItemValues = {
        "子业务":None,
        "主业务":None,
        "产品介绍":None,
        "计费方式": None,
        "功能费": None,
        "套餐内容_国内流量":None,
        "套餐内容_定向视频流量":None,
        "套餐内容_夜间闲时流量":None,
        "套餐内容_WLAN流量": None,
        "套餐内容_WLAN时长": None,
        "套餐内容_其他功能": None,
        "适用品牌": "全球通、动感地带、神州行",
        "超出处理_国内主叫":"0.19元/分钟，不收取漫游费",
        "超出处理_国内短信": "全球通、动感地带、神州行5元卡为0.1元/条；神州行升级版标准卡、畅听卡、家园卡为0.15元/条",
        "超出处理_国内彩信": "0.3元/条",
        "超出处理_国内流量": "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）",
        "结转规则_国内流量": "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
        "超出处理_WLAN流量": "0.01元/MB",
        "超出处理_WLAN时长": "0.01元/分钟计费。单个账号每月500元封顶，每月限40GB流量",
        "结转规则_WLAN流量": "不可结转分享",
        "结转规则_WLAN时长": "不可结转分享",
        "是否包含港澳台地区": "不包含港澳台",
        "能否结转滚存": "不能",
        "能否分享": "不能",
        "能否转赠": "不能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用限制":None,
        "使用有效期":None,
        "使用方式设置":None,
        "封顶规则": "套餐遵循500元、15G双封顶限制",
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "互斥业务": None,
        "开通客户限制": "北京移动全球通、动感地带、神州行升级版标准卡、畅听卡、家园卡、5元卡",
        "累次叠加规则": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "是否到期自动取消": "是",
        "能否变更或取消": "该套餐可以变更或取消",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "取消变更生效规则": "当月变更/取消，下月生效",
        "变更方式": None,
        "密码重置方式": "请拨打 10086 选择密码重置"
    }
    slot_excel_column_id={
        "子业务": 0,
        "主业务": 1,
        "产品介绍": 2,
        "计费方式": 3,
        "适用品牌": 4,
        "功能费": 5,
        "套餐内容_国内流量": 9,
        "套餐内容_定向视频流量":11,
        "套餐内容_夜间闲时流量":12,
        "套餐内容_WLAN流量": 13,
        "套餐内容_WLAN时长": 14,
        "套餐内容_其他功能": 15,
        "超出处理_国内流量": 19,
        "超出处理_WLAN流量": 21,
        "超出处理_WLAN时长": 22,
        "结转规则_国内流量": 26,
        "结转规则_WLAN流量": 28,
        "结转规则_WLAN时长": 29,
        "是否包含港澳台地区": 32,
        "能否结转滚存": 33,
        "能否分享": 34,
        "能否转赠": 36,
        "流量分享方式": 35,
        "流量转赠方式": 37,
        "转户转品牌管理": 38,
        "停机销号管理": 39,
        "赠送优惠活动": 40,
        "使用限制": 41,
        "使用有效期": 42,
        "使用方式设置": 43,
        "封顶规则": 44,
        "限速说明": 45,
        "受理时间": 46,
        "互斥业务": 47,
        "开通客户限制": 48,
        "累次叠加规则": 49,
        "开通方式": 50,
        "开通生效规则": 51,
        "是否到期自动取消": 53,
        "能否变更或取消": 54,
        "取消方式": 55,
        "取消变更生效规则": 56,
        "变更方式": 57,
        "密码重置方式":58
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        if table_values[0] == "":
            PrimaryItem = table_values

        for slot in Default_DataItemValues:
            if slot in WLAN_DB_slots:
                if table_values[slot_excel_column_id[slot]] != "":
                    DataItem[slot] = table_values[slot_excel_column_id[slot]]
                elif PrimaryItem[slot_excel_column_id[slot]] != "":
                    DataItem[slot] = PrimaryItem[slot_excel_column_id[slot]]
                else:
                    DataItem[slot] = Default_DataItemValues[slot]
        DataItem["结转规则"] = "WLAN 流量和 WLAN 时长均不可结转分享"
        DataItem["超出处理"] = "WLAN 流量超出后0.01元/MB，WLAN 时长超出后按照0.01元/分钟计费。单个账号每月500元封顶，每月限40GB流量"
        temp_str = "包含"
        for s in ["套餐内容_WLAN流量", "套餐内容_WLAN时长"]:
            if DataItem[s] !=None:
                if s == "套餐内容_其他功能":
                    temp_str += "%s，" % (DataItem[s])
                else:
                    temp_str += "%s%s，" %(s[5:], DataItem[s])
        temp_str = temp_str[:-1]
        DataItem["套餐内容"] = temp_str
        if DataItem["子业务"] != None:
            DataItem["主业务"] = None
            DataItem["计费方式"] = "%s，套餐内 WLAN 流量用尽后，超出部分0.01元/MB 或 0.01元/分钟，单个账号每月500元封顶，每月限40GB流量" % (DataItem["功能费"])
            if DataItem["产品介绍"] == None:
                DataItem["产品介绍"] = "%s: %s，套餐%s, 不包含港澳台" %(DataItem["子业务"], DataItem["功能费"], temp_str)
            if re.match(r"^KT.*",DataItem["开通方式"]):
                DataItem["变更方式"] = re.sub(r"^KT", "BG", DataItem["开通方式"])
        DataBaseList.append(copy.deepcopy(DataItem))

        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList

def extract_WLAN():
    """
    读取流量业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE WLAN("
    for slot in WLAN_DB_slots:
        if slot in ["功能费"]:
            exec_create_command += "%s NUMERIC," % slot
        else:
            exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_WLAN():
        print(data)
        if data["功能费"]:
            if data["功能费"] == "免费":
                data["功能费"] = 0
            else:
                m = re.match(r"(\d+).*", data["功能费"])
                data["功能费"] = int(m.group(1))

        exec_insert_command = "INSERT INTO WLAN (" +\
            ",".join([slot for slot in WLAN_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in WLAN_DB_slots:
            if slot in ["功能费",  "套餐内容_国内流量"]:
                if data[slot]  == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += str(data[slot])+','
            else:
                if data[slot] == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()

def excel_reader_Card():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('号卡业务')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []
    Default_DataItemValues = {
        "对应套餐":None,
        "产品介绍":None,
        "功能费": None,
        "套餐内容_国内流量":None,
        "套餐内容_定向视频流量":None,
        "套餐内容_夜间闲时流量":None,
        "套餐内容_WLAN流量": None,
        "套餐内容_WLAN时长": None,
        "套餐内容_其他功能": None,
        "适用品牌": "全球通、动感地带、神州行",
        "超出处理_国内主叫":"0.19元/分钟，不收取漫游费",
        "超出处理_国内短信": "全球通、动感地带、神州行5元卡为0.1元/条；神州行升级版标准卡、畅听卡、家园卡为0.15元/条",
        "超出处理_国内彩信": "0.3元/条",
        "超出处理_国内流量": "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）",
        "结转规则_国内流量": "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
        "超出处理_WLAN流量": "0.01元/MB",
        "超出处理_WLAN时长": "0.01元/分钟计费。单个账号每月500元封顶，每月限40GB流量",
        "结转规则_WLAN流量": "不可结转分享",
        "结转规则_WLAN时长": "不可结转分享",
        "是否包含港澳台地区": "不包含港澳台",
        "能否结转滚存": "不能",
        "能否分享": "不能",
        "能否转赠": "不能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用限制":None,
        "使用有效期":None,
        "使用方式设置":None,
        "封顶规则": "套餐遵循500元、15G双封顶限制",
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "互斥业务": None,
        "开通客户限制": "北京移动全球通、动感地带、神州行升级版标准卡、畅听卡、家园卡、5元卡",
        "累次叠加规则": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "是否到期自动取消": "是",
        "能否变更或取消": "该套餐可以变更或取消",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "取消变更生效规则": "当月变更/取消，下月生效",
        "变更方式": None,
        "密码重置方式": "请拨打 10086 选择密码重置",
        "激活方式": "为保证正常使用，请您在收货后的15天内拨打10086并按照语音提示进行激活。如未在指定的最晚激活时间之前进行激活操作，号码将自动销号。"
    }
    slot_excel_column_id={
        "号卡": 0,
        "对应套餐": 1,
        "产品介绍": 2,
        "适用品牌": 3,
        "功能费": 4,
        "套餐内容_国内主叫": 5,
        "套餐内容_国内短信":6,
        "套餐内容_国内流量":8,
        "套餐内容_定向视频流量":10,
        "套餐内容_夜间闲时流量":11,
        "套餐内容_WLAN流量": 12,
        "是否包含港澳台地区": 31,
        "能否结转滚存": 32,
        "能否分享": 33,
        "能否转赠": 35,
        "流量分享方式": 34,
        "流量转赠方式": 36,
        "主副卡处理": 37,
        "转户转品牌管理": 38,
        "停机销号管理": 39,
        "赠送优惠活动": 40,
        "使用限制": 41,
        "使用有效期": 42,
        "使用方式设置": 43,
        "封顶规则": 44,
        "限速说明": 45,
        "受理时间": 46,
        "互斥业务": 47,
        "开通客户限制": 48,
        "累次叠加规则": 49,
        "开通方式": 50,
        "开通生效规则": 51,
        "是否到期自动取消": 53,
        "能否变更或取消": 54,
        "取消方式": 55,
        "取消变更生效规则": 56,
        "变更方式": 57,
        "激活方式":58
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        for slot in Card_DB_slots:
            if slot in slot_excel_column_id and table_values[slot_excel_column_id[slot]] != "":
                DataItem[slot] = table_values[slot_excel_column_id[slot]]
            elif slot in Default_DataItemValues:
                DataItem[slot] = Default_DataItemValues[slot]
            else:
                DataItem[slot] = None
        DataItem["结转规则"] = "套餐内语音短信资源当月有效，未用完部分不累计到下月。当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转"
        DataItem["超出处理"] = "国内主叫0.19元/分钟，不收取漫游费，套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）"
        temp_str = "包含"
        for s in ["套餐内容_国内主叫", "套餐内容_国内短信", "套餐内容_国内流量",
                  "套餐内容_定向视频流量","套餐内容_夜间闲时流量", "套餐内容_WLAN流量"]:
            if DataItem[s] !=None:
                if s == "套餐内容_其他功能":
                    temp_str += "%s，" % (DataItem[s])
                else:
                    temp_str += "%s%s，" %(s[5:], DataItem[s])
        temp_str = temp_str[:-1]
        if temp_str != '包':
            DataItem["套餐内容"] = temp_str
        else:
            DataItem["套餐内容"] = None
        DataBaseList.append(copy.deepcopy(DataItem))
        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList

def extract_Card():
    """
    读取流量业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE Card("
    for slot in Card_DB_slots:
        if slot in ["功能费"]:
            exec_create_command += "%s NUMERIC," % slot
        else:
            exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_Card():
        print(data)
        if data["功能费"]:
            if data["功能费"] == "免费":
                data["功能费"] = 0
            else:
                m = re.match(r"(\d+).*", data["功能费"])
                data["功能费"] = int(m.group(1))

        exec_insert_command = "INSERT INTO Card (" +\
            ",".join([slot for slot in Card_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in Card_DB_slots:
            if slot in ["功能费"]:
                if data[slot]  == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += str(data[slot])+','
            else:
                if data[slot] == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()


def excel_reader_MultiTerminal():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('家庭及多终端')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []

    Default_DataItemValues = {
        "子业务":None,
        "主业务":None,
        "产品介绍":None,
        "计费方式": None,
        "适用品牌": "全球通、动感地带、神州行",
        "功能费": None,
        "副卡数量上限": None,
        "套餐内容_通话共享规则":None,
        "套餐内容_短信共享规则":None,
        "套餐内容_流量共享规则":None,
        "套餐内容_其他功能":None,
        "结转规则_国内流量": "当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
        "是否包含港澳台地区": "不包含港澳台",
        "能否结转滚存": "能",
        "能否分享": "能",
        "能否转赠": "能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用有效期":None,
        "封顶规则": None,
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "主卡互斥业务": None,
        "副卡互斥业务": None,
        "主卡开通客户限制": None,
        "副卡客户限制": None,
        "主卡套餐限制": None,
        "其他开通限制": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "主卡添加成员": None,
        "主卡删除成员": None,
        "副卡成员主动退出": None,
        "主卡查询副卡": None,
        "副卡查询主卡": None,
        "恢复流量功能": None,
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "取消变更生效规则": "当月变更/取消，下月生效",
        "能否变更或取消": "该套餐可以变更或取消",
        "是否到期自动取消": "不是",
        "是否自动顺延到下月": "是"
    }
    slot_excel_column_id={
        "子业务":0,
        "主业务":1,
        "产品介绍": 2,
        "计费方式": 3,
        "适用品牌": 4,
        "功能费": 5,
        "副卡数量上限": 6,
        "套餐内容_通话共享规则":7,
        "套餐内容_短信共享规则":8,
        "套餐内容_流量共享规则":9,
        "套餐内容_其他功能":10,
        "结转规则_国内流量": 11,
        "是否包含港澳台地区": 12,
        "能否结转滚存":13,
        "能否分享": 14,
        "能否转赠": 16,
        "流量分享方式": 15,
        "流量转赠方式" : 17,
        "转户转品牌管理": 18,
        "停机销号管理": 19,
        "赠送优惠活动": 20,
        "使用有效期":22,
        "封顶规则": 24,
        "限速说明": 25,
        "受理时间": 26,
        "主卡互斥业务": 27,
        "副卡互斥业务": 28,
        "主卡开通客户限制": 29,
        "副卡客户限制": 30,
        "主卡套餐限制": 31,
        "其他开通限制": 32,
        "开通方式": 33,
        "取消方式": 34,
        "主卡添加成员": 35,
        "主卡删除成员": 36,
        "副卡成员主动退出": 37,
        "主卡查询副卡": 38,
        "副卡查询主卡": 39,
        "恢复流量功能": 40,
        "开通生效规则": 41,
        "取消变更生效规则": 42,
        "是否自动顺延到下月": 43,
        "是否到期自动取消": 44,
        "能否变更或取消": 45,
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        if table_values[0] == "" or table_values[0] == " ":
            PrimaryItem = table_values

        for slot in Default_DataItemValues:
            if table_values[slot_excel_column_id[slot]] != ""and \
            table_values[slot_excel_column_id[slot]] != " ":
                DataItem[slot] = table_values[slot_excel_column_id[slot]]
            elif PrimaryItem[slot_excel_column_id[slot]] != ""and \
                    PrimaryItem[slot_excel_column_id[slot]] != " ":
                DataItem[slot] = PrimaryItem[slot_excel_column_id[slot]]
            else:
                DataItem[slot] = Default_DataItemValues[slot]
        temp_str = ""
        for s in ["套餐内容_通话共享规则", "套餐内容_短信共享规则",
                  "套餐内容_流量共享规则", "套餐内容_其他功能"]:
            if DataItem[s] !=None:
                temp_str += "%s：%s \n" %(s[5:], DataItem[s])
        DataItem["套餐内容"] = temp_str

        if DataItem["子业务"] != None:
            DataItem["主业务"] = None
        DataBaseList.append(copy.deepcopy(DataItem))

        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList


def extract_MultiTerminal():
    """
    读取家庭多终端业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE 家庭多终端("
    for slot in MultiTerminal_DB_slots:
        exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_MultiTerminal():
        print(data)
        exec_insert_command = "INSERT INTO 家庭多终端 (" +\
            ",".join([slot for slot in MultiTerminal_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in MultiTerminal_DB_slots:
            if data[slot] == None:
                exec_insert_command += 'NULL,'
            else:
                exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()


def excel_reader_Overseas():
    data = xlrd.open_workbook('NewOntology.xlsx')
    table = data.sheet_by_name('国际港澳台')  # 通过名称获取
    nrows = table.nrows
    DataBaseList = []

    Default_DataItemValues = {
        "子业务":None,
        "主业务":None,
        "产品介绍":None,
        "开通方向": None,
        "开通天数": None,
        "计费方式": None,
        "功能费": None,
        "套餐内容_通话时长": None,
        "套餐内容_短信": None,
        "套餐内容_彩信": None,
        "套餐内容_数据流量":None,
        "套餐内容_其他功能":None,
        "超出处理_通话时长": None,
        "超出处理_短信": None,
        "超出处理_数据流量":None,
        "能否结转滚存": "不能",
        "能否分享": "不能",
        "能否转赠": "不能",
        "流量分享方式": "登录移动APP客户端后，选择办理，点击“流量共享”，按提示操作即可",
        "流量转赠方式" : "登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
        "转户转品牌管理": None,
        "停机销号管理": "若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。",
        "赠送优惠活动": None,
        "使用限制": None,
        "封顶规则": None,
        "限速说明": None,
        "受理时间": "每月最后一天19点后无法办理",
        "互斥业务": None,
        "开通客户限制": None,
        "累次叠加规则": None,
        "开通方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式开通",
        "开通生效规则": "新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
        "是否到期自动取消": "是",
        "能否变更或取消": "该套餐可以变更或取消",
        "取消方式": "通过营业厅、10086人工、微厅、北京移动手机营业厅等方式取消",
        "到期失效规则": "到期自动失效"
    }
    slot_excel_column_id={
        "子业务":0,
        "主业务":1,
        "产品介绍": 2,
        "开通方向": 3,
        "开通天数": 4,
        "计费方式": 5,
        "功能费": 6,
        "套餐内容_通话时长": 7,
        "套餐内容_短信": 8,
        "套餐内容_彩信": 9,
        "套餐内容_数据流量":10,
        "套餐内容_其他功能":11,
        "超出处理_通话时长": 12,
        "超出处理_短信": 13,
        "超出处理_数据流量":14,
        "能否结转滚存": 15,
        "能否分享": 16,
        "能否转赠": 18,
        "流量分享方式": 17,
        "流量转赠方式" : 19,
        "转户转品牌管理": 20,
        "停机销号管理": 21,
        "赠送优惠活动": 22,
        "使用限制": 23,
        "封顶规则": 24,
        "限速说明": 25,
        "受理时间": 26,
        "互斥业务": 27,
        "开通客户限制": 28,
        "累次叠加规则": 29,
        "开通方式": 30,
        "开通生效规则": 31,
        "是否到期自动取消": 32,
        "能否变更或取消": 33,
        "取消方式": 34,
        "到期失效规则":35
    }

    for i in range(1, nrows):
        DataItem = {}
        table_values = table.row_values(i)
        if table_values[0] == "" or table_values[0] == " ":
            PrimaryItem = table_values

        for slot in Default_DataItemValues:
            if table_values[slot_excel_column_id[slot]] != ""and \
            table_values[slot_excel_column_id[slot]] != " ":
                DataItem[slot] = table_values[slot_excel_column_id[slot]]
            elif PrimaryItem[slot_excel_column_id[slot]] != ""and \
                    PrimaryItem[slot_excel_column_id[slot]] != " ":
                DataItem[slot] = PrimaryItem[slot_excel_column_id[slot]]
            else:
                DataItem[slot] = Default_DataItemValues[slot]
        DataItem["套餐内容"] = DataItem["产品介绍"]
        DataItem["超出处理"] = DataItem["超出处理_通话时长"]
        if DataItem["子业务"] != None:
            DataItem["主业务"] = None
        DataBaseList.append(copy.deepcopy(DataItem))

        # print(table.row_values(i))
        # DataItem = {'子业务':}
    return DataBaseList


def extract_Overseas():
    """
    读取国际港澳台业务，并存为数据库
    :return: 返回知识表 dict list
    """
    conn = sqlite3.connect("CMCC_NewDB.db")
    cur = conn.cursor()
    # create table
    exec_create_command = "CREATE TABLE 国际港澳台("
    for slot in Overseas_DB_slots:
        if slot in ["开通天数"]:
            exec_create_command += "%s NUMERIC," % slot
        else:
            exec_create_command += "%s TEXT ," % slot
    exec_create_command = exec_create_command[:-1]
    exec_create_command += ");"
    cur.execute(exec_create_command)

    for data in excel_reader_Overseas():
        print(data)
        if data["开通天数"]:
            m = re.match(r"(\d+).*", data["开通天数"])
            print(m)
            if m is not None:
                data["开通天数"] = int(m.group(1))
        exec_insert_command = "INSERT INTO 国际港澳台 (" +\
            ",".join([slot for slot in Overseas_DB_slots]) +")\n" +\
            "VALUES ("
        for slot in Overseas_DB_slots:
            if slot in ["开通天数"]:
                if data[slot]  == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += str(data[slot])+','
            else:
                if data[slot] == None:
                    exec_insert_command += 'NULL,'
                else:
                    exec_insert_command += '\''+data[slot]+'\','
        exec_insert_command = exec_insert_command[:-1]
        exec_insert_command += ')'
        print(exec_insert_command)
        cur.execute(exec_insert_command)

    # close DB
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # extract_TAOCAN()
    # extract_LIULIANG()
    # extract_WLAN()
    # extract_Card()
    # extract_MultiTerminal()
    extract_Overseas()