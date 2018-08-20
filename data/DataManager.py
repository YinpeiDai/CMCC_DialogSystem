"""
1. 能够统一生成词典、训练词向量，并保存这些中间文件至 /tmp 文件夹
2. 能够提供查询数据库、分词、查词典、查词向量、查ontology 数据交换的接口
3. 个人信息返回
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..'))


import tensorflow as tf
import os,json, pickle, time
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
from pylab import *

from data.WordDict.generate_dict import DictGenerator
from data.WordDict.word2vec import NCE_word2vec
from data.WordDict.char2vec import NCE_char2vec
from data.WordSeg.WordSegmentation import WordSegWrapper
from data.DataBase.Operation import DBOperationWrapper
from data.DataBase.Ontology import *  # 提供 Ontology,需要预先写好

# 处理中文字体在 matplotlib 乱码的问题
mpl.rcParams['font.sans-serif'] = ['SimHei']



# 在本文件 main 函数执行即可
def train_word_and_char(save_path,
                        data_words,
                        retrain=False,
                        word_dict_size=1500,
                        char_dict_size = 700,
                        word_embed_size = 20,
                        char_embed_size = 20):
    """
    得到词典，词向量,字符向量等
    :param save_path: 存放路径，默认是 tmp 中
    :param data_words: 已经分好词的 list
    :param retrain: bool 是否重新训练字符向量和词向量
    """
    dictgenerator = DictGenerator(save_path, data_words,word_dict_size,char_dict_size)
    print("生成字符表、逆字符表、字符频，字符向量训练数据...")
    char2vec_traindata, char_dictionary, reversed_char_dictionary, char_count = \
        dictgenerator.generate_char_dict()
    with open(os.path.join(save_path, "char_dict.json"), "w", encoding="utf-8") as f:
        json.dump(char_dictionary, f, ensure_ascii=False)
    with open(os.path.join(save_path, "reversed_char_dict.json"), "w", encoding="utf-8") as f:
        json.dump(reversed_char_dictionary, f, ensure_ascii=False)
    with open(os.path.join(save_path, "char_freq.json"), "w", encoding="utf-8") as f:
        json.dump(char_count, f, ensure_ascii=False)
    with open(os.path.join(save_path, "char2vec_traindata.json"), "w", encoding="utf-8") as f:
        json.dump(char2vec_traindata, f, ensure_ascii=False)

    print("生成词表、逆词表、词频，词向量训练数据...")
    word2vec_traindata, word_dictionary, reversed_word_dictionary, word_count = \
        dictgenerator.generate_word_dict()
    with open(os.path.join(save_path, "word_dict.json"), "w", encoding="utf-8") as f:
        json.dump(word_dictionary, f, ensure_ascii=False)
    with open(os.path.join(save_path, "reversed_word_dict.json"), "w", encoding="utf-8") as f:
        json.dump(reversed_word_dictionary, f, ensure_ascii=False)
    with open(os.path.join(save_path, "word_freq.json"), "w", encoding="utf-8") as f:
        json.dump(word_count, f, ensure_ascii=False)
    with open(os.path.join(save_path, "word2vec_traindata.json"), "w", encoding="utf-8") as f:
        json.dump(word2vec_traindata, f, ensure_ascii=False)

    if retrain:
        print("训练词向量...")
        synonym_inputs_ = []
        with open(os.path.join(save_path, '_同义词.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.lstrip('\ufeff')
                words = line.split()
                if words[0] in word_dictionary and words[1] in word_dictionary:
                    synonym_inputs_.append([word_dictionary[words[0]], word_dictionary[words[1]]])
        nce_word2vec = NCE_word2vec(word2vec_traindata,
                                    len(word_dictionary),
                                    word_dictionary,
                                    synonym_inputs_,
                                    lr=1.0,
                                    num_sampled=2,
                                    embedding_size=word_embed_size)
        with tf.Session() as sess:
            wordvec = nce_word2vec.run_train(sess, 6000)
        with open(os.path.join(save_path, "wordvec.pkl"), "wb") as f:
            pickle.dump(wordvec,f)

        # Visualize the word embeddings.
        def plot_with_labels(low_dim_embs, labels, filename):
            assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
            plt.figure(figsize=(18, 18))  # in inches
            for i, label in enumerate(labels):
                x, y = low_dim_embs[i, :]
                plt.scatter(x, y)
                plt.annotate(label,
                             xy=(x, y),
                             xytext=(5, 2),
                             textcoords='offset points',
                             ha='right',
                             va='bottom')

            plt.savefig(os.path.join(save_path,filename))

        tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
        plot_only = 300
        low_dim_embs = tsne.fit_transform(wordvec[:plot_only, :])
        labels = [reversed_word_dictionary[i] for i in range(plot_only)]
        plot_with_labels(low_dim_embs, labels, 'tsne.png')

        print("训练字符向量...")
        nce_char2vec = NCE_char2vec(char2vec_traindata,
                                    len(char_dictionary),
                                    lr=1.0,
                                    num_sampled=2,
                                    embedding_size=char_embed_size)
        with tf.Session() as sess:
            char2vec = nce_char2vec.run_train(sess, 6000)
        with open(os.path.join(save_path, "charvec.pkl"), "wb") as f:
            pickle.dump(char2vec,f)

# 在词典，词向量等构造好了之后才能使用 DataManager
class DataManager:
    def __init__(self, save_path):
        # 提供查词典、查词向量
        print('载入词向量...')
        with open(os.path.join(save_path, "word_dict.json"), "r", encoding="utf-8") as f:
            self.word_dictionary = json.load(f)
        with open(os.path.join(save_path, "wordvec.pkl"), "rb") as f:
            self.word_vectors = pickle.load(f)
            self.word_dict_size = np.shape(self.word_vectors)[0]
            self.word_embed_size = np.shape(self.word_vectors)[1]

        # 提供查字符典、查字符向量
        print('载入字符向量...')
        with open(os.path.join(save_path, "char_dict.json"), "r", encoding="utf-8") as f:
            self.char_dictionary = json.load(f)
        with open(os.path.join(save_path, "charvec.pkl"), "rb") as f:
            self.char_vectors = pickle.load(f)
            self.char_dict_size = np.shape(self.char_vectors)[0]
            self.char_embed_size = np.shape(self.char_vectors)[1]

        # 查询数据库
        print('载入数据库...')
        self.DBoperation = DBOperationWrapper(os.path.join(save_path, 'CMCC_NewDB.db'))

        # 个人信息
        print("载入个人信息...")
        self.person_info = {
            "已购业务": ["180元档幸福流量年包", "18元4G飞享套餐升级版", "流量安心包",
                     "139邮箱免费版", "飞信", "满意100服务资讯"],
            "使用情况": "剩余流量 11.10 GB，剩余通话 0 分钟，话费余额 110.20 元，本月已产生话费 247.29 元",
            "号码": "18811369685",
            "归属地" : "北京",
            "品牌": "动感地带",
            "是否转品牌过渡期": "否",
            "话费查询": "话费余额 110.20 元",
            "流量查询": "剩余流量 11.10 GB",
            "订购时间": "订购时间 2017-04-04， 生效时间 2017-05-01",
            "是否停机": "否",
            "话费充值": "请登录网上营业厅、微厅或 APP 充值",
            "流量充值": "请登录网上营业厅、微厅或 APP 充值",
            "账单查询": "请登录网上营业厅、微厅或 APP 查询"
        }

        # 提供对话训练数据
        print("载入 2018.6.13 收集的对话训练数据...")
        with open(os.path.join(save_path, "DialogData20180613.json"), "r", encoding="utf-8") as f:
            self.DialogData = json.load(f)


        # 分词
        print('载入分词工具...')
        self.WordSegmentor = WordSegWrapper(save_path)
        time.sleep(2)


    def SearchingByConstraints(self, table, feed_dict):
        """
        :param table:  数据库的table
        :param feed_dict: Slot-filling 模块 SlotFillingDector.get_informable_slots_results 直接给出
        :return: list of  所有符合要求的套餐
        """
        results = []
        if table == "套餐":
            for item in self.DBoperation.SearchingByConstraints(table, feed_dict):
                results.append(dict(zip(TaoCan_DB_slots, item)))
            return results
        elif table == "流量":
            for item in self.DBoperation.SearchingByConstraints(table, feed_dict):
                if item[0] not in ["元旦包", "春节包", "清明包", "五一包", "端午包",
                                       "中秋包", "国庆包"]:
                    results.append(dict(zip(LiuLiang_DB_slots, item)))
            return results
        elif table == "国际港澳台":
            for item in self.DBoperation.SearchingByConstraints(table, feed_dict):
                results.append(dict(zip(Overseas_DB_slots, item))) #  此处更改
            return results
        return results

    def SearchingByEntity(self, table, feed_dict):
        results = []
        if table == "套餐":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(TaoCan_DB_slots, item)))
            return results
        elif table == "流量":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(LiuLiang_DB_slots, item)))
            return results
        elif table == "Card":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(Card_DB_slots, item)))
            return results
        elif table == "WLAN":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(WLAN_DB_slots, item)))
            return results
        elif table == "国际港澳台":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(Overseas_DB_slots, item))) #  此处更改
                return results
        elif table == "家庭多终端":
            for item in self.DBoperation.SearchingByEntity(table, feed_dict):
                results.append(dict(zip(MultiTerminal_DB_slots, item)))  # 此处更改
                return results
        return results

    def WordSegmentCut(self, sent):
        return self.WordSegmentor.tokenize(sent)

    def sent2num(self, sents, max_sent_length=40, max_word_length=6):
        """
        将自然语句转为词嵌入矩阵，字符矩阵
        :param sents: a list of 输入句子
        :param max_sent_length: 一个单词包含的最大字符个数
        :param max_word_length: 一个句子包含的最大单词个数
        :return: 词嵌入矩阵(batch*max_sent_length*word_emb_size)，
                  字符矩阵 (batch * max_sent_length * max_word_length * char_emb_size)
        """
        # batchsize = len(sents)
        # word_emb_matrix = np.zeros(shape=[batchsize, max_sent_length, self.word_embed_size], dtype=np.float32)
        # char_emb_matrix = np.zeros(shape=[batchsize, max_sent_length, max_word_length, self.char_embed_size], dtype=np.float32)
        # for i, sent in enumerate(sents):
        #     for j, word in enumerate(sent):
        #         if j < max_sent_length: # 超过了最大长度，只读入最大长度的句子，后面的丢弃
        #             if word in self.word_dictionary:
        #                 word_emb_matrix[i, j] = self.word_vectors[self.word_dictionary[word]]
        #             else:
        #                 word_emb_matrix[i, j] = self.word_vectors[self.word_dictionary["UNK"]]
        #         for k, char in enumerate(word):
        #             if k < max_word_length: # 超过了最大长度，只读入最大长度的字符，后面的丢弃
        #                 if char in self.char_dictionary:
        #                     char_emb_matrix[i, j, k] = self.char_vectors[self.char_dictionary[char]]
        #                 else:
        #                     char_emb_matrix[i, j, k] = self.char_vectors[self.char_dictionary["UNK"]]
        batchsize = len(sents)
        word_emb_matrix = np.zeros(shape=[batchsize, max_sent_length, self.word_embed_size], dtype=np.float32)
        seqlen = np.zeros(shape=[batchsize], dtype=np.int32)
        char_emb_matrix = np.zeros(shape=[batchsize, max_sent_length, self.char_embed_size],
                                   dtype=np.float32)

        for i, sent in enumerate(sents):
            sent = self.WordSegmentCut(str(sent))
            seqlen[i] = len(sent)
            for j, word in enumerate(sent):
                if j < max_sent_length:  # 超过了最大长度，只读入最大长度的句子，后面的丢弃
                    if word in self.word_dictionary:
                        word_emb_matrix[i, j] = self.word_vectors[self.word_dictionary[word]]
                    else:
                        word_emb_matrix[i, j] = self.word_vectors[self.word_dictionary["UNK"]]
                    for k, char in enumerate(word):
                        if char in self.char_dictionary:
                            char_emb_matrix[i, j] += self.char_vectors[self.char_dictionary[char]]
                        else:
                            char_emb_matrix[i, j] += self.char_vectors[self.char_dictionary["UNK"]]
                    char_emb_matrix[i, j] /= len(word)

        return char_emb_matrix, word_emb_matrix, seqlen

if __name__ == '__main__':
    # # 读入data，生成词典，训练词向量
    # file = os.path.dirname(os.path.abspath(__file__))
    # file = os.path.join(file, "tmp")
    # #  如果后续加入业务实体识别，需去词汇化处理，则可以重新生成词典等文件
    # with open('./tmp/DialogData20180613.json',  'r', encoding='utf-8') as f:
    #     dialog_data = json.load(f)
    # CMCC_WordSeg = WordSegWrapper("./tmp")
    # words = []
    # for k, item in dialog_data.items():
    #     for sent in item["用户回复示例"]:
    #         words.extend(CMCC_WordSeg.tokenize(str(sent)))
    # print(words)
    # train_word_and_char(file, words, True)

    # 测试 DataManager
    data_manager = DataManager('./tmp')
    for ii in data_manager.SearchingByConstraints('流量', {"套餐内容_国内流量_文字描述": '高'}):
        print(ii)
    # for ii in data_manager.SearchingByEntity("套餐", {"子业务": '88元畅享套餐'}):
    #     print(ii)

    # # 测试 sent2num
    # data_manager = DataManager('./tmp')
    # print(data_manager.sent2num([["要", "价格", "贵","的"]],5, 3))

    # # 展现某些训练数据
    # data_manager = DataManager('./tmp')
    # for ii in data_manager.DialogData['id71']['用户回复示例']:
    #     print(ii)




