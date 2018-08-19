"""
领域检测
"""
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../..'))
from NLU.DomDect.model.model import *
from data.DataManager import DataManager
import tensorflow as tf

class DomainDetector:
    def __init__(self, model_path):
        print('载入 DomainDetector 模型...')
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.model = DomainModel("DomDect")
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            tf_config.allow_soft_placement=True
            self.sess = tf.Session(config=tf_config)
            self.sess.run(tf.global_variables_initializer())
            self.saver = tf.train.Saver()
            self.saver.restore(self.sess, model_path + "/model.ckpt")

    def get_domain_results(self, user_utter, data_manager):
        """
        给定当前输入句子，上一轮检测领域结果，返回当前句子检测出来的领域
        :param user_utter: 输入句子，不用分词
        :return: a domain string in
                    ["个人", "套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端" ]
                    and its probability
        TODO: Add last_domain information
        """
        domains = ["个人", "套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端" ]
        batch_data = [user_utter]
        char_emb_matrix, word_emb_matrix, _ = data_manager.sent2num(batch_data)
        predict, probs = self.sess.run([self.model.predict,
                                                          self.model.probs],
                               feed_dict={
                                   self.model.is_training: False,
                                   self.model.char_emb_matrix: char_emb_matrix,
                                   self.model.word_emb_matrix: word_emb_matrix,
                               })
        pred_result = domains[predict[0]]
        pred_prob = probs[0][predict[0]]
        return pred_result, pred_prob

    def close(self):
        self.sess.close()


if __name__ == '__main__':
    DomDetector = DomainDetector("./model/ckpt")
    data_manager = DataManager('../../data/tmp')
    while True:
        usr_input = input("请输入：")
        print(DomDetector.get_domain_results(usr_input, data_manager))