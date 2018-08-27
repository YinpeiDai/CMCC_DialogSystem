"""
给定本轮用户输入，上一轮系统动作，输出
领域检测、业务实体、（情感检测）、槽值对、问询槽、用户动作
"""
import sys
sys.path.append('..')
import tensorflow as tf
from NLU.DomDect.DomainDection import DomainDetector
from NLU.ER.EntityRecogition import EntityDetector
from NLU.SentiDect.SentimentDection import SentimentDetector
from NLU.UserAct.UserAction import UserActDetector
from NLU.SlotFilling.DialogState import SlotFillingDetector


save_path_dict = {
    'domain': './DomDect/model/ckpt',
    'useract': './UserAct/model/ckpt',
    'slotfilling': './SlotFilling/model/ckpt',
    'entity': './ER/entity_list.txt',
    'sentiment': './SentiDect'
}


infslot_str2num = {
    '功能费_文字描述': {
        '低': (0, 50),
        '中': (50, 200),
        '高': (200, 900)
    },
    '套餐内容_国内流量_文字描述': {
        '低': (0, 400),
        '中': (400, 1500),
        '高': (1500, 37000)
    },
    '套餐内容_国内主叫_文字描述': {
        '低': (0, 400),
        '中': (400, 1500),
        '高': (1500, 6000)
    },
}

def informable_slot_to_num(belief_state):
    # 输入一个turn的belief state: dict
    if '功能费_文字描述' in belief_state:
        if '功能费' in belief_state:
            del belief_state['功能费_文字描述']
        else:
            fee_str = belief_state['功能费_文字描述']
            belief_state['功能费'] = infslot_str2num['功能费_文字描述'][fee_str]
            del belief_state['功能费_文字描述']
    if '套餐内容_国内流量_文字描述' in belief_state:
        if '套餐内容_国内流量' in belief_state:
            del belief_state['套餐内容_国内流量_文字描述']
        else:
            fee_str = belief_state['套餐内容_国内流量_文字描述']
            belief_state['套餐内容_国内流量'] = infslot_str2num['套餐内容_国内流量_文字描述'][fee_str]
            del belief_state['套餐内容_国内流量_文字描述']
    if '套餐内容_国内主叫_文字描述' in belief_state:
        if '套餐内容_国内主叫' in belief_state:
            del belief_state['套餐内容_国内主叫_文字描述']
        else:
            fee_str = belief_state['套餐内容_国内主叫_文字描述']
            belief_state['套餐内容_国内主叫'] = infslot_str2num['套餐内容_国内主叫_文字描述'][fee_str]
            del belief_state['套餐内容_国内主叫_文字描述']


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
        ent_list, user_utter_without_ent = self.EntityDetector.get_ER_results(user_utter)
        result['entity'] = ent_list
        result['domain'] = self.DomainDetector.get_domain_results(user_utter, data_manager)
        result['useract'] = self.UserActDetector.get_user_act_results(user_utter, data_manager)
        result['informable'] = self.SlotFillingDetector.get_informable_slots_results(user_utter_without_ent, data_manager)
        informable_slot_to_num(result['informable'])
        result['requestable'] = self.SlotFillingDetector.get_requestable_slots_results(user_utter_without_ent, data_manager)
        result['sentiment'] = None   # TODO: sentimental detection
        result['userutter'] = user_utter
        return result

    def close(self):
        self.DomainDetector.close()
        self.EntityDetector.close()
        self.UserActDetector.close()
        self.SlotFillingDetector.close()
        self.SentimentDetector.close()


if __name__ == '__main__':
    nlu_manager = NLUManager(save_path_dict)