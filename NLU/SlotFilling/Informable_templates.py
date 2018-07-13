"""
数值描述型的informable slots 预测
"""
from data.DataManager import DataManager
import os, re
Num_re = re.compile(r"(?P<thousand>[一二两三四五六七八九]+千)?"
                    r"(?P<hundred>[一二两三四五六七八九]+百)?零?"
                    r"(?P<ten>[一二三四五六七八九]+十)?零?"
                    r"(?P<one>[一二两三四五六七八九]*)")
# 功能费模板
cost_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)(?:多)?(?:元钱|元|块钱|块)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多)?(?:元钱|元|块钱|块)?")
cost_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
cost_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:了|消费)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?(?:[^起点些个下Gg兆Mm分小]|$)")
# 通话时长模板
time_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六time七八九十百千]+)(?:多个|多|个)?(?P<Metric1>分钟|小时|分|时|min|h)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多个|多|个)?(?P<Metric2>分钟|小时|分|时|min|h)")
time_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric1>分钟|小时|分|时|min|h)(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多个|多|个)?(?P<Metric2>分钟|小时|分|时|min|h)(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
time_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:时间|分钟数|分钟|打电话|通话|包打|包|打|主叫)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric>通话分钟|分钟|小时|分|时|min|h)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")
# 数据流量模板
data_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六time七八九十百千]+)(?:多个|多|个)?(?P<Metric1>MB|GB|gb|mb|M|G|兆|m|g)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多个|多|个)?(?P<Metric2>MB|GB|gb|mb|M|G|兆|m|g)")
data_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric1>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多个|多|个)?(?P<Metric2>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
data_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:流量|能有|包含|包流量|包|含|)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")

# # 开通天数模板， 目前暂不作为 informable slots
# days_re = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
#                       r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
#                       r"(?:流量|能有|包含|包流量|包|含|)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
#                      r"(?:多个|多|个)?(?P<Metric>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")

def Chinese2num(sent):
    """
    中文数字转英文数字，七八十，五百五，八十八，一千零五，一千五，一千零五十， 一千五百
    :param sent: 中文数字串
    :return: int list
    """
    if sent == "十":
        return [10]
    elif sent == "百":
        return [100]
    else:
        number = dict(zip("零一二两三四五六七八九",[0,1,2,2,3,4,5,6,7,8,9]))
        sent = re.sub(r"千([一二三四五六七八九])([^百]|$)", "千\g<1>百\g<2>", sent)
        sent = re.sub(r"百([一二三四五六七八九])([^十]|$)", "百\g<1>十\g<2>", sent)
        Nums = Num_re.findall(sent)
        num_list = []
        for num in Nums:
            if num[0]=="" and num[1]=="" and \
                num[2] == "" and num[3] == "":
                continue
            tmp = 0
            if len(num[0].rstrip('千'))>1:
                for ch in num[0].rstrip('千'):
                    num_list.append(number[ch]*1000)
            elif len(num[0].rstrip('千')) == 1:
                tmp += number[num[0].rstrip('千')]*1000
            if len(num[1].rstrip('百'))>1:
                for ch in num[1].rstrip('百'):
                    num_list.append(number[ch]*100)
            elif len(num[1].rstrip('百'))==1:
                tmp += number[num[1].rstrip('百')]*100
            if len(num[2].rstrip('十'))>1:
                for ch in num[2].rstrip('十'):
                    num_list.append(number[ch]*10)
            elif len(num[2].rstrip('十'))==1:
                tmp += number[num[2].rstrip('十')]*10
            if len(num[3])>1:
                for ch in num[3]:
                    num_list.append(number[ch])
            elif len(num[3])==1:
                tmp += number[num[3]]
            if tmp !=0:
                num_list.append(tmp)
        return num_list

def Cost_match(user_utter):
    """
    输入用户句子 ，输出匹配到的功能费范围， 否则返回None
    """
    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    if cost_re1.search(user_utter):
        data = cost_re1.search(user_utter)
        print('re1:', data)
        num_list = []
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num in [num1, num2]:
            num_list.append(num)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0]-50, 0), num_list[0]+50
        else:
            return num_list[0], num_list[-1]
    elif cost_re2.search(user_utter):
        num_list=[]
        data = cost_re2.search(user_utter)
        print('re2:', data)
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num in [num1, num2]:
            num_list.append(num)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0]-50, 0), num_list[0]+50
        else:
            return num_list[0], num_list[-1]
    elif cost_re3.search(user_utter):
        num_list = []
        for data in cost_re3.findall(user_utter):
            print('re3:',data)
            num = data[1]
            try:
                num_list.append(int(num))
            except Exception as e:
                num_list.extend(Chinese2num(num))
            scope = data[2]
            mostleast = data[0]
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0] - 50, 0), num_list[0] + 50
        else:
            return num_list[0], num_list[-1]
    return  None

