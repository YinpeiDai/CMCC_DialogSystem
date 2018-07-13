"""
对话状态跟踪、维护对话历史

四个业务实体集合：用户主动提及集合（保留两轮）、用户个人业务集合、数据库查询结果、系统提供结果集合（保留一轮）
所有领域的 belief states（累计） 和 requested slots(保留两轮)、领域检测结果（保留两轮）、 用户动作结果（保留两轮）

是否 DST 不变、是否用户重复表述同一句话、情感检测结果

"""
from collections import deque

class DialodStateTracker:
    def __init__(self):
        self.MentionedEntitySet = deque([], maxlen=2)
        self.PersonalEntitySet = None
        self.SearchedEntitySet = None
        self.ReturnedEntitySet = None
        self.requested_slots = deque([], maxlen=2)
        self.detected_domain = deque([], maxlen=2)
        self.user_acts = deque([], maxlen=2)
        self.isDSTChange = True
        self.isUtterSame = False
        self.detected_sentiment = None
        self.user_utter = None
        self.belief_states = {}

    def update(self, NLU_results, data_manager):
        """
        NLU_results 包含
        Dom_results, ER_results, Senti_results, UserAct_results,
        Slot_filling_results, user_utter
        :param NLU_results: dict
        :param data_manager: data_manager
        """
        pass
















if __name__ == '__main__':
    dst = DialodStateTracker()
    dst.MentionedEntitySet.append(1)
    dst.MentionedEntitySet.append(2)
    dst.MentionedEntitySet.append(3)
    print(dst.MentionedEntitySet)
