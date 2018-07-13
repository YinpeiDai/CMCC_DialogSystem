"""
领域检测
"""
from NLU.DomDect.model.model import LSTM
import tensorflow as tf

class DomainDector:
    def __init__(self):
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.model = LSTM() # TODO 模型是LSTM还是别的亦驰你自己来定
        # self.saver = tf.train.Saver()
        # self.saver.restore(self.sess, "xxx")  # xxx为ckpt路径

    def get_Dom_results(self, user_utter, last_domain):
        """
        给定当前输入句子，上一轮检测领域结果，返回当前句子检测出来的领域
        TODO 是否需要上一轮的结果亦驰你自己来定
        """
        return None

    def close(self):
        self.sess.close()