def Time_match(user_utter):
    """
    输入用户句子 ，输出匹配到的通话时长范围， 否则返回None
    还返回去除掉 通话时间匹配span 的句子，因为 功能费 有时不带单位，剔除比较好
    """
    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    if time_re1.search(user_utter):
        data = time_re1.search(user_utter)
        user_utter = time_re1.sub("",user_utter)
        print('re1:', data)
        num_list = []
        if data.group("Metric2") == "小时" or data.group("Metric2") == "时" or data.group("Metric2") == "h":
            metric2 = 60
        else:
            metric2 = 1
        if data.group("Metric1") == "小时" or data.group("Metric1") == "时" or data.group("Metric1") == "h":
            metric1 = 60
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num,metric in [num1,metric1],[num2, metric2]:
            num_list.append(num*metric)
        num_list = sorted(list(set(num_list)))

        if len(num_list) == 1:
            return max(num_list[0] - 100, 0), num_list[0] + 100, user_utter
        else:
            return num_list[0], num_list[-1], user_utter
    elif time_re2.search(user_utter):
        num_list = []
        data = time_re2.search(user_utter)
        user_utter = time_re2.sub("",user_utter)
        print('re2:', data)
        if data.group("Metric2") == "小时" or data.group("Metric2") == "时" or data.group("Metric2") == "h":
            metric2 = 60
        else:
            metric2 = 1
        if data.group("Metric1") == "小时" or data.group("Metric1") == "时" or data.group("Metric1") == "h":
            metric1 = 60
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num,metric in [num1,metric1],[num2, metric2]:
            num_list.append(num*metric)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0] - 100, 0), num_list[0] + 100, user_utter
        else:
            return num_list[0], num_list[-1], user_utter
    elif time_re3.search(user_utter):
        num_list = []
        for data in time_re3.findall(user_utter):
            print('re3:', data)
            num = data[1]
            metric = data[2]
            if metric == "小时" or metric == "时" or metric == "h":
                metric = 60
            else:
                metric = 1
            try:
                num_list.append(int(num)*metric)
            except Exception as e:
                num_list.extend([i*metric for i in Chinese2num(num)])
            scope = data[3]
            mostleast = data[0]
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        newsent = time_re3.sub("", user_utter)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0] - 100, 0), num_list[0] + 100, newsent
        else:
            return num_list[0], num_list[-1], newsent
    return None

def Data_match(user_utter):
    """
    输入用户句子 ，输出匹配到的流量范围， 否则返回None
    """
    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    if data_re1.search(user_utter):
        data = data_re1.search(user_utter)
        user_utter = data_re1.sub("", user_utter)
        print('re1:', data.groups())
        num_list = []
        if data.group("Metric2") != None and re.match(r"(GB|G|gb|g)", data.group("Metric2")):
            metric2 = 1024
        else:
            metric2 = 1
        if data.group("Metric1") != None and re.match(r"(GB|G|gb|g)", data.group("Metric1")):
            metric1 = 1024
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num, metric in [num1, metric1], [num2, metric2]:
            num_list.append(num * metric)
        num_list = sorted(list(set(num_list)))

        if len(num_list) == 1:
            return max(num_list[0] - 200, 0), num_list[0] + 200, user_utter
        else:
            return num_list[0], num_list[-1], user_utter
    elif data_re2.search(user_utter):
        num_list = []
        data = data_re2.search(user_utter)
        user_utter = data_re2.sub("", user_utter)
        print('re2:', data)
        if data.group("Metric2") != None and re.match(r"GB|G|gb|g", data.group("Metric2")):
            metric2 = 1024
        else:
            metric2 = 1
        if data.group("Metric1") != None and re.match(r"GB|G|gb|g", data.group("Metric1")):
            metric1 = 1024
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num, metric in [num1, metric1], [num2, metric2]:
            num_list.append(num * metric)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0] - 200, 0), num_list[0] + 200, user_utter
        else:
            return num_list[0], num_list[-1], user_utter
    elif data_re3.search(user_utter):
        num_list = []
        for data in data_re3.findall(user_utter):
            print('re3:', data)
            num = data[1]
            metric = data[2]
            if metric != None and re.match(r"GB|G|gb|g", metric):
                metric = 1024
            else:
                metric = 1
            try:
                num_list.append(int(num) * metric)
            except Exception as e:
                num_list.extend([i * metric for i in Chinese2num(num)])
            scope = data[3]
            mostleast = data[0]
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        newsent = data_re3.sub("", user_utter)
        num_list = sorted(list(set(num_list)))
        if len(num_list) == 1:
            return max(num_list[0] - 200, 0), num_list[0] + 200, newsent
        else:
            return num_list[0], num_list[-1], newsent
    return None

def Match_Cost_Time_Data(user_utter):
    """
    通话时长和数据流量是一定要有单位的，功能费则不一定，因此最后判断
    """
    time = Time_match(user_utter)
    if time != None:
        user_utter = time[2]
    data = Data_match(user_utter)
    if data != None:
        user_utter = data[2]
    cost = Cost_match(user_utter)
    results = {}
    if cost != None:
        results["功能费"] = (cost[0], cost[1])
    if data != None:
        results["套餐内容_国内流量"] = (data[0], data[1])
    if time != None:
        results["套餐内容_国内主叫"] = (time[0], time[1])
    return results


def Country_match(user_utter):
    """
    输入用户句子 ，输出匹配到的开通方向， 否则返回None
    TODO 此函数由张亦驰来补充, 主要就是匹配一些国家名和地区名，比较容易
    """
    return {"开通国家":"","开通地区":""}

if __name__ == '__main__':
    data_manager = DataManager('../../data/tmp')
    for sent in data_manager.DialogData['id116']["用户回复示例"]:
            print(sent, '|', data_manager.WordSegmentCut(sent))
