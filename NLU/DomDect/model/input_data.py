<<<<<<< Updated upstream
import sys
sys.path.append('../../..')
from data.DataManager import DataManager
import random, copy, pprint

domains = ["个人", "套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端" ]
domain_data_ids = {
    '号卡': ['id118', 'id116'],
    '套餐': ['id25', 'id35', 'id60', 'id107', 'id91', 'id47', 'id97', 'id98', 'id124', 'id19',
                'id89', 'id106', 'id51', 'id86', 'id36', 'id62', 'id48', 'id42', 'id45', 'id40',
                'id110', 'id93', 'id56', 'id71', 'id33', 'id72', 'id46', 'id31', 'id81', 'id102',
                'id53', 'id26', 'id100', 'id111', 'id34', 'id75', 'id22', 'id59', 'id44', 'id119',
                'id58', 'id76', 'id61', 'id21', 'id87', 'id70', 'id83', 'id64', 'id65', 'id43', 'id28',
                'id74', 'id109', 'id103','id50', 'id101', 'id94', 'id92', 'id85', 'id82', 'id99',
                'id90', 'id52', 'id95', 'id57', 'id80', 'id37', 'id55', 'id38', 'id77', 'id73',
                'id63', 'id96', 'id20', 'id54', 'id105', 'id84', 'id27', 'id104', 'id49', 'id88',
                'id78', 'id39', 'id41', 'id79',  'id108',],
    '流量': ['id24', 'id121', 'id29', 'id123', 'id32', 'id122', 'id68', 'id66', 'id30', 'id67',
                'id23', 'id69'],
    '个人': ['id2', 'id7', 'id16', 'id8', 'id17', 'id5', 'id18', 'id10', 'id1', 'id14', 'id6', 'id15',
                'id13', 'id3', 'id4', 'id9', 'id11', 'id12'],
    '国际港澳台': ['id150', 'id151', 'id142', 'id145', 'id146', 'id152', 'id140', 'id143',
                          'id141', 'id149', 'id148', 'id153', 'id147', 'id144'],
    'WLAN': ['id115', 'id114', 'id117', 'id112', 'id113'],
    '家庭多终端': ['id134', 'id127', 'id139', 'id128', 'id135', 'id132', 'id131', 'id129',
                          'id120', 'id133', 'id130', 'id126', 'id136', 'id138', 'id125', 'id137']
}


'''
号卡, count:2
套餐, count:86
流量, count:12
个人, count:18
国际港澳台, count:14
WLAN, count:5
家庭多终端, count:16
'''

