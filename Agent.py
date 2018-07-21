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
    # agent = DialogAgent()
    # agent.run()
    a = [9187, 8531, 9875, ]
    b = """requestable slot: 已购业务, accu 0.9500
requestable slot: 订购时间, accu 1.0000
requestable slot: 使用情况, accu 0.9917
requestable slot: 号码, accu 1.0000
requestable slot: 归属地, accu 0.9875
requestable slot: 品牌, accu 0.1667
requestable slot: 是否转品牌过渡期, accu 1.0000
requestable slot: 是否停机, accu 1.0000
requestable slot: 账单查询, accu 0.9792
requestable slot: 话费充值, accu 0.9958
requestable slot: 流量充值, accu 0.9875
requestable slot: 话费查询, accu 0.9875
requestable slot: 流量查询, accu 0.9958
requestable slot: 功能费, accu 0.9708
requestable slot: 套餐内容_国内主叫, accu 0.9458
requestable slot: 套餐内容_国内流量, accu 0.9000
requestable slot: 产品介绍, accu 0.9833
requestable slot: 计费方式, accu 0.9875
requestable slot: 适用品牌, accu 0.9958
requestable slot: 套餐内容_国内短信, accu 0.9958
requestable slot: 套餐内容_国内彩信, accu 1.0000
requestable slot: 套餐内容_其他功能, accu 0.1667
requestable slot: 套餐内容, accu 0.9708
requestable slot: 超出处理_国内主叫, accu 0.9958
requestable slot: 超出处理_国内流量, accu 0.9875
requestable slot: 超出处理, accu 0.9875
requestable slot: 结转规则_国内主叫, accu 1.0000
requestable slot: 结转规则_国内流量, accu 0.9958
requestable slot: 结转规则_赠送流量, accu 0.9542
requestable slot: 结转规则, accu 0.9750
requestable slot: 是否全国接听免费, accu 0.1667
requestable slot: 能否结转滚存, accu 0.9917
requestable slot: 能否分享, accu 0.9625
requestable slot: 能否转赠, accu 0.9750
requestable slot: 转户转品牌管理, accu 0.1667
requestable slot: 停机销号管理, accu 0.9958
requestable slot: 赠送优惠活动, accu 0.9917
requestable slot: 使用限制, accu 0.9833
requestable slot: 使用有效期, accu 0.9958
requestable slot: 使用方式设置, accu 0.9708
requestable slot: 封顶规则, accu 1.0000
requestable slot: 限速说明, accu 1.0000
requestable slot: 受理时间, accu 1.0000
requestable slot: 互斥业务, accu 0.9958
requestable slot: 开通客户限制, accu 0.9917
requestable slot: 累次叠加规则, accu 1.0000
requestable slot: 开通方式, accu 0.9875
requestable slot: 开通生效规则, accu 1.0000
requestable slot: 是否到期自动取消, accu 1.0000
requestable slot: 能否变更或取消, accu 0.9958
requestable slot: 取消方式, accu 0.9458
requestable slot: 取消变更生效规则, accu 0.9792
requestable slot: 变更方式, accu 0.8333
requestable slot: 密码重置方式, accu 1.0000
requestable slot: 激活方式, accu 1.0000
requestable slot: 副卡数量上限, accu 0.9917
requestable slot: 主卡添加成员, accu 0.9917
requestable slot: 主卡删除成员, accu 0.9583
requestable slot: 副卡成员主动退出, accu 0.9750
requestable slot: 主卡查询副卡, accu 0.9917
requestable slot: 副卡查询主卡, accu 1.0000
requestable slot: 恢复流量功能, accu 0.9958
requestable slot: 开通方向, accu 1.0000"""

    import re
    accu = []
    for i, line in enumerate(b.split('\n')):
        if re.search(r"accu (\d\.\d{4})", line):
            rep = re.search(r"accu (\d\.\d{4})", line)
            accu.append(float(rep.group(1)))
    print(sum(accu)/len(accu))
    print(sum(a)/len(a))











