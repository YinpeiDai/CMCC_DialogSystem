"""
业务实体识别
"""

entity_list = [

]

class EntityDetector:
    def __init__(self, entity_list_file):
        with open(entity_list_file, 'r', encoding='utf-8') as f:
            self.entity_list = f.read().splitlines()
        self.entity_detected = []

    def get_ER_results(self, user_utter):
        """
        找到句中的业务实体，并将相应地方去词汇化或直接去掉，返回 (业务实体结果，处理后句子)
        :param user_utter: 输入语句
        :return: tuple
        """
        self.entity_detected = []
        for entity in self.entity_list:
            # 子业务名经常包括主业务，可以通过
            # 将主业务放到entity_list的后面解决
            # 因为在找到子业务时，这个业务就被替换成了ENT
            if entity in user_utter:
                if user_utter[user_utter.find(entity)-1].isnumeric():
                    pass
                else:
                    self.entity_detected.append(entity)
                    user_utter = user_utter.replace(entity,'ENT')
        return (self.entity_detected, user_utter)

    def close(self):
        pass

if __name__ == '__main__':
    ED = EntityDetector('entity_list.txt')
    print(ED.entity_list)
    user_utter = '亲情通真好用'
    print(ED.get_ER_results(user_utter))