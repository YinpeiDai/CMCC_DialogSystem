import sys
sys.path.append('../../..')
from data.DataManager import DataManager
import random, copy, pprint

user_acts = [
    '问询', '告知', '要求更多', '要求更少', '更换', '问询说明', '话题=WLAN', '话题=号卡', '话题=套餐流量', '话题=资源分享',
    '同时办理', '比较', '闲聊'
]
user_act_data_ids = {
    '问询': ['id11', 'id97', 'id128', 'id116', 'id114', 'id76', 'id94', 'id103', 'id88', 'id137',
    'id10', 'id7', 'id73', 'id115', 'id112', 'id107', 'id108', 'id96', 'id100', 'id106', 'id109',
    'id74', 'id5', 'id90', 'id71', 'id77', 'id105', 'id87', 'id104', 'id102', 'id150', 'id110',
    'id75', 'id149', 'id80', 'id91', 'id4', 'id92', 'id133', 'id151', 'id12', 'id93', 'id78', 'id136',
    'id85', 'id83', 'id101', 'id99', 'id81', 'id111', 'id153', 'id135', 'id86', 'id126', 'id89', 'id95',
     'id6', 'id148', 'id98', 'id79', 'id127', 'id14', 'id1', 'id84', 'id18', 'id130', 'id82', 'id131',
     'id16', 'id9', 'id138', 'id134', 'id3', 'id132', 'id8', 'id125', 'id2', 'id129', 'id72', 'id139',
     'id113', 'id70', 'id152', 'id13', 'id15', 'id17'],
    '告知': ['id53', 'id54', 'id46', 'id58', 'id57', 'id49', 'id67', 'id142', 'id65', 'id39', 'id52',
    'id69', 'id41', 'id61', 'id143', 'id63', 'id66', 'id55', 'id140', 'id36', 'id60', 'id44', 'id50',
     'id47', 'id37', 'id35', 'id141', 'id59', 'id145', 'id62', 'id45', 'id146', 'id34', 'id51', 'id64',
      'id56', 'id42', 'id40', 'id144'],
    '更换': ['id33', 'id32', 'id31'],
    '同时办理': ['id123', 'id122', 'id121'],
    '话题=套餐流量': ['id119'],
    '话题=号卡': ['id118'],
    '话题=WLAN': ['id117'],
    '话题=资源分享': ['id120'],
    '比较': ['id147'],
    '要求更多': ['id20', 'id21', 'id19', 'id23', 'id22', 'id24'],
    '要求更少': ['id30', 'id29', 'id27', 'id28', 'id25', 'id26'],
    '闲聊': ['id124'],
    '问询通话时长选项': ['id43'],
    '问询费用选项': ['id38'],
    '问询流量选项': ['id68', 'id48'],
    # '问询说明': ['id43', 'id38', 'id68', 'id48', ],
}


'''
task count:
问询费用选项, count:1
问询流量选项, count:2
问询, count:86
告知, count:39
更换, count:3
同时办理, count:3
话题=套餐流量, count:1
比较, count:1
话题=号卡, count:1
话题=WLAN, count:1
话题=资源分享, count:1
要求更少, count:6
问询通话时长选项, count:1
闲聊, count:1
要求更多, count:6
'''

