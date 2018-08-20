"""
对话状态跟踪、维护对话历史

四个业务实体集合：用户主动提及集合（保留两轮）、用户个人业务集合、数据库查询结果、系统提供结果集合（保留一轮）
所有领域的 belief states（累计） 和 requested slots(保留两轮)、领域检测结果（保留两轮）、 用户动作结果（保留两轮）

是否 DST 不变、是否用户重复表述同一句话、情感检测结果

"""
import os
import sys
import copy
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../..'))
# from collections import deque
from NLU.NLUManager import *
from DM.policy.RuleMapping import *

main_bussiness_dict = ['畅享套餐', '畅享不限量套餐','88商旅套餐', '4G飞享套餐升级版', '4G短信包',
                            '短信包套餐', '和4G套餐', '动感地带可选套餐', '神州行可选套餐', '全球通专属数据包',
                            '4G数据终端资费套餐', '畅游包', ' 数据流量加油包', '夜间流量套餐', '数据流量实体卡',
                            '流量小时包', '流量日包', '流量季包', '流量半年包', '幸福流量年包', '4G上网卡',
                            '任我用流量套餐', '月末流量安心包', '流量月末包', '移动数据流量不限流量叠加包',
                            '流量安心套餐', '假日流量包', '7天手机视频流量包', '手机视频流量包', '地铁流量包',
                            '任我看视频流量包', 'WLAN标准套餐', 'WLAN流量套餐', 'WLAN校园套餐',
                            '和家庭分享', '家庭计划', '多终端分享', '和校园', '亲情通',
                            '国际/港澳台漫游', '多国/大包多天流量包', '港澳台三地畅游包', '数据流量包',
                            '2018俄罗斯世界杯特惠包', '“海外随心看”日套餐']
card_dict = ['4G包年卡', '4G飞享卡', '4G任我用卡', '4G爱家卡', '8元卡', '万能副卡']

DB_tables = ['套餐', '流量', 'WLAN',  '国际港澳台', '家庭多终端']


DialogStateSample = {
    'TurnNum':int,
    # 用户主动提及业务实体集合
    'EntityMentioned': {'curr_turn': [],
                        'prev_turn': []},
    'UserPersonal': {'111':111
        }, # 个人信息，dict
    'QueryResults': [], # 查询数据库得到的list of 业务信息dict
    # 一轮就提供一个套餐
    'OfferedResult': {'prev_turn':{'子业务': '188元畅享套餐', '主业务': None, '功能费': 188, '套餐内容_国内主叫': 700, '套餐内容_国内流量': 12288},
                    'preprev_turn': {'子业务': '188元畅享套餐', '主业务': None, '功能费': 188, '套餐内容_国内主叫': 700, '套餐内容_国内流量': 12288}},
    'SystemAct': {'curr_turn': {'offer': {'子业务': '158元畅享套餐', '主业务': None, '功能费': 158, '套餐内容_国内主叫': 700, '套餐内容_国内流量': 6144},
                                      'inform':['适用品牌', '产品介绍']},
                     'prev_turn': {}},
    'BeliefState': {'curr_turn':{"功能费": [150, 300]},
                    'prev_turn':{"功能费": [150, 300]}},
    'RequestedSlot': {'curr_turn': ["套餐内容_国内流量", "副卡客户限制"],
                      'prev_turn': []},
    'DetectedDomain': {'curr_turn': "套餐",
                         'prev_turn': None},
    'UserAct': {'curr_turn': "告知",
                'prev_turn': None}
}


