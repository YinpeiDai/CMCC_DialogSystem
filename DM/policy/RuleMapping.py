"""
基于规则的policy
"""
import sys
sys.path.append('../..')
from data.DataBase.Ontology import *
from data.DataManager import DataManager
import copy

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

def Ask_more_or_less(required_slots, KB_results, KB_pointer, UsrAct):
    """
    根据用户要求，从搜索结果 QueryResults 中找出一个符合要求的
    :param required_slots:
    :param KB_results:
    :param KB_pointer:
    :param UsrAct:
    :return:
    """
    slot = required_slots[0] # 取第一个排序
    if len(KB_results) == 0:
        return None
    if UsrAct == "要求更多":
        KB_results.sort(key=lambda x:x[slot],reverse=True)
        if KB_pointer == KB_results[0]:
            return None
        else:
            return KB_results[0]
    else:
        KB_results.sort(key=lambda x: x[slot], reverse=False)
        if KB_pointer == KB_results[0]:
            return None
        else:
            return KB_results[0]

class RulePolicy:
    def __init__(self):
        self.not_mentioned_informable_slots = \
            ["功能费", "套餐内容_国内流量", "套餐内容_国内主叫", "开通方向"]
        self.DislikeResults = [] # 用户明确说不要某业务，就存到这里

    def Reply(self, CurrrentDialogState):
        """
        return System Action for NLG
        :param CurrrentDialogState: 对话状态
        :return: dict
        """
        # 根据 BeliefState 更新 未提及的 informable slots
        self.informable_slots = CurrrentDialogState["BeliefState"]["curr_turn"]
        if CurrrentDialogState["BeliefState"]["curr_turn"] ==\
                CurrrentDialogState["BeliefState"]["prev_turn"]:
            self.IsInformableSlotChanged = False
        else:
            self.IsInformableSlotChanged = True
        if ("功能费" in self.informable_slots  or
            "功能费_文字描述" in self.informable_slots) and \
                "功能费" in self.not_mentioned_informable_slots:
            self.not_mentioned_informable_slots.remove("功能费")
        if ("套餐内容_国内主叫" in self.informable_slots
            or "套餐内容_国内主叫_文字描述" in self.informable_slots)  and\
                "套餐内容_国内主叫" in self.not_mentioned_informable_slots:
            self.not_mentioned_informable_slots.remove("套餐内容_国内主叫")
        if ("套餐内容_国内流量" in self.informable_slots or
            "套餐内容_国内流量_文字描述" in self.informable_slots)  and\
                "套餐内容_国内流量" in self.not_mentioned_informable_slots:
            self.not_mentioned_informable_slots.remove("套餐内容_国内流量")
        if "开通方向" in self.informable_slots and \
                "开通方向" in self.not_mentioned_informable_slots:
            self.not_mentioned_informable_slots.remove("开通方向")

        self.domain = CurrrentDialogState["DetectedDomain"]["curr_turn"]
        self.UsrAct = CurrrentDialogState['UserAct']['curr_turn']
        self.last_SysAct = CurrrentDialogState['SystemAct']['curr_turn'].keys()
        self.requestable_slots = set(CurrrentDialogState["RequestedSlot"]["curr_turn"])
        self.ER = copy.deepcopy(CurrrentDialogState["EntityMentioned"]["curr_turn"])
        self.KB_results = copy.deepcopy(CurrrentDialogState["QueryResults"])
        self.KB_pointer = copy.deepcopy(CurrrentDialogState["OfferedResult"]["prev_turn"])

        if len(self.ER) > 0: self.offer = self.ER # 业务实体优先填充
        # 如果 belief_states 更新了，KB_resluts 也找到了，拿第一个填充
        elif len(self.KB_results) > 0 and self.IsInformableSlotChanged:
            for item in self.KB_results:
                if item not in self.DislikeResults:
                    self.offer = item
                    break
        else: self.offer = None
        if self.UsrAct == "告知":
            if self.offer != None:
                SysAct = {'offer': self.offer,
                          'inform': ["产品介绍"],
                          'reqmore': None,  # None 是因为 reqmore 没有参数
                          'domain':self.domain}
                #  NLG 的实现例如 "***套餐价格... 您有什么需要了解的?"
                return SysAct

            # 系统问询一到两个 informable slot
            if self.domain == "套餐" or self.domain == "流量":
                if "功能费" in self.not_mentioned_informable_slots:
                    SysAct = {'request': ["功能费"],
                              'domain': self.domain} # 例如 "想要多少钱的套餐，对价位有要求吗？"
                    return SysAct
                if "套餐内容_国内流量" in self.not_mentioned_informable_slots and "套餐内容_国内主叫" in self.not_mentioned_informable_slots:
                    SysAct = {'request': ["套餐内容_国内流量", "套餐内容_国内主叫"],
                              'domain': self.domain} # 例如 "想要多少流量的套餐， 一般每月通话多少分钟"
                    # TODO: 在 NLG 中需要判断一下 如果 domain == 流量，就不说 套餐内容_国内主叫
                    return SysAct
            elif self.domain == "国际港澳台":
                if "开通方向" in self.not_mentioned_informable_slots:
                    SysAct = {'request': ["开通方向"],
                              'domain': self.domain} # 例如 "请问您是去哪个国家或地区"
                    return SysAct
            elif self.domain == "WLAN":
                if "功能费" in self.not_mentioned_informable_slots:
                    SysAct = {'request': ["功能费"],
                              'domain': self.domain} # 例如 "想要多少价格的WLAN套餐？"
                    return SysAct
        elif self.UsrAct == "问询":
            if self.offer != None:
                if self.domain == "家庭多终端":
                    if "能否分享" in self.requestable_slots:
                        self.requestable_slots.remove("能否分享")
                        self.requestable_slots.add("套餐内容_通话共享规则")
                        self.requestable_slots.add("套餐内容_短信共享规则")
                        self.requestable_slots.add("套餐内容_流量共享规则")
                    if "互斥业务" in self.requestable_slots:
                        self.requestable_slots.remove("互斥业务")
                        self.requestable_slots.add("主卡互斥业务")
                        self.requestable_slots.add("副卡互斥业务")
                        self.requestable_slots.add("套餐内容_流量共享规则")
                    if "开通客户限制" in self.requestable_slots:
                        self.requestable_slots.remove("开通客户限制")
                        self.requestable_slots.add("主卡开通客户限制")
                        self.requestable_slots.add("副卡客户限制")
                        self.requestable_slots.add("主卡套餐限制")
                        self.requestable_slots.add("其他开通限制")
                # 对一些 slot 增加一些补充
                if "限速说明" in self.requestable_slots:
                    self.requestable_slots.add("封顶说明")
                if "适用品牌" in self.requestable_slots:
                    self.requestable_slots.add("互斥业务")

                SysAct = {'offer': self.offer,
                          'inform': list(self.requestable_slots),
                          'domain':self.domain }  # 例如 "***套餐的***是***" 语句要尽量自然
                return SysAct
            else:
                # 只返回具有一定普适性的问询槽
                SysAct = {'inform': [i for i in self.requestable_slots if i in GLOBAL_slots ],
                          'domain': self.domain}  # 例如 "***套餐的***是***" 语句要尽量自然
                return SysAct
        elif self.UsrAct == "比较":
            # 比较不同的套餐
            # 先考虑用户主动提及集合
            if len(CurrrentDialogState["EntityMentioned"]["curr_turn"]) > 1:
                self.compared_entities = CurrrentDialogState["EntityMentioned"]["curr_turn"]
            # 再考虑对话系统提供的业务实体集
            elif self.KB_pointer != CurrrentDialogState["OfferedResult"]["prev_turn"]:
                self.compared_entities = [self.KB_pointer, CurrrentDialogState["OfferedResult"]["prev_turn"]]
            else: # 最后是个人业务
                self.compared_entities = CurrrentDialogState["UserPersonal"]["已购业务"]
            SysAct = {'offer_comp': self.compared_entities,
            # 比较这里的offer是entity的list，和offer不同，定义成一个新的sysact: offer_comp
                      'inform': ["套餐内容"],
                      'reqmore': None,
                      'domain':self.domain}  # 把这几个业务都介绍一下
                      # zyc: 这里inform定死为套餐内容，但实际可能只对比流量或者通话时长之类的
            return SysAct
        elif self.UsrAct == "要求更多" or self.UsrAct == "要求更少":
            # 此用户动作仅限以下slot
            required_slots = ["功能费", "套餐内容_国内流量", "套餐内容_国内主叫"]
            for i in required_slots:
                if i not in self.requestable_slots:
                    required_slots.remove(i)
                self.new_offer = Ask_more_or_less(required_slots, self.KB_results, self.KB_pointer, self.UsrAct)
                # new_offer 可能是None， 如果没有更多或者更少的了
                SysAct = {'offer': self.new_offer,
                          'inform': ['产品介绍'],
                          'domain': self.domain}
                return SysAct
        elif self.UsrAct == "更换":
            self.DislikeResults.append(self.KB_pointer)
            for item in self.KB_results:
                if item not in self.DislikeResults:
                    self.new_offer = item
                    break
            else:
                self.new_offer = None
            SysAct = {'offer': self.new_offer, # TODO 是否换 offer 这个标签，亦驰可以根据 NLG 的实现来定
                      'inform': ['产品介绍'],
                      'domain': self.domain}
            return SysAct
        elif self.UsrAct == "问询说明":
            SysAct = {'offerhelp':None,
                      'domain': self.domain} # 回复问询说明
            return SysAct
        elif self.UsrAct == "闲聊":
            SysAct = {'chatting': None,
                      'domain': self.domain}  # 引导用户进入任务 例如, "嘻嘻，那请问您想要什么样的套餐？"
            return SysAct
        elif self.UsrAct == "同时办理":
            SysAct = {'offer': self.ER ,
                      'inform': ['互斥业务'],
                      'domain': self.domain}
            return SysAct
        else:
            SysAct = {'sorry': None,
                      'domain': self.domain} # "未能找到满意答案，您可登录中国移动网上营业厅查找相关最新信息"
            return SysAct


if __name__ == '__main__':
    import pprint
    rule_policy = RulePolicy()
    pprint.pprint(rule_policy.Reply(DialogStateSample))
