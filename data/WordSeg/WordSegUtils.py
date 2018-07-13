"""
半自动生成 add_words 和 del_words
"""
import json
from .WordSegmentation import WordSegWrapper

def generate_new_words():
    """
    读取DialogData，找到新词
    """
    with open('../tmp/DialogData20180613.json',  'r', encoding='utf-8') as f:
        dialog_data = json.load(f)
    CMCC_WordSeg = WordSegWrapper('../tmp')
    count = 0
    for k, item in dialog_data.items():
        for sent in item["用户回复示例"]:
            count += 1
            print(sent)
            try:
                print(' | '.join(CMCC_WordSeg.tokenize(sent)))
            except Exception as e:
                pass
    print(count)

if __name__ == '__main__':
    # generate_new_words()
    CMCC_WordSeg = WordSegWrapper("../tmp")
    ss = ["我每个月的流量都用不完，请帮我更换一个流量小一点的价格低一点的套餐",
          "有没有通话时长的套餐",
          "不多不少",
          "不太多，还行吧！",
          "没有用完的话能转至下月吗",
          "我能不能不要这个套餐了",
          "什么情况不能开副卡？"]
    for sent in ss:
        print(' | '.join(CMCC_WordSeg.tokenize(sent)))

