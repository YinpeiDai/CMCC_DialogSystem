import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../../..'))

from data.DataManager import DataManager
import random, copy, pprint
# random.seed(1234)

class InformableSlotDataset:
    def __init__(self,
                 high_data,
                 medium_data,
                 low_data,
                 none_data):
        """
        产生训练数据一个 minibatch size 为 16，高、中、低、无 比例为 1:1:1:1
        :param high_data: 对应标签是 高 的数据
        :param medium_data: 对应标签是 中 的数据
        :param low_data: 对应标签是 低 的数据
        :param none_data: 对应标签是 无 的数据
        """
        self.high_data = high_data
        self.medium_data = medium_data
        self.low_data = low_data
        self.none_data = none_data
        random.shuffle(self.high_data)
        random.shuffle(self.medium_data)
        random.shuffle(self.low_data)
        random.shuffle(self.none_data)

        # 分训练集 和 测试集  6:1
        split = 7
        self.test_high_data = self.high_data[: len(self.high_data)//split]
        self.test_medium_data = self.medium_data[: len(self.medium_data) // split]
        self.test_low_data = self.low_data[: len(self.low_data) // split]
        self.test_none_data = self.none_data[: len(self.none_data) // split]

        self.train_high_data = self.high_data[len(self.high_data) // split :]
        self.train_medium_data = self.medium_data[len(self.medium_data) // split :]
        self.train_low_data = self.low_data[len(self.low_data) // split :]
        self.train_none_data = self.none_data[len(self.none_data) // split :]

        # 节约内存
        del self.high_data
        del self.medium_data
        del self.low_data
        del self.none_data


        self.high_batch_id = 0
        self.medium_batch_id = 0
        self.low_batch_id = 0
        self.none_batch_id = 0


    def next_batch(self, batch_ratio):
        """
        Return a batch of data. When dataset end is reached, start over.
        :param batch_ratio: high:medium,low,none
        :return:
        """
        if self.high_batch_id+batch_ratio[0]>=len(self.train_high_data):
            self.high_batch_id = 0
            random.shuffle(self.train_high_data)
        if self.medium_batch_id+batch_ratio[1]>=len(self.train_medium_data):
            self.medium_batch_id = 0
            random.shuffle(self.train_medium_data)
        if self.low_batch_id+batch_ratio[2]>=len(self.train_low_data):
            self.low_batch_id = 0
            random.shuffle(self.train_low_data)
        if self.none_batch_id+batch_ratio[3]>=len(self.train_none_data):
            self.none_batch_id = 0
            random.shuffle(self.train_none_data)

        batch_data = self.train_high_data[self.high_batch_id:self.high_batch_id+batch_ratio[0]]+ \
                     self.train_medium_data[self.medium_batch_id:self.medium_batch_id + batch_ratio[1]] + \
                     self.train_low_data[self.low_batch_id:self.low_batch_id + batch_ratio[2]] + \
                     self.train_none_data[self.none_batch_id:self.none_batch_id + batch_ratio[3]]
        self.high_batch_id += batch_ratio[0]
        self.medium_batch_id += batch_ratio[1]
        self.low_batch_id += batch_ratio[2]
        self.none_batch_id += batch_ratio[3]

        batch_output = [0]*batch_ratio[0]+[1]*batch_ratio[1]+[2]*batch_ratio[2]+[3]*batch_ratio[3]
        return batch_data, batch_output

    def get_testset(self):
        test_data = self.test_high_data + self.test_medium_data + \
            self.test_low_data + self.test_none_data
        test_output = [0] * len(self.test_high_data) + [1] * len(self.test_medium_data) + \
                      [2] * len(self.test_low_data) + [3] * len(self.test_none_data)
        return test_data, test_output


class RequestableSlotDataset:
    def __init__(self,
                 positive_data,
                 negative_data):
        """
        产生训练数据一个 minibatch size 为 24，比例为 5:10
        requestable slots 检测是否出现
        """
        self.positive_data = positive_data
        self.negative_data = negative_data
        random.shuffle(self.positive_data)
        random.shuffle(self.negative_data)

        # 分训练集 和 测试集  6:1
        split = 7
        self.test_positive_data = self.positive_data[: len(self.positive_data) // split]
        self.test_negative_data = self.negative_data[: len(self.negative_data) // split]

        self.train_positive_data = self.positive_data[len(self.positive_data) // split:]
        self.train_negative_data = self.negative_data[len(self.negative_data) // split:]

        # 节约内存
        del self.positive_data
        del self.negative_data

        self.positive_batch_id = 0
        self.negative_batch_id = 0


    def next_batch(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        if self.positive_batch_id+5>=len(self.train_positive_data):
            self.positive_batch_id = 0
            random.shuffle(self.train_positive_data)
        if self.negative_batch_id+10>=len(self.train_negative_data):
            self.negative_batch_id = 0
            random.shuffle(self.train_negative_data)

        batch_data = self.train_positive_data[self.positive_batch_id:self.positive_batch_id+5]+ \
                     self.train_negative_data[self.negative_batch_id:self.negative_batch_id+10]
        self.positive_batch_id += 5
        self.negative_batch_id += 10

        batch_output = [0]*5+[1]*10
        return batch_data, batch_output

    def get_testset(self):
        test_data = self.test_positive_data + self.test_negative_data
        test_output = [0] * len(self.test_positive_data) + [1] * len(self.test_negative_data)
        return test_data, test_output


if __name__ == '__main__':
    data_manager = DataManager('../../../data/tmp')
    def extract_training_data(DialogData, dict):
        dialog_data = copy.deepcopy(DialogData)
        high_data = []
        for id in dict['高']:
            high_data.extend(dialog_data[id]["用户回复示例"])
            del dialog_data[id]
        medium_data = []
        for id in dict['中']:
            medium_data.extend(dialog_data[id]["用户回复示例"])
            del dialog_data[id]
        low_data = []
        for id in dict['低']:
            low_data.extend(dialog_data[id]["用户回复示例"])
            del dialog_data[id]
        none_data = []
        for id, item in dialog_data.items():
            none_data.extend(item["用户回复示例"])
        return high_data, medium_data, low_data, none_data


    informable_slot_dataset_cost = InformableSlotDataset(
        *extract_training_data(data_manager.DialogData,
                              {"高":["id36", "id51"],
                               "中":["id35", "id50"],
                               "低":["id34", "id49"]}))
    pprint.pprint(informable_slot_dataset_cost.next_batch([4,8,8,8]))





