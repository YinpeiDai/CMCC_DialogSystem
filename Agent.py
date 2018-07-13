"""
结合所有的 Manager,实现text-in text-out的交互式 agent 的接口
"""

from DM.DST.StateTracking import DialodStateTracker
from DM.policy.RuleMapping import RulePolicy
from data.DataManager import DataManager
from NLU.NLUManager import NLUManager
from NLG.NLGManager import NLG_template


class DialogAgent:
    def __init__(self):
        self.rule_policy = RulePolicy()
        self.dst = DialodStateTracker()
        self.data_manager = DataManager("xxx")
        self.nlu_manager = NLUManager()
        self.nlg_template = NLG_template
        self.turn_num = 0
        self.dialog_history = []

    def run(self):
        last_DA = None
        while True:
            user_utter = input("用户输入：")
            nlu_results = self.nlu_manager.get_NLU_results(user_utter, last_DA)
            self.dst.update(nlu_results, self.data_manager)
            reply,last_DA  = self.rule_policy.Reply(self.dst, self.nlg_template)
            self.dialog_history.append({"系统":reply, "用户":user_utter})
            self.turn_num += 1

if __name__ == '__main__':
    agent = DialogAgent()
    agent.run()












