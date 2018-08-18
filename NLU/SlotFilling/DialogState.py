"""
informable slots and requestable slots 当前轮的识别结果
informable slots 主要有 "功能费","套餐内容_国内主叫","套餐内容_国内流量" "开通天数"
"开通方向"。  文字描述用简化版的EDST模型预测，数值描述用正则表达式来匹配。
"""
import sys
sys.path.append('../..')

import tensorflow as tf
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"]="1"
from NLU.SlotFilling.model.model import InformableSlotDector, RequestableSlotDector
from data.DataManager import DataManager
from NLU.SlotFilling.model.train import  All_requestable_slots_order
from NLU.SlotFilling.Informable_templates import Match_Cost_Time_Data

# 开通方向 value
All_countries = {'乌拉圭', '芬兰艾伦岛', '冰岛', '西班牙马略卡岛', '斯图尔特岛', '尼加拉瓜', '多米尼加共和国', '约旦河西岸', '斯洛伐克', '法罗群岛', '哈萨克斯坦', '亚美尼亚', '安提瓜岛', '坦桑尼亚', '新加坡', '巴西', '塞班岛', '希腊克里特岛', '芬兰', '格林纳达', '象牙海岸', '葡萄牙圣港岛', '斯里兰卡', '圭亚那', '新西兰斯图尔特岛', '瑞典厄兰岛', '巴林', '古巴', '郝布里底群岛', '柬埔寨', '北爱尔兰', '马耳他', '蒙特塞拉特岛', '圣港岛', '台湾', '波兰', '洪都拉斯', '奥兰府', '博茨瓦纳', '科威特', '安的列斯群岛',
                 '西班牙梅诺卡岛', '希腊罗德岛', '法国', '西佛里西亚群岛', '特克斯和凯克斯群岛', '格林纳丁斯群岛', '伊朗', '危地马拉', '肯尼亚', '刚果', '英国郝布里底群岛', '突尼斯', '百慕大', '亚述尔群岛', '津巴布韦', '苏丹', '西班牙卡那利群岛', '挪威罗弗敦群岛', '尼日尔', '立陶宛', '爱沙尼亚', '意大利西西里岛', '英国北爱尔兰', '牙买加', '西班牙', '瑞士', '毛里求斯', '土耳其', '塞舌尔', '希腊爱奥尼亚', '乌干达', '乌克兰', '俄罗斯', '罗弗敦群岛', '罗德岛', '挪威斯雅尔巴群岛', '墨西哥', '瑙鲁', '巴拿马', '夏威夷',
                 '库拉索岛和博奈尔岛', '希腊伯罗奔尼撒', '新喀里多尼亚', '加纳', '也门', '多米尼克', '荷兰南贝佛兰岛', '马尔代夫', '乌兹别克斯坦', '秘鲁', '葡萄牙马德拉群岛', '苏里南', '美属维尔京群岛', '马提尼岛', '阿鲁巴', '缅甸', '斯洛文尼亚', '吉尔吉斯斯坦', '伯利兹', '斯雅尔巴群岛', '泰国', '格鲁吉亚', '西班牙伊比沙岛', '西班牙卡夫雷拉岛', '关岛', '斐济', '贝弗敖群岛', '意大利', '设得兰群岛', '巴勒斯坦', '巴布亚新几内亚', '阿根廷', '海地', '尼日利亚', '巴哈马', '纳米比亚', '海峡群岛', '阿尔及利亚', '英属维尔京群岛',
                 '文莱', '莫桑比克', '波恩荷尔摩岛', '马约特岛', '捷克', '哥特兰岛', '美国', '澳大利亚', '塞浦路斯', '哥斯达黎加', '丹麦', '英国', '蒙古', '巴基斯坦', '马其顿', '以色列', '刚果民主共和国', '科西嘉岛', '加蓬', '塔吉克斯坦', '列支敦士登', '日本', '约旦', '阿联酋', '曼岛', '塞内加尔', '伯罗奔尼撒', '泽西岛', '丹麦措辛厄岛', '保加利亚', '加拿大', '塞拉利昂', '新西兰', '英国设得兰群岛', '南非', '韩国', '西班牙美利利亚', '艾伦岛', '瑞典哥特兰岛', '法属圭亚那', '梵蒂冈', '帛琉岛', '印度', '摩尔多瓦', '葡萄牙亚述尔群岛',
                 '塞尔维亚', '丹麦波恩荷尔摩岛', '南贝佛兰岛', '越南', '卡塔尔', '圣文森特', '意大利撒丁岛', '阿富汗', '马德拉群岛', '圣卢西亚', '爱尔兰', '葡萄牙', '比利时', '西班牙切乌塔', '天宁岛', '希腊', '德国', '喀麦隆', '挪威西奥仑群岛', '帕劳', '尼泊尔', '丹麦朗厄兰岛', '不丹', '阿尔巴尼亚', '科特迪瓦', '波黑', '埃及', '萨尔瓦多', '荷兰西佛里西亚群岛', '沙特', '克里特岛', '摩纳哥', '奥地利', '直布罗陀', '基克拉泽', '阿塞拜疆', '开曼群岛', '海事漫游', '澳门', '奥克尼群岛', '汤加', '英国奥克尼群岛', '克罗地亚',
                 '卢森堡', '孟加拉', '马达加斯加', '印度尼西亚', '菲律宾', '巴布达', '巴拉圭', '孟加拉国', '萨摩亚', '西班牙福门特拉', '法国科西嘉岛', '瓜德罗普岛', '希腊基克拉泽', '白俄罗斯', '圣马力诺', '委内瑞拉', '玻利维亚', '安圭拉', '圣基茨和尼维斯', '马来西亚', '伊拉克', '东帝汶', '格陵兰', '老挝', '阿曼', '卢旺达', '西班牙加那利群岛', '香港', '瑞典', '匈牙利', '挪威', '哥伦比亚', '留尼汪岛', '厄瓜多尔', '赞比亚', '厄兰岛', '荷兰', '维尔京群岛', '摩洛哥', '黑山', '拉脱维亚', '罗马尼亚', '西奥仑群岛', '智利', '巴巴多斯',
                 '波多黎各', '爱奥尼亚', '黎巴嫩', '航空漫游', '瓦努阿图', '安哥拉'}

