"""
生成对话语料的词典
"""
import collections, os, json

class DictGenerator:
    def __init__(self, save_path, raw_data, word_dict_size = 1500, char_dict_size = 700):
        """
        词典生成器
        :param raw_data: 已经分好词的语料
        :param save_path: 存放路径
        :param dict_size: 词表大小（含UNK）
        """
        self.raw_data = raw_data
        self.save_path = save_path
        self.word_dict_size = word_dict_size
        self.char_dict_size = char_dict_size

    def generate_word_dict(self):
        """
        生成词表、逆词表、词频，词向量训练数据,存放到 save_path 文件夹中
        """
        word_count = [['UNK', -1]]
        word_dictionary = dict()
        word2vec_traindata = list()
        word_count.extend(collections.Counter(self.raw_data).most_common(self.word_dict_size - 1))
        for word, _ in word_count:
            word_dictionary[word] = len(word_dictionary)
        unk_count = 0
        for word in self.raw_data:

            if word in word_dictionary:
                index = word_dictionary[word]
            else:
                index = 0  # dictionary['UNK']
                unk_count += 1
            word2vec_traindata.append(index)
        word_count[0][1] = unk_count
        reversed_word_dictionary = dict(zip(word_dictionary.values(), word_dictionary.keys()))
        return word2vec_traindata, word_dictionary, reversed_word_dictionary, word_count

    def generate_char_dict(self):
        """
        生成字符表、逆字符表、字符频，字符向量训练数据,存放到 save_path 文件夹中
        """
        self.raw_data_string = "".join(self.raw_data)
        char_count = [['UNK', -1]]
        char_dictionary = dict()
        char2vec_traindata = list()
        char_count.extend(collections.Counter(self.raw_data_string).most_common(self.char_dict_size - 1))
        for char, _ in char_count:
            char_dictionary[char] = len(char_dictionary)
        unk_count = 0
        for char in self.raw_data_string:
            if char in char_dictionary:
                index = char_dictionary[char]
            else:
                index = 0  # dictionary['UNK']
                unk_count += 1
            char2vec_traindata.append(index)
        char_count[0][1] = unk_count
        reversed_char_dictionary = dict(zip(char_dictionary.values(), char_dictionary.keys()))
        return char2vec_traindata, char_dictionary, reversed_char_dictionary, char_count


if __name__ == '__main__':
    from data.WordSeg.WordSegmentation import WordSegWrapper
    with open('../tmp/DialogData20180613.json',  'r', encoding='utf-8') as f:
        dialog_data = json.load(f)
    CMCC_WordSeg = WordSegWrapper("../tmp")
    raw_data = []
    strings = ""
    for k, item in dialog_data.items():
        for sent in item["用户回复示例"]:
            strings += str(sent)
            raw_data.extend(CMCC_WordSeg.tokenize(str(sent)))
    print(len(collections.Counter(raw_data)))
    print(len(collections.Counter(strings)))


    # dictgenerator = DictGenerator(['李小福', '是', '创新办', '主任', '也', '是', '云', '计算', '方面', '的', '专家', '；', '什么', '是', '八一', '双鹿', '\n'],
    #                               "../tmp")
    # dictgenerator.generate_char_dict()
    # dictgenerator.generate_word_dict()
