"""
对话状态跟踪、维护对话历史

四个业务实体集合：用户主动提及集合（保留两轮）、用户个人业务集合、数据库查询结果、系统提供结果集合（保留一轮）
所有领域的 belief states（累计） 和 requested slots(保留两轮)、领域检测结果（保留两轮）、 用户动作结果（保留两轮）

是否 DST 不变、是否用户重复表述同一句话、情感检测结果

"""
import sys
sys.path.append('../..')
# from collections import deque
from NLU.NLUManager import *

class BeliefState():
    pass
DialogStateSample = {
    'TurnNum':int,
    # 用户主动提及业务实体集合
    'EntityMentioned': {'curr_turn': [],
                        'prev_turn': []},
    'UserPersonal': {
            "已购业务": ["180元档幸福流量年包", "18元4G飞享套餐升级版"], # 这里应该是完整的业务的信息dict
            "使用情况": "剩余流量 11.10 GB，剩余通话 0 分钟，话费余额 110.20 元，本月已产生话费 247.29 元",
            "号码": "18811369685",
            "归属地" : "北京",
            "品牌": "动感地带",
            "是否转品牌过渡期": "否",
            "话费查询": "话费余额 110.20 元",
            "流量查询": "剩余流量 11.10 GB",
            "订购时间": "订购时间 2017-04-04， 生效时间 2017-05-01",
            "是否停机": "否",
            "话费充值": "请登录网上营业厅、微厅或 APP 充值",
            "流量充值": "请登录网上营业厅、微厅或 APP 充值",
            "账单查询": "请登录网上营业厅、微厅或 APP 查询"
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
        # dialog state objects
        self.EntityMentioned =  {'curr_turn': None,  'prev_turn': None}
        self.UserPersenal = usr_personal
        self.QueryResult = None
        self.SystemReturnAct = None
        self.BeliefState = {'curr_turn': None,  'prev_turn': None}
        self.RequestedSlot = {'curr_turn': None,  'prev_turn': None}
        self.DetectedDomain = {'curr_turn': None,  'prev_turn': None}
        self.UserAct = {'curr_turn': None,  'prev_turn': None}
        self.TurnNum = 0
        self.DialogState = {
            'TurnNum': self.TurnNum,
            'EntityMentioned': self.EntityMentioned,
            'UserPersenal': self.UserPersenal,
            'QueryResult': self.QueryResult,
            'SystemReturnAct': self.SystemReturnAct,
            'BeliefState': self.BeliefState,
            'RequestedSlot': self.RequestedSlot,
            'DetectedDomain':self.DetectedDomain,
            'UserAct': self.UserAct
        }
        # status variables
        self.isDSTChange = True
        self.isUtterSame = False
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
        self.TurnNum += 1
        # 复制上一轮的dialog state到prev_turn
        for key,value in self.DialogState.items():
            if 'prev_turn' in value.keys():
                value['prev_turn'] = value['curr_turn']

        # 利用本轮NLU结果更新当前轮的dialog state
        self.EntityMentioned['curr_turn'] = NLU_results['entity']
        self.BeliefState['curr_turn'] = NLU_results['informable']
        self.RequestedSlot['curr_turn'] = NLU_results['requestable']
        self.DetectedDomain['curr_turn'] =NLU_results['domain']
        self.UserAct['curr_turn'] = NLU_results['useract']
        # TODO: sentiment
        # self.detected_sentiment = ?

        self.UserPersenal = self.UserPersenal  #个人信息不变
        self.QueryResult = DataManager.SearchingByConstraints(
            table=NLU_results['domain'], feed_dict=NLU_results['informable'])
        self.SystemReturnAct = rule_policy.Reply(self.DialogState)

        self.isUtterSame = True if self.user_utter == NLU_results['userutter'] else False

        self.isDSTChange = False
        for key,value in self.DialogState.items():
            if 'prev_turn' in value.keys():
                if value['prev_turn'] != value['curr_turn']:
                    self.isDSTChange = True

        pass





if __name__ == '__main__':
    dst = DialodStateTracker(usr_personal)
    dst.MentionedEntitySet.append(1)
    dst.MentionedEntitySet.append(2)
    dst.MentionedEntitySet.append(3)
    print(dst.MentionedEntitySet)