class DialogStateTracker:
    def __init__(self, usr_personal):
        self.DialogState = {
            'TurnNum': 0,
            'EntityMentioned': {'curr_turn': [],  'prev_turn': []},
            'UserPersenal': usr_personal,
            'QueryResults': [],
            'OfferedResult': {'curr_turn': {},  'prev_turn': {}},
            'SystemAct': {'curr_turn': {},  'prev_turn': {}},
            'BeliefState':{'curr_turn': {},  'prev_turn': {}},
            'RequestedSlot':{'curr_turn': [],  'prev_turn': []},
            'DetectedDomain': {'curr_turn': None,  'prev_turn': None},
            'UserAct': {'curr_turn': None,  'prev_turn': None}
        }
        # status variables
        self.isDSTChange = True
        self.isOfferedEntityChange = True
        self.isUtterChange = True
        self.detected_sentiment = None
        self.user_utter = None

    def update(self, NLU_results, rule_policy, data_manager):
        """
        NLU_results 包含
        Dom_results, ER_results, Senti_results, UserAct_results,
        Slot_filling_results, user_utter
        :param NLU_results: dict
        :param data_manager: data_manager
        """
        self.DialogState['TurnNum'] += 1
        # 复制上一轮的dialog state到prev_turn
        for key,value in self.DialogState.items():
            if isinstance(value,dict) and 'prev_turn' in value.keys():
                value['prev_turn'] = copy.deepcopy(value['curr_turn'])

        # 利用本轮NLU结果更新当前轮的dialog state
        self.DialogState['RequestedSlot']['curr_turn'] = NLU_results['requestable']
        self.DialogState['DetectedDomain']['curr_turn'] =NLU_results['domain'][0]
        self.DialogState['UserAct']['curr_turn'] = NLU_results['useract'][0]
        for slot, value in NLU_results['informable'].items():
            self.DialogState['BeliefState']['curr_turn'][slot] = value
        # TODO: sentiment
        # self.detected_sentiment = ?
        self.DialogState['EntityMentioned']['curr_turn']= []
        if NLU_results['entity']:
            QueryResults = []
            for entity_name in NLU_results['entity']:
                if entity_name in main_bussiness_dict:
                    for table in DB_tables:
                        ent = data_manager.SearchingByEntity(
                            table=table, feed_dict={'主业务':entity_name})
                        QueryResults += ent
                        self.DialogState['EntityMentioned']['curr_turn'] += ent
                elif entity_name in card_dict:
                    ent += data_manager.SearchingByEntity(
                        table='Card', feed_dict={'号卡':entity_name})
                    QueryResults += ent
                    self.DialogState['EntityMentioned']['curr_turn'] += ent
                else:
                    for table in DB_tables:
                        ent = data_manager.SearchingByEntity(
                            table=table, feed_dict={'子业务':entity_name})
                        QueryResults += ent
                        self.DialogState['EntityMentioned']['curr_turn'] += ent
        else:
            QueryResults = data_manager.SearchingByConstraints(
                table=self.DialogState['DetectedDomain']['curr_turn'],
                feed_dict=self.DialogState['BeliefState']['curr_turn'])
        self.DialogState['QueryResults'] = QueryResults

        #self.DialogState['UserPersenal'] = self.UserPersenal  #个人信息不变

        # 最后更新system act
        self.DialogState['SystemAct']['curr_turn'] = rule_policy.Reply(self.DialogState)
        if self.DialogState['SystemAct']['curr_turn'] == None:
            self.DialogState['SystemAct']['curr_turn'] = {}

        if 'offer' in self.DialogState['SystemAct']['curr_turn'].keys():
            self.DialogState['OfferedResult']['curr_turn'] = \
            self.DialogState['SystemAct']['curr_turn']['offer']
        else:
            self.DialogState['OfferedResult']['curr_turn'] = \
            self.DialogState['OfferedResult']['prev_turn']

        # 状态判断量的更新
        self.isUtterChange = False if self.user_utter == NLU_results['userutter'] else True
        self.isDSTChange = False
        for key,value in self.DialogState.items():
            if isinstance(value, dict) and 'prev_turn' in value.keys():
                if value['prev_turn'] != value['curr_turn']:
                    self.isDSTChange = True
        self.isOfferedEntityChange = False if self.DialogState['OfferedResult']['curr_turn'] == \
           self.DialogState['OfferedResult']['prev_turn'] else True

    def dialog_state_print(self):
        # dialog state printer
        def print_entity(self, dst_key_name):
            temp = ' - ' + dst_key_name + '\n'
            for turn in ['prev_turn', 'curr_turn']:
                entity = self.DialogState[dst_key_name][turn]
                temp += '   '+turn+': '
                if isinstance(entity, list):
                    for ent in entity:
                        if '子业务' in ent and '子业务' is not None:
                            temp += str(ent['子业务']) + ', '
                        elif '主业务' in ent and '主业务' is not None:
                            temp +=str(ent['主业务']) + ', '
                        else:
                            temp += 'None, '
                    temp = temp[:-2] + '\n'
                elif isinstance(entity, dict):
                    ent = entity
                    if '子业务' in ent and '子业务' is not None:
                        temp += str(ent['子业务']) + '\n'
                    elif '主业务' in ent and '主业务' is not None:
                        temp +=str(ent['主业务']) + '\n'
                    else:
                        temp += 'None\n'
                elif entity is None:
                    temp += 'None\n'
                else:
                    raise ValueError('invalid entity type')
            return temp

        def print_QR(self):
            QR = self.DialogState['QueryResults']
            temp = ' - QueryResults\n'
            for ent in QR:
                if isinstance(ent, dict):
                    if '子业务' in ent and '子业务' is not None:
                        temp += '   '+str(ent['子业务']) + '\n'
                    elif '主业务' in ent and '主业务' is not None:
                        temp += '   '+str(ent['主业务']) + '\n'
            return temp

        def print_NLU(self, dst_key_name):
            temp = ' - ' + dst_key_name + '\n'
            for turn in ['prev_turn', 'curr_turn']:
                result = self.DialogState[dst_key_name][turn]
                temp += '   '+turn+': ' + str(result) + '\n'
            return temp

        def print_sysact(self):
            SysAct = self.DialogState['SystemAct']
            temp = ' - SystemAct\n'
            # print(SysAct)
            for turn in ['prev_turn', 'curr_turn']:
                temp += '   '+turn+': \n'
                for sysact, content in SysAct[turn].items():
                    temp += '      '+sysact+'  '
                    if sysact == 'offer':
                        if isinstance(content, dict):
                            if '子业务' in content and '子业务' is not None:
                                temp += str(content['子业务']) + '\n'
                            elif '主业务' in content and '主业务' is not None:
                                temp +=str(content['主业务']) + '\n'
                        else:
                            temp += 'None\n'
                    elif sysact == 'offer_comp':
                        for ent in content:
                            if isinstance(ent, dict):
                                if '子业务' in ent and '子业务' is not None:
                                    temp += str(ent['子业务']) + ', '
                                elif '主业务' in ent and '主业务' is not None:
                                    temp +=str(ent['主业务']) + ', '
                            else:
                                temp += 'None, '
                        temp = temp[:-2] + '\n'
                    else:
                        temp += str(content)+'\n'
            return temp

        print('Dialog State in turn %d:' %self.DialogState['TurnNum'])
        print(print_entity(self, 'EntityMentioned'))
        print(print_QR(self))
        print(print_entity(self, 'OfferedResult'))
        print(print_NLU(self, 'DetectedDomain'))
        print(print_NLU(self, 'UserAct'))
        print(print_NLU(self, 'RequestedSlot'))
        print(print_NLU(self, 'BeliefState'))
        print(print_sysact(self))
        print(' - isDSTChange:' + str(self.isDSTChange) + '\n')
        print(' - isUtterChange:' + str(self.isUtterChange) + '\n')
        print(' - isOfferedEntityChange:' + str(self.isOfferedEntityChange) + '\n')




