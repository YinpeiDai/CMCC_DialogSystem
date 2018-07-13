from data.DataManager import DataManager
import random, copy, pprint

class InformableSlotDataset:
    def __init__(self,
                 high_data,
                 medium_data,
                 low_data,
                 none_data):
        """
        产生训练数据一个 minibatch size 为 32，高、中、低、无 比例为 1:1:1:5
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
        self.high_batch_id = 0
        self.medium_batch_id = 0
        self.low_batch_id = 0
        self.none_batch_id = 0


    def next_batch(self, batch_size=32):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        if self.high_batch_id+4>=len(self.high_data):
            self.high_batch_id = 0
            random.shuffle(self.high_data)
        if self.medium_batch_id+4>=len(self.medium_data):
            self.medium_batch_id = 0
            random.shuffle(self.medium_data)
        if self.low_batch_id+4>=len(self.low_data):
            self.low_batch_id = 0
            random.shuffle(self.low_data)
        if self.none_batch_id+20>=len(self.none_data):
            self.none_batch_id = 0
            random.shuffle(self.none_data)

        batch_data = self.high_data[self.high_batch_id:self.high_batch_id+4]+ \
                     self.medium_data[self.medium_batch_id:self.medium_batch_id + 4] + \
                     self.low_data[self.low_batch_id:self.low_batch_id + 4] + \
                     self.none_data[self.none_batch_id:self.none_batch_id + 20]
        self.high_batch_id += 4
        self.low_batch_id += 4
        self.medium_batch_id += 4
        self.none_batch_id += 20

        batch_output = [0]*4+[1]*4+[2]*4+[3]*20
        return batch_data, batch_output

class RequestableSlotDataset:
    def __init__(self,
                 positive_data,
                 negative_data):
        """
        产生训练数据一个 minibatch size 为 24，比例为 1:5
        requestable slots 检测是否出现
        """
        self.positive_data = positive_data
        self.negative_data = negative_data
        random.shuffle(self.positive_data)
        random.shuffle(self.negative_data)
        self.positive_batch_id = 0
        self.negative_batch_id = 0


    def next_batch(self, batch_size=24):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        if self.positive_batch_id+4>=len(self.positive_data):
            self.positive_batch_id = 0
            random.shuffle(self.positive_data)
        if self.negative_batch_id+20>=len(self.negative_data):
            self.negative_batch_id = 0
            random.shuffle(self.negative_data)

        batch_data = self.positive_data[self.positive_batch_id:self.positive_batch_id+4]+ \
                     self.negative_data[self.negative_batch_id:self.negative_batch_id+20]
        self.positive_batch_id += 4
        self.negative_batch_id += 20

        batch_output = [0]*4+[1]*20
        return batch_data, batch_output

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
    pprint.pprint(informable_slot_dataset_cost.next_batch())





