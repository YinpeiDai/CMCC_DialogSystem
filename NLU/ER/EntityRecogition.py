"""
业务实体识别
"""

class EntityDetector:
    def __init__(self):
        pass

    def get_ER_results(self, user_utter):
        """
        找到句中的业务实体，并将相应地方去词汇化或直接去掉，返回 (业务实体结果，处理后句子)
        :param user_utter: 输入语句
        :return: tuple
        """
        return (None, user_utter)

    def close(self):
        pass