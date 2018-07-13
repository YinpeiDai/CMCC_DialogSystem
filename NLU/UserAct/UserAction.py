"""
用户动作检测
"""
from NLU.UserAct.model.model import LSTM
import tensorflow as tf

class UserActDector:
    def __init__(self):
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.model = LSTM()
        # self.saver = tf.train.Saver()
        # self.saver.restore(self.sess, "xxx")  # xxx为ckpt路径

    def get_UserAct_results(self, user_utter, last_DA):
        # 给定 输入句子， 返回预测的用户动作
        # 参考 data.DataBase.Ontology.USER_ACT
        # TODO： 可能还有别的参数，亦驰你自己来定
        return None

    def close(self):
        self.sess.close()
