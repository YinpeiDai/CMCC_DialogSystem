"""
给定本轮用户输入，上一轮系统动作，输出
领域检测、业务实体、（情感检测）、槽值对、问询槽、用户动作
"""
import tensorflow as tf
from NLU.DomDect.DomainDection import DomainDector
from NLU.ER.EntityRecogition import EntityDector
from NLU.SentiDect.SentimentDection import SentimentDector
from NLU.UserAct.UserAction import UserActDector
# from NLU.SlotFilling import *** 具体接口还没设定


class NLUManager:
    def __init__(self):
        self.domain_dector = DomainDector()
        self.entity_dector = EntityDector()
        self.useract_dector = UserActDector()
        self.sentiment_dector = SentimentDector()

    def get_NLU_results(self, user_utter, last_DA):
        pass

    def close(self):
        self.domain_dector.close()
        self.useract_dector.close()


if __name__ == '__main__':
    nlu_manager = NLUManager()