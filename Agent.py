"""
结合所有的 Manager,实现text-in text-out的交互式 agent 的接口
"""

from DM.DST.StateTracking import DialogStateTracker
from DM.policy.RuleMapping import RulePolicy
from data.DataManager import DataManager
from NLU.NLUManager import NLUManager
from NLG.NLGManager import *

UserPersonal =  {
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
        }

save_path_dict = {
    'domain': 'NLU/DomDect/model/ckpt',
    'useract': 'NLU/UserAct/model/ckpt',
    'slotfilling': 'NLU/SlotFilling/model/ckpt',
    'entity': 'NLU/ER/entity_list.txt',
    'sentiment': 'NLU/SentiDect'
}

class DialogAgent:
    def __init__(self):
        self.rule_policy = RulePolicy()
        self.dst = DialogStateTracker(UserPersonal)
        self.data_manager = DataManager('data/tmp')
        self.nlu_manager = NLUManager(save_path_dict)
        # self.nlg_template = NLG_template
        self.turn_num = 0
        self.dialog_history = []

    def run(self):
        last_DA = None   # ?
        while True:
            user_utter = input("用户输入：")
            nlu_results = self.nlu_manager.get_NLU_results(user_utter,  self.data_manager)
            self.dst.update(nlu_results, self.rule_policy, self.data_manager)
            reply  = rule_based_NLG(self.dst.DialogState['SystemAct']['curr_turn'])
            print(reply)
            self.dialog_history.append({"系统":reply, "用户":user_utter})
            self.turn_num += 1

if __name__ == '__main__':
    agent = DialogAgent()
    agent.run()





            # print('\n\nprint DST:')
            # for k,v in self.dst.DialogState.items():
            #     if k == 'OfferedResult':
            #         print(k)
            #         if '子业务' in v['prev_turn'] :
            #             print(v['prev_turn']['子业务'])
            #         if '子业务' in v['curr_turn']:
            #             print(v['curr_turn']['子业务'])
            #     elif k == 'QueryResults':
            #         print(k)
            #         for ent in v:
            #             print(ent['子业务'])
            #     else:
            #         if k=='SystemAct':
            #             print(k)
            #             for kk,vv in v.items():
            #                 if kk == 'offer':
            #                     pass
            #                 else:
            #                     print(kk,vv)
            #         else:
            #             print(k,v)
            # print('\n\n')