class UserActDataset:
    def __init__(self, user_act_data_dicts):
        """
        产生训练数据一个 minibatch size 为 40，
        个人：套餐：流量：WLAN：号卡：国际港澳台：家庭多终端 =
        5：17：5：2：1：5：5
        :param high_data: 对应标签是 高 的数据
        :param medium_data: 对应标签是 中 的数据
        :param low_data: 对应标签是 低 的数据
        :param none_data: 对应标签是 无 的数据
        """
        self.data = user_act_data_dicts

        # self.batch_size = {
        #     '个人': 5,
        #     '套餐': 17,
        #     '流量': 5,
        #     'WLAN': 2,
        #     '号卡': 1,
        #     '国际港澳台': 5,
        #     '家庭多终端': 5,
        # }
        self.batch_size = {
            '问询': 30,
            '告知': 20,
            '问询说明': 10,
            '更换': 10,
            '同时办理': 10,
            '话题=套餐流量': 10,
            '话题=号卡': 10,
            '话题=WLAN': 10,
            '话题=资源分享': 10,
            '比较': 10,
            '要求更多': 10,
            '要求更少': 10,
            '闲聊': 10,
        }

        self.batch_id = {}
        for user_act in user_acts:
            random.shuffle(self.data[user_act])
            self.batch_id[user_act] = 0

        self.train_data = {}
        self.valid_data = {}
        for user_act in user_acts:
            user_act_num = len(self.data[user_act])
            split = int(user_act_num*0.9)
            self.train_data[user_act] = self.data[user_act][0:split]
            self.valid_data[user_act] = self.data[user_act][split:]

    def next_train_batch(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        for user_act in user_acts:
            if self.batch_id[user_act] + self.batch_size[user_act] >= len(self.train_data[user_act]):
                self.batch_id[user_act] = 0
                # print(user_act+" epoch done!")
                random.shuffle(self.train_data[user_act])

        batch_data = []
        for user_act in user_acts:
            bid = self.batch_id[user_act]
            bsz = self.batch_size[user_act]
            batch_data += self.train_data[user_act][bid : bid+bsz]
            self.batch_id[user_act] += bsz

        batch_output = []
        user_act_id = 0
        for user_act in user_acts:
            # label = [0,0,0,0,0,0,0]
            # label[user_act_id] = 1
            # batch_output += [label] * self.batch_size[user_act]
            batch_output += [user_act_id] * self.batch_size[user_act]
            user_act_id += 1

        return batch_data, batch_output

    def produce_valid_data(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        batch_data = []
        for user_act in user_acts:
            batch_data += self.valid_data[user_act]

        batch_output = []
        user_act_id = 0
        for user_act in user_acts:
            # label = [0,0,0,0,0,0,0]
            # label[domain_id] = 1
            # batch_output += [label] * self.batch_size[user_act]
            batch_output += [user_act_id] * len(self.valid_data[user_act])
            user_act_id += 1

        return batch_data, batch_output


    def test_by_user_act(self, user_act, test_batchsize):

        batch_data = []
        end_flag = False
        bid = self.batch_id[user_act]
        if self.batch_id[user_act] + test_batchsize >= len(self.valid_data[user_act]):
            batch_data += self.valid_data[user_act][bid : ]
            end_flag = True
        else:
            batch_data += self.valid_data[user_act][bid : bid+test_batchsize]
        self.batch_id[user_act] += test_batchsize

        batch_output = []
        user_act_id = user_acts.index(user_act)
        batch_output += [user_act_id] * len(batch_data)

        return batch_data, batch_output, end_flag

def generate_user_act_dataset(DialogData, user_act_data_ids):
    dialog_data = copy.deepcopy(DialogData)
    user_act_datas = {}
    for user_act, data_ids in user_act_data_ids.items():
        if user_act in [ '问询费用选项', '问询通话时长选项', '问询流量选项']:
            user_act = '问询说明'
        if user_act not in user_act_datas.keys():
            user_act_datas[user_act] = []
        for data_id in data_ids:
            user_act_datas[user_act] += dialog_data[data_id]["用户回复示例"]
    user_act_dataset = UserActDataset(user_act_datas)
    return user_act_dataset



if __name__ == '__main__':
    data_manager = DataManager('../../../data/tmp')
    user_act_dataset = generate_user_act_dataset(
        data_manager.DialogData,  user_act_data_ids)
    for user_act, data in user_act_dataset.data.items():
        print(user_act)
        print(len(data))
    # binput,boutput = domain_dataset.next_batch()
    # pprint.pprint(domain_dataset.next_batch())
    # binput,boutput = domain_dataset.next_batch()
    # pprint.pprint(domain_dataset.next_batch())

