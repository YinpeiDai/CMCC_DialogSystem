"""
结合所有的 Manager,实现text-in text-out的交互式 agent 的接口
"""
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../..'))
from DM.DST.StateTracking import DialogStateTracker
from DM.policy.RuleMapping import RulePolicy
from data.DataManager import DataManager
from NLU.NLUManager import NLUManager
from NLG.NLGManager import rule_based_NLG
os.environ["CUDA_VISIBLE_DEVICES"]="1"

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
    'domain': os.path.join(BASE_DIR, 'NLU/DomDect/model/ckpt'),
    'useract': os.path.join(BASE_DIR, 'NLU/UserAct/model/ckpt'),
    'slotfilling': os.path.join(BASE_DIR, 'NLU/SlotFilling/model/ckpt'),
    'entity': os.path.join(BASE_DIR, 'NLU/ER/entity_list.txt'),
    'sentiment': os.path.join(BASE_DIR, 'NLU/SentiDect')
}

class DialogAgent:
    def __init__(self):
        self.rule_policy = RulePolicy()
        self.dst = DialogStateTracker(UserPersonal)
        self.data_manager = DataManager(os.path.join(BASE_DIR, 'data/tmp'))
        self.nlu_manager = NLUManager(save_path_dict)
        # self.nlg_template = NLG_template
        self.turn_num = 0
        self.dialog_history = []

    def run(self):
        last_DA = None   # ?
        try:
            while True:
                user_utter = input("用户输入：")
                nlu_results = self.nlu_manager.get_NLU_results(user_utter,  self.data_manager)
                self.dst.update(nlu_results, self.rule_policy, self.data_manager)

                print('\n')
                self.dst.dialog_state_print()
                print('\n')

                reply  = rule_based_NLG(self.dst)
                print('系统:', reply)
                self.dialog_history.append({"系统":reply, "用户":user_utter})
                self.turn_num += 1

        except KeyboardInterrupt:
            self.nlu_manager.close()
            print('\n系统: 感谢您的使用，再见！')

if __name__ == '__main__':
    agent = DialogAgent()
    agent.run()

















