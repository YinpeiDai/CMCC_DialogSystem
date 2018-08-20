"""
容错处理
输入未处理的对话状态、输出经过容错检错处理的对话状态
"""
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../..'))

from data.DataBase.Ontology import *
#

def ErrorHandling(DialogState):
    domain = DialogState["DetectedDomain"]["curr_turn"]
    requested_slots = DialogState["RequestedSlot"]["curr_turn"]
    requestable_slots_dict = {
        "套餐": TaoCan_requestable_slots,
        "流量": LiuLiang_requestable_slots,
        "WLAN": WLAN_requestable_slots,
        "号卡": Card_requestable_slots,
        "国际港澳台": Overseas_requestable_slots,
        "家庭多终端": MultiTerminal_requestable_slots,
        "个人": Personal_requestable_slots,
    }
    # 检测出了不属于领域的 requestable slots, 以 领域检测为准
    for slot in requested_slots:
        if slot not in requestable_slots_dict[domain]:
            requested_slots.remove(slot)

    # 如果 数值描述 和 文字描述 同时出现，只保留数值描述
    informable_slots = list(DialogState["BeliefState"]["curr_turn"].keys())
    if "功能费" in informable_slots and "功能费_文字描述" in informable_slots:
        del DialogState["BeliefState"]["curr_turn"]["功能费_文字描述"]
    if "套餐内容_国内流量" in informable_slots and "套餐内容_国内流量_文字描述" in informable_slots:
        del DialogState["BeliefState"]["curr_turn"]["套餐内容_国内流量_文字描述"]
    if "套餐内容_国内主叫" in informable_slots and "套餐内容_国内主叫_文字描述" in informable_slots:
        del DialogState["BeliefState"]["curr_turn"]["套餐内容_国内主叫_文字描述"]
    DialogState["DislikeResult"].append(1234)

    return DialogState

if __name__ == '__main__':
    from DM.policy.RuleMapping import DialogStateSample
    new = ErrorHandling(DialogStateSample)
    print(new["DislikeResult"])




