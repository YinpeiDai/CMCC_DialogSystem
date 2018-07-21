"""
基于规则的policy

"""
# 这么写是为了说明数据结构是和 DataManager.SearchingByEntity 等一样的
DialogStateExample = {
    'TurnNum':int,
    # 用户主动提及业务实体集合
    'EntityMentioned': {'curr_turn': {'20元地铁流量包':DataManager.SearchingByEntity("流量", {"子业务": '20元地铁流量包'})},
                        'prev_turn': {}},
    'UserPersenal': DataManager.person_info, # 个人信息，dict
    'QueryResult': DataManager.SearchingByConstraints(),
    'SystemReturnAct': {'curr_turn': {'offer': DataManager.SearchingByConstraints()[0], 'inform':['适用品牌', '产品介绍']},
                     'prev_turn': {}},
    'BeliefState': SlotFillingDector.get_informable_slots_results(),
    'RequestedSlot': {'curr_turn': SlotFillingDector.get_requestable_slots_results(),
                      'prev_turn': SlotFillingDector.get_requestable_slots_results()},
    'DetectedDomain': {'curr_turn': None,
                         'prev_turn': None},
    'UserAct': {'curr_turn': None,
                'prev_turn': None}
}




class RulePolicy:
    def __init__(self):
        pass

    def Reply(self, CurrrentDialogState, NLG_template):
        # return reply,last_DA
        pass



