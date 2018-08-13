"""
自然语言生成，系统动作到语句的映射
"""
import sys
sys.path.append('..')
from data.DataManager import DataManager
from data.DataBase.Ontology import *

import random


special_slot_mapping = {
    "超出处理_国内主叫": "国内主叫超出处理规则",
    "超出处理_国内流量": "国内流量超出处理规则",
    "结转规则_国内主叫":"国内主叫结转规则",
    "结转规则_国内流量":"国内流量结转规则",
    "结转规则_赠送流量": "赠送流量结转规则",
    "停机销号管理": "停机销号管理规则"
}



def period_handler(nl, nl_to_add):
    if len(nl) == 0 :
        nl = nl_to_add
        return nl

    if nl[-1] in ['，', '、', '/'] :
        nl = nl[:-1]+'。'+nl_to_add
    elif nl[-1] in [ '。', '？', '\n', '；']:
        nl += nl_to_add
    else:
        nl += '。'+nl_to_add

    return nl



def rule_based_NLG(SysAct):
    def inform_template(content, offered_entity=None):
        nl = ''
        # 'inform' 的content为一个requestable slot组成的list
        if offered_entity is None:
            for req_slot in content:
                if req_slot in special_slot_mapping:
                    nl += '该套餐的' + special_slot_mapping[req_slot] + '为：'
                    nl += GLOBAL_slots[req_slot] + '；'
                elif '是否' in req_slot:
                    nl += '该套餐' + req_slot + '：' + GLOBAL_slots[req_slot] + '；'
                else:
                    nl += '该套餐的' + req_slot + '为：' + GLOBAL_slots[req_slot] + '；'
            nl = period_handler(nl, '') + '\n'
        else:
            prev_req_slot = []
            for req_slot in content:
                value = offered_entity[req_slot]
                if value == None: value = '无'

                if req_slot == '产品介绍':
                    value = offered_entity['产品介绍']
                    nl += value if '：' in value else '产品介绍：'+value
                    nl += '\n' if nl[-1] == '。' else '。\n'
                elif '_' in req_slot:
                    if '套餐内容' in req_slot:
                        if not '套餐内容' in prev_req_slot:
                            nl = period_handler(nl, '该套餐包括')
                        nl += req_slot[5:]
                        if '时长' in req_slot or '主叫' in req_slot:
                            value = 0 if value=='无' else value
                            nl += str(value) + '分钟，'
                        elif '流量' in req_slot:
                            value = 0 if value=='无' else value
                            nl += str(value) + 'MB，' #TODO: MB,GB的转换
                        elif '彩信' in req_slot or '短信' in req_slot:
                            value = 0 if value=='无' else value
                            nl += str(value) + '条，'
                        else:
                            nl += value+'，'
                    elif '结转规则' in req_slot:
                        if not '结转规则' in prev_req_slot:
                            nl = period_handler(nl, '该套餐的')
                        if value[-1] in ['。', '；']:
                            nl += req_slot[5:] + '结转规则为' + value
                        else:
                            nl += req_slot[5:] + '结转规则为' + value + '。'
                    elif '超出处理' in req_slot:
                        if not '超出处理' in prev_req_slot:
                            nl = period_handler(nl, '该套餐的')
                        if value[-1] in ['。', '；']:
                            nl += req_slot[5:] + '超出处理规则为' + value
                        else:
                            nl += req_slot[5:] + '超出处理规则为' + value + '。'
                elif '否' in req_slot:
                    nl = period_handler(nl, '该套餐' +  req_slot+'：' + value)
                else:
                    nl = period_handler(nl, '该套餐的' +  req_slot+'为' + value)
                prev_req_slot = req_slot

        return nl

    def request_template(content):
        nl = ''
        # 'request' 的content为一个informable slot组成的list
        if len(content) == 1: #只有1个request的情况
            slot = content[0]
            strategy = random.choice([0,1,2,3])
            if slot == '功能费':
                if strategy == 0:
                    nl += '您对套餐价格有什么要求吗？'
                elif strategy == 1:
                    nl += '想要什么价位的套餐？'
                elif strategy == 2:
                    nl += '您可以希望办理什么价格的套餐呢？'
                else:
                    nl += '那么您对套餐价格有什么要求？'
            elif slot == '套餐内容_国内主叫':
                if strategy in [0,1]:
                    nl += '您对套餐的国内主叫通话时长有什么要求？'
                else:
                    nl += '您需要包含多少分钟国内主叫通话时长的套餐呢？'
            elif slot == '套餐内容_国内流量':
                if strategy in [0,1]:
                    nl += '您对套餐包含的流量有什么要求？'
                else:
                    nl += '您每个月需要多少流量上网呢？'
            elif slot == '开通方向':
                if strategy in [0,1]:
                    nl += '您要去哪个国家旅行？'
                else:
                    nl += '您希望查询哪个国家的境外套餐资费呢？'
            else: pass  # 目前sysact只有这4个可能的request对象
        elif len(content) == 2:
            # 有2个request的情况
            # 目前只有["套餐内容_国内流量", "套餐内容_国内主叫"]这一种情况，针对这个写的NLG
            strategy = random.choice([0,1,2,3])
            if strategy in [0,1,2,3]:
                nl += '您对套餐包含的'
                for slot in content:
                    if '套餐内容' in slot:
                        slot = slot[5:]
                    nl += slot + '和'
                nl = nl[:-1] +'有什么要求呢？'
            else:
                pass
        else: pass #目前sysact只有1或2个request
        return nl

    def reqmore_template():
        nl = ''
        strategy = random.choice([0,1,2])
        if strategy == 0:
            nl += '请问您还有什么需要了解的吗？'
        elif strategy == 1:
            nl += '请问还有什么可以帮助您的？'
        elif strategy == 2:
            nl += '您还要查询该套餐的其他信息吗？'
        return nl

    nl = ''
    offered_entity = SysAct['offer'] if 'offer' in SysAct.keys() else None
    compared_entities = SysAct['offer_comp'] if 'offer_comp' in SysAct.keys() else None
    # for sysact_type, content in SysAct.items():
    if 'offer_comp' in SysAct.keys():
        nl += '您希望对比的套餐为：'
        for idx, entity in enumerate(compared_entities):
            nl += entity['子业务']
            nl +='、'
        nl = period_handler(nl, '') + '\n'
        if 'inform' in SysAct.keys():
            for req_slot in SysAct['inform']:
                nl += req_slot + '：\n'
                for idx, entity in enumerate(compared_entities):
                    nl += str(idx+1) + '. ' + entity['子业务'] + '：'
                    nl += inform_template([req_slot], offered_entity=entity)
                    nl = period_handler(nl, '') + '\n'
        if 'reqmore' in SysAct.keys():
            nl += reqmore_template()
            nl = period_handler(nl, '') + '\n'
        return nl
    if 'offer' in SysAct.keys():
        entity = SysAct['offer']
        if entity is not None:
            if isinstance(entity, dict) or (isinstance(entity, list) and len(entity)==1):
                if isinstance(entity, list): entity == entity[0]
                strategy = random.choice([0,1,2])
                if strategy == 0:
                    nl += '已为您找到业务：'+entity['子业务']
                elif strategy == 1:
                    nl += '符合您要求的业务是：'+entity['子业务']
                elif strategy == 2:
                    nl += entity['子业务']+'符合您的需求。'
                nl = period_handler(nl, '') + '\n'
                # 一个entity， 不return，等下面处理inform，request等act
            elif isinstance(entity, list):
                # 多个entity，一般为用户在查询，即inform的情况
                # 遍历sys act后return
                if 'inform' in SysAct.keys():
                    for req_slot in SysAct['inform']:
                        nl += req_slot + '：\n'
                        for idx, entity in enumerate(compared_entities):
                            nl += str(idx+1) + '. ' + entity['子业务'] + '：'
                            nl += inform_template([req_slot], offered_entity=entity)
                            nl = period_handler(nl, '') + '\n'
                if 'reqmore' in SysAct.keys():
                    nl += reqmore_template()
                    nl = period_handler(nl, '') + '\n'
                return nl
        else:
            nl += '没有找到符合您要求的业务，请尝试放松条件。'
            # TODO: 根据不同的user act，设置不同的sys act，以获得更独特的自然语言回复
            # 例： UsrAct == "更换"，回复“这个套餐已经是唯一的了”
            #        UsrAct == "要求更多"，回复“没有流量更多的套餐了”
            return nl
    if 'inform' in SysAct.keys():
        nl += inform_template(SysAct['inform'], offered_entity=offered_entity)
        nl = period_handler(nl, '') + '\n'
    if 'request' in SysAct.keys():
        nl += request_template(SysAct['request'])
        nl = period_handler(nl, '') + '\n'
    if 'reqmore' in SysAct.keys():
        nl += reqmore_template()
        nl = period_handler(nl, '') + '\n'
    if 'offerhelp' in SysAct.keys():
        nl += SysAct['domain'] + '领域的说明' #TODO: 问询说明的内容？
    if 'sorry' in SysAct.keys():
        nl += '未能找到满意答案，您可登录中国移动网上营业厅查找相关最新信息'
    if 'chatting' in SysAct.keys():
        strategy = random.choice([0,1,2])
        if strategy == 0:
            nl += '您好，我是中国移动业务咨询机器人，可以帮助您进行套餐查找、业务咨询、个人信息查询等，请问您需要什么帮助吗？'
        elif strategy == 1:
            nl += '抱歉，您说的这些我不太理解，但我可以在套餐查找、业务咨询、个人信息查询等方面为您提供帮助的~'
        else:
            nl += '请不要再调戏我了，问一些套餐查找、业务咨询、个人信息查询方面的问题吧'


    # if 'repeat' in SysAct.keys():
    #     nl += "抱歉，能再重述一遍么？"

    return nl