if __name__ == '__main__':
    dst = DialogStateTracker(DialogStateSample['UserPersonal'])
    data_manager = DataManager('../../data/tmp')
    rule_policy = RulePolicy()
    NLU_results = {
    'domain': ('套餐', 0.67),
    'useract': ('问询',  0.99),
    'informable': {"功能费": [500, 700]},
    'requestable': ['套餐内容', '产品介绍'],
    'entity': ['188元畅享套餐'],
    'sentiment':None,
    'userutter': '畅享套餐，188元那个，介绍一下'
    }
    NLU_results2 = {
    'domain': ('套餐', 0.17),
    'useract': ('问询',  0.89),
    'informable': {"功能费": [100, 400]},
    'requestable': ['套餐内容'],
    'entity': [],
    'sentiment':None,
    'userutter': 'hhhhhhhh'
    }
    NLU_results3 = {
    'domain': ('套餐', 0.19),
    'useract': ('比较',  0.44),
    'informable': {"功能费": [100, 150]},
    'requestable': ['套餐内容'],
    'entity': ['88元畅享套餐', '288元畅享套餐'],
    'sentiment':None,
    'userutter': 'hhhhhhhh'
    }
    dst.update(NLU_results, rule_policy, data_manager)
    dst.dialog_state_print()
    dst.update(NLU_results2, rule_policy, data_manager)
    dst.dialog_state_print()
    dst.update(NLU_results3, rule_policy, data_manager)
    dst.dialog_state_print()
