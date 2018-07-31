"""
给定本轮用户输入，上一轮系统动作，输出
领域检测、业务实体、（情感检测）、槽值对、问询槽、用户动作
"""
import tensorflow as tf
from NLU.DomDect.DomainDection import DomainDetector
from NLU.ER.EntityRecogition import EntityDetector
from NLU.SentiDect.SentimentDection import SentimentDetector
from NLU.UserAct.UserAction import UserActDetector
from NLU.SlotFilling.DialogState import SlotFillingDetector
# from NLU.SlotFilling import *** 具体接口还没设定

save_path_dict = {
    'domain': './DomDect/model/ckpt',
    'useract': './UserAct/model/ckpt',
    'slotfilling': './SlotFilling/model/ckpt',
    'entity': './ER',
    'sentiment': './SentiDect'
}

class NLUManager:
    def __init__(self, save_path_dict):
        self.DomainDetector = DomainDetector(save_path_dict['domain'])
        self.EntityDetector = EntityDetector(save_path_dict['entity'])
        self.UserActDetector = UserActDetector(save_path_dict['useract'])
        self.SlotFillingDetector = SlotFillingDetector(save_path_dict['slotfilling'])
        self.SentimentDetector = SentimentDetector(save_path_dict['sentiment'])

    def get_NLU_results(self, user_utter, data_manager):
        """
        给定当前输入句子，上一轮检测领域结果，返回NLU各模块的识别结果
        :param user_utter: 输入句子，不用分词
        :return:
        """
        result = {}
        result['domain'] = self.DomainDetector.get_domain_results(user_utter, data_manager)
        result['useract'] = self.UserActDetector.get_user_act_results(user_utter, data_manager)
        result['informable'] = self.SlotFillingDetector.get_informable_slots_results(user_utter, data_manager)
        result['requestable'] = self.SlotFillingDetector.get_requestable_slots_results(user_utter, data_manager)
        result['entity'] = None    #TODO: entity recognize
        result['sentiment'] = None   # TODO: sentimental detection
        return result

    def close(self):
        self.DomainDetector.close()
        self.EntityDetector.close()
        self.UserActDetector.close()
        self.SlotFillingDetector.close()
        self.SentimentDetector.close()


if __name__ == '__main__':
    nlu_manager = NLUManager()