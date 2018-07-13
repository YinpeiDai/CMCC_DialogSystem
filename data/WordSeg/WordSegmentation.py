import jieba, os

class WordSegWrapper:
    def __init__(self, save_path):
        add_words_file = os.path.join(save_path, '_add_words.txt')
        del_words_file = os.path.join(save_path, '_del_words.txt')
        with open(add_words_file, "r", encoding='utf-8') as f:
            for word in f:
                word = word.strip().lstrip('\ufeff')
                jieba.add_word(word)
        with open(del_words_file, "r", encoding='utf-8') as f:
            for word in f:
                word = word.strip().lstrip('\ufeff')
                jieba.del_word(word)

    def tokenize(self, sent):
        return list(jieba.cut(sent))


if __name__ == '__main__':
    # jieba.load_userdict("add_words.txt")
    CMCC_WordSeg = WordSegWrapper("../tmp")
    sent = "李小福是创新办主任也是云计算方面的专家；什么是八一双鹿\n"
    print(CMCC_WordSeg.tokenize(sent))
