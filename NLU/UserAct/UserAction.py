"""
用户动作检测
"""
import sys
sys.path.append('../..')
from NLU.UserAct.model.model import *
from data.DataManager import DataManager
import tensorflow as tf

class UserActDetector:
    def __init__(self, model_path):
        print('载入 UserActDetector 模型...')
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.model = UserActModel("UserActDect")
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            tf_config.allow_soft_placement=True
            self.sess = tf.Session(config=tf_config)
            self.sess.run(tf.global_variables_initializer())
            self.saver = tf.train.Saver()
            self.saver.restore(self.sess, model_path + "/model.ckpt")

    def get_user_act_results(self, user_utter, data_manager):
        """
        # 给定 输入句子， 返回预测的用户动作
        # 参考 data.DataBase.Ontology.USER_ACT
        # TODO： 可能还有别的参数，亦驰你自己来定
        :param user_utter: 输入句子，不用分词
        :return: a domain string in
                    ['问询', '告知', '要求更多', '要求更少', '更换', '问询说明',
                     '话题=WLAN', '话题=号卡', '话题=套餐流量', '话题=资源分享',
                     '同时办理', '比较', '闲聊']
                     and its probability
        TODO: Add last_domain information
        """
        user_acts = [ '问询', '告知', '要求更多', '要求更少', '更换', '问询说明',
                             '话题=WLAN', '话题=号卡', '话题=套餐流量', '话题=资源分享',
                             '同时办理', '比较', '闲聊']
        batch_data = [user_utter]
        char_emb_matrix, word_emb_matrix, _ = data_manager.sent2num(batch_data)
        predict, probs = self.sess.run([self.model.predict,
                                                          self.model.probs],
                               feed_dict={
                                   self.model.is_training: False,
                                   self.model.char_emb_matrix: char_emb_matrix,
                                   self.model.word_emb_matrix: word_emb_matrix,
                               })
        pred_result = user_acts[predict[0]]
        pred_prob = probs[0][predict[0]]
        return pred_result, pred_prob

    def close(self):
        self.sess.close()


if __name__ == '__main__':
    UADetector = UserActDetector("./model/ckpt")
    data_manager = DataManager('../../data/tmp')
    while True:
        usr_input = input("请输入：")
        print(UADetector.get_user_act_results(usr_input, data_manager))