class DomainDataset:
    def __init__(self,
                Personal_data,
                TaoCao_data,
                LiuLiang_data,
                WLAN_data,
                Card_data,
                Overseas_data,
                MultiTerminal_data):
        """
        产生训练数据一个 minibatch size 为 40，
        个人：套餐：流量：WLAN：号卡：国际港澳台：家庭多终端 =
        5：17：5：2：1：5：5
        :param high_data: 对应标签是 高 的数据
        :param medium_data: 对应标签是 中 的数据
        :param low_data: 对应标签是 低 的数据
        :param none_data: 对应标签是 无 的数据
        """
        self.data = {}
        self.data["个人"] = Personal_data
        self.data["套餐"] = TaoCao_data
        self.data["流量"] = LiuLiang_data
        self.data["WLAN"] = WLAN_data
        self.data["号卡"] = Card_data
        self.data["国际港澳台"] = Overseas_data
        self.data["家庭多终端"] = MultiTerminal_data

        self.batch_size = {
            '个人': 5,
            '套餐': 17,
            '流量': 5,
            'WLAN': 2,
            '号卡': 1,
            '国际港澳台': 5,
            '家庭多终端': 5,
        }

        self.batch_id = {}
        for domain in domains:
            random.shuffle(self.data[domain])
            self.batch_id[domain] = 0

    def next_batch(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        for domain in domains:
            if self.batch_id[domain] + self.batch_size[domain] >= len(self.data[domain]):
                self.batch_id[domain] = 0
                # print(domain+" epoch done!")
                random.shuffle(self.data[domain])

        batch_data = []
        for domain in domains:
            bid = self.batch_id[domain]
            bsz = self.batch_size[domain]
            batch_data += self.data[domain][bid : bid+bsz]
            self.batch_id[domain] += bsz

        batch_output = []
        domain_id = 0
        for domain in domains:
            # label = [0,0,0,0,0,0,0]
            # label[domain_id] = 1
            # batch_output += [label] * self.batch_size[domain]
            batch_output += [domain_id] * self.batch_size[domain]
            domain_id += 1

        return batch_data, batch_output

    def test_data_batch(self, domain, test_batchsize):

        batch_data = []
        end_flag = False
        bid = self.batch_id[domain]
        if self.batch_id[domain] + test_batchsize >= len(self.data[domain]):
            batch_data += self.data[domain][bid : ]
            end_flag = True
        else:
            batch_data += self.data[domain][bid : bid+test_batchsize]
        self.batch_id[domain] += test_batchsize

        batch_output = []
        domain_id = domains.index(domain)
        batch_output += [domain_id] * len(batch_data)

        return batch_data, batch_output, end_flag

def generate_domain_dataset(DialogData, domain_data_ids):
    dialog_data = copy.deepcopy(DialogData)
    domain_datas = {}
    for domain, data_ids in domain_data_ids.items():
        domain_datas[domain] = []
        for data_id in data_ids:
            domain_datas[domain] += dialog_data[data_id]["用户回复示例"]
    domain_dataset = DomainDataset(
        domain_datas['个人'],
        domain_datas['套餐'],
        domain_datas['流量'],
        domain_datas['WLAN'],
        domain_datas['号卡'],
        domain_datas['国际港澳台'],
        domain_datas['家庭多终端'])
    return domain_dataset



if __name__ == '__main__':
    data_manager = DataManager('../../../data/tmp')
    domain_dataset = generate_domain_dataset(
        data_manager.DialogData,  domain_data_ids)
    binput,boutput = domain_dataset.next_batch()
    pprint.pprint(domain_dataset.next_batch())
    binput,boutput = domain_dataset.next_batch()
    pprint.pprint(domain_dataset.next_batch())




=======
import sys
sys.path.append('../../..')
from data.DataManager import DataManager
import random, copy, pprint

domains = ["个人", "套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端" ]
domain_data_ids = {
    '号卡': ['id118', 'id116'],
    '套餐': ['id25', 'id35', 'id60', 'id107', 'id91', 'id47', 'id97', 'id98', 'id124', 'id19',
                'id89', 'id106', 'id51', 'id86', 'id36', 'id62', 'id48', 'id42', 'id45', 'id40',
                'id110', 'id93', 'id56', 'id71', 'id33', 'id72', 'id46', 'id31', 'id81', 'id102',
                'id53', 'id26', 'id100', 'id111', 'id34', 'id75', 'id22', 'id59', 'id44', 'id119',
                'id58', 'id76', 'id61', 'id21', 'id87', 'id70', 'id83', 'id64', 'id65', 'id43', 'id28',
                'id74', 'id109', 'id103','id50', 'id101', 'id94', 'id92', 'id85', 'id82', 'id99',
                'id90', 'id52', 'id95', 'id57', 'id80', 'id37', 'id55', 'id38', 'id77', 'id73',
                'id63', 'id96', 'id20', 'id54', 'id105', 'id84', 'id27', 'id104', 'id49', 'id88',
                'id78', 'id39', 'id41', 'id79',  'id108',],
    '流量': ['id24', 'id121', 'id29', 'id123', 'id32', 'id122', 'id68', 'id66', 'id30', 'id67',
                'id23', 'id69'],
    '个人': ['id2', 'id7', 'id16', 'id8', 'id17', 'id5', 'id18', 'id10', 'id1', 'id14', 'id6', 'id15',
                'id13', 'id3', 'id4', 'id9', 'id11', 'id12'],
    '国际港澳台': ['id150', 'id151', 'id142', 'id145', 'id146', 'id152', 'id140', 'id143',
                          'id141', 'id149', 'id148', 'id153', 'id147', 'id144'],
    'WLAN': ['id115', 'id114', 'id117', 'id112', 'id113'],
    '家庭多终端': ['id134', 'id127', 'id139', 'id128', 'id135', 'id132', 'id131', 'id129',
                          'id120', 'id133', 'id130', 'id126', 'id136', 'id138', 'id125', 'id137']
}


'''
号卡, count:2
套餐, count:86
流量, count:12
个人, count:18
国际港澳台, count:14
WLAN, count:5
家庭多终端, count:16
'''

class DomainDataset:
    def __init__(self,
                Personal_data,
                TaoCao_data,
                LiuLiang_data,
                WLAN_data,
                Card_data,
                Overseas_data,
                MultiTerminal_data):
        """
        产生训练数据一个 minibatch size 为 40，
        个人：套餐：流量：WLAN：号卡：国际港澳台：家庭多终端 =
        5：17：5：2：1：5：5
        :param high_data: 对应标签是 高 的数据
        :param medium_data: 对应标签是 中 的数据
        :param low_data: 对应标签是 低 的数据
        :param none_data: 对应标签是 无 的数据
        """
        self.data = {}
        self.data["个人"] = Personal_data
        self.data["套餐"] = TaoCao_data
        self.data["流量"] = LiuLiang_data
        self.data["WLAN"] = WLAN_data
        self.data["号卡"] = Card_data
        self.data["国际港澳台"] = Overseas_data
        self.data["家庭多终端"] = MultiTerminal_data

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
            '个人': 6,
            '套餐': 10,
            '流量': 6,
            'WLAN': 3,
            '号卡': 3,
            '国际港澳台': 6,
            '家庭多终端': 6,
        }

        self.batch_id = {}
        for domain in domains:
            random.shuffle(self.data[domain])
            self.batch_id[domain] = 0

        self.train_data = {}
        self.valid_data = {}
        for domain in domains:
            domain_num = len(self.data[domain])
            split = int(domain_num*0.9)
            self.train_data[domain] = self.data[domain][0:split]
            # if domain in ['个人','流量','国际港澳台','家庭多终端']:
            #     self.train_data[domain] *= 5
            # if domain in ['WLAN', '号卡']:
            #     self.train_data[domain] *= 25
            self.valid_data[domain] = self.data[domain][split:]

    def next_train_batch(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        for domain in domains:
            if self.batch_id[domain] + self.batch_size[domain] >= len(self.train_data[domain]):
                self.batch_id[domain] = 0
                # print(domain+" epoch done!")
                random.shuffle(self.train_data[domain])

        batch_data = []
        for domain in domains:
            bid = self.batch_id[domain]
            bsz = self.batch_size[domain]
            batch_data += self.train_data[domain][bid : bid+bsz]
            self.batch_id[domain] += bsz

        batch_output = []
        domain_id = 0
        for domain in domains:
            # label = [0,0,0,0,0,0,0]
            # label[domain_id] = 1
            # batch_output += [label] * self.batch_size[domain]
            batch_output += [domain_id] * self.batch_size[domain]
            domain_id += 1

        return batch_data, batch_output

    def produce_valid_data(self):
        """
        Return a batch of data. When dataset end is reached, start over.
        """
        batch_data = []
        for domain in domains:
            batch_data += self.valid_data[domain]

        batch_output = []
        domain_id = 0
        for domain in domains:
            # label = [0,0,0,0,0,0,0]
            # label[domain_id] = 1
            # batch_output += [label] * self.batch_size[domain]
            batch_output += [domain_id] * len(self.valid_data[domain])
            domain_id += 1

        return batch_data, batch_output


    def test_by_domain(self, domain, test_batchsize):

        batch_data = []
        end_flag = False
        bid = self.batch_id[domain]
        if self.batch_id[domain] + test_batchsize >= len(self.valid_data[domain]):
            batch_data += self.valid_data[domain][bid : ]
            end_flag = True
        else:
            batch_data += self.valid_data[domain][bid : bid+test_batchsize]
        self.batch_id[domain] += test_batchsize

        batch_output = []
        domain_id = domains.index(domain)
        batch_output += [domain_id] * len(batch_data)

        return batch_data, batch_output, end_flag

def generate_domain_dataset(DialogData, domain_data_ids):
    dialog_data = copy.deepcopy(DialogData)
    domain_datas = {}
    for domain, data_ids in domain_data_ids.items():
        domain_datas[domain] = []
        for data_id in data_ids:
            domain_datas[domain] += dialog_data[data_id]["用户回复示例"]
    domain_dataset = DomainDataset(
        domain_datas['个人'],
        domain_datas['套餐'],
        domain_datas['流量'],
        domain_datas['WLAN'],
        domain_datas['号卡'],
        domain_datas['国际港澳台'],
        domain_datas['家庭多终端'])
    return domain_dataset



if __name__ == '__main__':
    data_manager = DataManager('../../../data/tmp')
    domain_dataset = generate_domain_dataset(
        data_manager.DialogData,  domain_data_ids)
    binput,boutput = domain_dataset.next_batch()
    pprint.pprint(domain_dataset.next_batch())
    binput,boutput = domain_dataset.next_batch()
    pprint.pprint(domain_dataset.next_batch())




>>>>>>> Stashed changes