class SlotFillingDetector:
    """
    给出 informable slots 和 requestable slots
    """
    def __init__(self, save_path):
        print('载入 SlotFilling 模型...')
        self.informable_graph = tf.Graph()
        with self.informable_graph.as_default():
            self.informable_slots_models = {
                "功能费": InformableSlotDector('cost'),
                "流量": InformableSlotDector('data'),
                "通话时长": InformableSlotDector('time'),
            }
            self.informable_tf_config = tf.ConfigProto()
            self.informable_tf_config.gpu_options.allow_growth = True
            self.informable_tf_config.allow_soft_placement = True
            self.informable_sess = tf.Session(config=self.informable_tf_config)
            self.informable_sess.run(tf.global_variables_initializer())
            self.informable_saver = tf.train.Saver()
            self.informable_saver.restore(self.informable_sess, save_path + "/informable/model.ckpt")

        self.requestable_graph = tf.Graph()
        with self.requestable_graph.as_default():
            self.requestable_slots_models = {}
            for k, v in All_requestable_slots_order.items():
                self.requestable_slots_models[k] = RequestableSlotDector(str(v))
            self.requestable_tf_config = tf.ConfigProto()
            self.requestable_tf_config.gpu_options.allow_growth = True
            self.requestable_tf_config.allow_soft_placement = True
            self.requestable_sess = tf.Session(config=self.requestable_tf_config)
            self.requestable_sess.run(tf.global_variables_initializer())
            self.requestable_saver = tf.train.Saver()
            self.requestable_saver.restore(self.requestable_sess, save_path + "/requestable/model.ckpt")


    def get_informable_slots_results(self, user_utter, data_manager):
        """
        给定输入句子，上一轮DA, 本轮检测出来的领域、用户动作
        :param user_utter: 输入句子，不用分词
        :return: dictionary of slot-value pairs， 即 DataManager.SearchingByConstraints()中的 feed_dict
                  文字描述 统一 value 是高、中、低
                  数值描述 统一 value 是 tuple (下限， 上限)
        """
        results_dict = {}
        # 给出 informable slots 功能费_文字描述，套餐内容_国内流量_文字描述，套餐内容_国内主叫_文字描述
        discription = ["高","中","低","无"]
        for slot, model in self.informable_slots_models.items():
            batch_data = [user_utter]
            char_emb_matrix, word_emb_matrix, _ = data_manager.sent2num(batch_data)
            predict = self.informable_sess.run(model.predict,
                                   feed_dict={
                                       model.char_emb_matrix: char_emb_matrix,
                                       model.word_emb_matrix: word_emb_matrix,
                                   })
            if slot == "流量" and discription[predict[0]] != "无":
                results_dict["套餐内容_国内流量_文字描述"] = discription[predict[0]]
            if slot == "功能费" and discription[predict[0]] != "无":
                results_dict["功能费_文字描述"] = discription[predict[0]]
            if slot == "通话时长" and discription[predict[0]] != "无":
                results_dict["套餐内容_国内主叫_文字描述"] = discription[predict[0]]

        # 给出 informable slots  套餐内容_国内主叫，套餐内容_国内流量，功能费
        for slot, value in Match_Cost_Time_Data(user_utter).items():
            if value != None:
                results_dict[slot] = value

        # 开通方向
        for value in All_countries:
            if value in user_utter:
                results_dict["开通方向"] = value
        return results_dict

    def get_requestable_slots_results(self, user_utter, data_manager):
        """
        给定输入句子，上一轮DA, 本轮检测出来的领域、用户动作
        :return: a list of requestable slots
        """
        # 测试 requestable slots
        requested_slots = []
        for slot, model in self.requestable_slots_models.items():
            batch_data = [user_utter]
            char_emb_matrix, word_emb_matrix, _ = data_manager.sent2num(batch_data)
            predict = self.requestable_sess.run(model.predict,
                                    feed_dict={
                                        model.char_emb_matrix: char_emb_matrix,
                                        model.word_emb_matrix: word_emb_matrix,
                                    })
            bad_slots = [] # 差结果，不要，反正不影响
            if predict[0] == 0 and slot not in bad_slots: # 套餐内容_国内短信 slot 结果太差不要了
                requested_slots.append(slot)

        return requested_slots

    def close(self):
        self.informable_sess.close()
        self.requestable_sess.close()

if __name__ == '__main__':
    slot_filling = SlotFillingDetector("./model/ckpt")
    data_manager = DataManager('../../data/tmp')
    while True:
        usr_input = input("请输入：")
        print(slot_filling.get_informable_slots_results(usr_input, data_manager))
        print(slot_filling.get_requestable_slots_results(usr_input, data_manager))
