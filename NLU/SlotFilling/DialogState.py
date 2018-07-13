"""
informable slots and requestable slots 当前轮的识别结果
informable slots 主要有 "功能费","套餐内容_国内主叫","套餐内容_国内流量" "开通天数"
"开通方向"。  文字描述用简化版的EDST模型预测，数值描述用正则表达式来匹配。
"""
import tensorflow as tf
from NLU.SlotFilling.model.model import InformableSlotDector, RequestableSlotDector
from data.DataManager import DataManager
from NLU.SlotFilling.model.train import All_requestable_slots, All_requestable_slots_order

class SlotFillingDector:
    """
    给出 informable slots 和 requestable slots
    """
    def __init__(self, save_path):
        print('载入 SlotFilling 模型...')
        self.informable_slots_models = {
            "功能费": InformableSlotDector('cost'),
            "流量": InformableSlotDector('data'),
            "通话时长": InformableSlotDector('time')
        }
        self.requestable_slots_models = {}
        for k, v in All_requestable_slots_order.items():
            self.requestable_slots_models[k] = RequestableSlotDector(str(v))
        self.sess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True))
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.saver.restore(self.sess, save_path)

    def get_informable_slots_results(self, user_utter, data_manager):
        """
        给定输入句子，上一轮DA, 本轮检测出来的领域、用户动作
        :param user_utter: 已经分好词的
        :return: dictionary of slot-value pairs
                  文字描述 统一 value 是高、中、低
                  数值描述 统一 value 是 tuple (下限， 上限)
        """
        # TODO: 下次完成数值描述和文字描述的结合
        # 测试 informable slots 文字描述
        discription = ["高","中","低","无"]
        for slot, model in self.informable_slots_models.items():
            batch_data = [user_utter]
            char_emb_matrix, word_emb_matrix, _ = data_manager.sent2num(batch_data)
            predict = self.sess.run(model.predict,
                                   feed_dict={
                                       model.char_emb_matrix: char_emb_matrix,
                                       model.word_emb_matrix: word_emb_matrix,
                                   })
            print("informable slot: %s, predict %s" % (slot, discription[predict[0]]))

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
            predict = self.sess.run(model.predict,
                                    feed_dict={
                                        model.char_emb_matrix: char_emb_matrix,
                                        model.word_emb_matrix: word_emb_matrix,
                                    })
            if predict[0] == 0:
                requested_slots.append(slot)
        return requested_slots

    def close(self):
        self.sess.close()

if __name__ == '__main__':
    slot_filling = SlotFillingDector("./model/ckpt/model.ckpt")
    data_manager = DataManager('../../data/tmp')
    while True:
        usr_input = input("请输入")
        print(slot_filling.get_requestable_slots_results(usr_input, data_manager))