if __name__ == '__main__':
    data_manager = DataManager('../data/tmp')
    offer_entity = data_manager.SearchingByConstraints('套餐', {"功能费": [700, 900]})[0]
    compared_entities = data_manager.SearchingByConstraints('套餐', {"功能费": [700, 900]})
    domain = '套餐'
    SysAct = {
        'ex0': {
        'offer': offer_entity,
        'inform':['产品介绍', '套餐内容_国内主叫', '套餐内容_国内流量', '套餐内容_国内短信', '结转规则', '是否包含港澳台地区']},
         'ex1': #self.UsrAct == "告知":
         {'offer': offer_entity,
          'inform': ["产品介绍"],
          'reqmore': None,  # None 是因为 reqmore 没有参数
          'domain':domain},
        'ex2':
        {'request': ["套餐内容_国内流量", "套餐内容_国内主叫"],
                              'domain': domain},
        'ex3':
        {'request': ["功能费"],
                              'domain':domain},
        'ex4':
        {'offer_comp': compared_entities,
                      'inform': ["套餐内容", '套餐内容_国内流量', '取消方式'],
                      'reqmore': None,
                      'domain':domain},
        'ex5':
        {'offer': None,
                      'inform': ['产品介绍'],
                      'domain': domain},
        'ex6':
         {'offerhelp':None,
                  'domain': domain},
        'ex7':
        {'chatting': None,
                      'domain':domain}
    }
    nl = rule_based_NLG(SysAct['ex4'])
    print(nl)