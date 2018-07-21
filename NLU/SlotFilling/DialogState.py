"""
informable slots and requestable slots 当前轮的识别结果
informable slots 主要有 "功能费","套餐内容_国内主叫","套餐内容_国内流量" "开通天数"
"开通方向"。  文字描述用简化版的EDST模型预测，数值描述用正则表达式来匹配。
"""
import tensorflow as tf
import numpy as np
import os
from NLU.SlotFilling.model.model import InformableSlotDector, RequestableSlotDector
from data.DataManager import DataManager
from NLU.SlotFilling.model.train import  All_requestable_slots_order
from NLU.SlotFilling.Informable_templates import Match_Cost_Time_Data

class SlotFillingDector:
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
            self.informable_sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
            self.informable_sess.run(tf.global_variables_initializer())
            self.informable_saver = tf.train.Saver()
            self.informable_saver.restore(self.informable_sess, save_path + "/informable/model.ckpt")

        self.requestable_graph = tf.Graph()
        with self.requestable_graph.as_default():
            self.requestable_slots_models = {}
            for k, v in All_requestable_slots_order.items():
                self.requestable_slots_models[k] = RequestableSlotDector(str(v))
            self.requestable_sess = tf.Session(graph=self.requestable_graph,
                                               config=tf.ConfigProto(allow_soft_placement=True))
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
        # 测试 informable slots 文字描述
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

        # 测试 informable slots 数值描述
        for slot, value in Match_Cost_Time_Data(user_utter).items():
            if value != None:
                results_dict[slot] = value
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
            bad_slots = ["订购时间","互斥业务", "封顶规则"] # 差结果，不要，反正不影响
            if predict[0] == 0 and slot not in bad_slots: # 套餐内容_国内短信 slot 结果太差不要了
                requested_slots.append(slot)

        return requested_slots

    def close(self):
        self.informable_sess.close()
        self.requestable_sess.close()

if __name__ == '__main__':
    slot_filling = SlotFillingDector("./model/ckpt")
    data_manager = DataManager('../../data/tmp')
    while True:
        usr_input = input("请输入：")
        print(slot_filling.get_informable_slots_results(usr_input, data_manager))