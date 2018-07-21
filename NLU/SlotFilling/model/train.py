import tensorflow as tf
import numpy as np
import copy, pprint, os
from data.DataManager import DataManager
from NLU.SlotFilling.model.input_data import InformableSlotDataset, RequestableSlotDataset
from NLU.SlotFilling.model.model import InformableSlotDector, RequestableSlotDector



# requestable slots 对应的 DialogData20180613 的 id, 用于指导生成训练数据
All_requestable_slots = {
    '已购业务':['id1', 'id14'],
    '订购时间':['id2', 'id14'],
    '使用情况':['id3'],
    '号码':['id4'],
    '归属地':['id5'],
    '品牌':['id6'],
    '是否转品牌过渡期':['id7'],
    '是否停机':['id8'],
    '账单查询':['id9'],
    '话费充值':['id10','id15','id16'],
    '流量充值':['id11','id15','id17'],
    '话费查询':['id12','id16','id18'],
    '流量查询':['id13','id17','id18'],
    '功能费':['id22','id24','id28','id30','id71','id38'],
    '套餐内容_国内主叫':['id20','id26','id72','id149', 'id43'],
    '套餐内容_国内流量':['id19','id23','id25','id29','id75','id152','id68','id48'],
    '产品介绍':['id76'],
    '计费方式':['id77'],
    '适用品牌':['id70'],
    '套餐内容_国内短信':['id21','id27','id73','id150'],
    '套餐内容_国内彩信':['id74','id151'],
    '套餐内容_其他功能':['id78'],
    '套餐内容':['id79'],
    '超出处理_国内主叫':['id80','id153'],
    '超出处理_国内流量':['id81'],
    '超出处理':['id82','id115'],
    '结转规则_国内主叫':['id83'],
    '结转规则_国内流量':['id84'],
    '结转规则_赠送流量':['id85'],
    '结转规则':['id86'],
    '是否全国接听免费':['id87'],
    '能否结转滚存':['id88'],
    '能否分享':['id89','id91','id126','id127','id128'],
    '能否转赠':['id90','id92'],
    '转户转品牌管理':['id93'],
    '停机销号管理':['id94'],
    '赠送优惠活动':['id95'],
    '使用限制':['id96','id113'],
    '使用有效期':['id97'],
    '使用方式设置':['id98','id114'],
    '封顶规则':['id99'],
    '限速说明':['id100'],
    '受理时间':['id101'],
    '互斥业务':['id102','id129','id130'],
    '开通客户限制':['id103','id131','id132'],
    '累次叠加规则':['id104'],
    '开通方式':['id105'],
    '开通生效规则':['id106'],
    '是否到期自动取消':['id107'],
    '能否变更或取消':['id108'],
    '取消方式':['id109'],
    '取消变更生效规则':['id110'],
    '变更方式':['id111'],
    '密码重置方式':['id112'],
    '激活方式':['id116'],
    '副卡数量上限':['id125'],
    '主卡添加成员':['id134'],
    '主卡删除成员':['id135'],
    '副卡成员主动退出':['id136'],
    '主卡查询副卡':['id137'],
    '副卡查询主卡':['id138'],
    '恢复流量功能':['id139'],
    '开通方向':['id148']
}
All_requestable_slots_order = dict(zip(All_requestable_slots.keys(), range(len(All_requestable_slots.keys()))))

def extract_informable_data(DialogData, dict):
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

def extract_requestable_data(DialogData, list):
    dialog_data = copy.deepcopy(DialogData)
    positive_data = []
    negative_data = []
    for id in list:
        positive_data.extend(dialog_data[id]["用户回复示例"])
        del dialog_data[id]
    for id, item in dialog_data.items():
        negative_data.extend(item["用户回复示例"])
    return positive_data, negative_data

def generate_dataset(DialogData):
    """
    生成informable slots 和 requestable slots 的训练数据集
    """
    # 生成 功能费 相关的训练数据
    informable_slot_dataset_cost = InformableSlotDataset(
        *extract_informable_data(DialogData,
                                 {"高": ["id36", "id51"],
                                  "中": ["id35", "id50"],
                                  "低": ["id34", "id49"]}))
    # 通话时长 相关的训练数据
    informable_slot_dataset_time = InformableSlotDataset(
        *extract_informable_data(DialogData,
                                 {"高": ["id39", "id52"],
                                  "中": ["id40", "id53"],
                                  "低": ["id41", "id54"]}))
    # 流量 相关的训练数据
    informable_slot_dataset_data = InformableSlotDataset(
        *extract_informable_data(DialogData,
                                 {"高": ["id44", "id55"],
                                  "中": ["id45", "id56"],
                                  "低": ["id46", "id57"]}))
    informable_slot_datasets = {
        "功能费":informable_slot_dataset_cost,
        "流量": informable_slot_dataset_data,
        "通话时长":informable_slot_dataset_time
    }
    requestable_slot_datasets = {}
    for k,v in All_requestable_slots.items():
        requestable_slot_datasets[k] = \
            RequestableSlotDataset(*extract_requestable_data(DialogData, v))
    return informable_slot_datasets,requestable_slot_datasets

def get_F1score(correct, predict):
    """
    correct like [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    predict like [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
    :return: F1
    """
    hit = 0
    precision_set = 0
    recall_set = 0
    for i in range(len(correct)):
        if correct[i] == predict[i] and predict[i] == 0:
            hit += 1
        if correct[i] == 0 :
            precision_set += 1
        if predict[i] == 0:
            recall_set += 1
    return 2*hit/(precision_set + recall_set)

def train_informable(data_tmp_path):
    """
    用于训练模型，先训练完存好了才能用
    训练用 early stopping
    :param data_tmp_path:  data tmp 文件夹位置
    """
    print('载入数据管理器...')
    data_manager = DataManager(data_tmp_path)

    print('载入训练数据...')
    informable_slot_datasets, requestable_slot_datasets = generate_dataset(data_manager.DialogData)

    print('载入 informable slot detector ...')
    init_learning_rate = 0.01
    informable_batch_ratios = { # 不同slot 的minibatch ratio
        "通话时长": [2, 8, 8, 8],
        "流量": [4, 8, 8, 8],
        "功能费": [4, 8, 8, 8]
    }
    graph = tf.Graph()
    with graph.as_default():
        informable_slots_models = {
            "功能费": InformableSlotDector('cost', learning_rate=init_learning_rate),
            "流量": InformableSlotDector('data', learning_rate=init_learning_rate),
            "通话时长": InformableSlotDector('time', learning_rate=init_learning_rate),
        }
    with tf.Session(graph=graph,config=tf.ConfigProto(
            allow_soft_placement=True)) as sess:
        sess.run(tf.group(tf.global_variables_initializer()))
        saver = tf.train.Saver()
        # saver.restore(sess, "./ckpt/informable/model.ckpt")

        # 训练 informable slots
        informable_slots_accus = []
        for slot , model in informable_slots_models.items():
            learning_rate = init_learning_rate
            average_loss = 0
            best_accu = 0
            tolerance = 20
            tolerance_count = 0
            display_step = 10
            for step in range(5000):
                step += 1
                batch_data, batch_output = informable_slot_datasets[slot].next_batch(informable_batch_ratios[slot])
                char_emb_matrix, word_emb_matrix, seqlen = data_manager.sent2num(batch_data)
                _, training_loss = sess.run([model.train_op, model.final_loss],
                                            feed_dict={
                                                model.char_emb_matrix: char_emb_matrix,
                                                model.word_emb_matrix: word_emb_matrix,
                                                model.output: batch_output
                                               })
                average_loss += training_loss / display_step
                if step % display_step == 0:
                    batch_data, batch_output = informable_slot_datasets[slot].get_testset()
                    char_emb_matrix, word_emb_matrix, seqlen = data_manager.sent2num(batch_data)
                    pred, accu = sess.run([model.predict, model.accuracy],
                                    feed_dict={
                                        model.char_emb_matrix: char_emb_matrix,
                                        model.word_emb_matrix: word_emb_matrix,
                                        model.output: batch_output
                                    })
                    if best_accu < accu:
                        best_accu = accu
                        tolerance_count = 0
                        # if not os.path.exists("./ckpt/informable/"):
                        #     os.makedirs("./ckpt/informable/")
                        # saver.save(sess, "./ckpt/informable/model.ckpt")
                    if tolerance_count == tolerance:
                        break
                    print("%s, step % 4d, loss %0.4f, accu %0.4f" % (slot, step, average_loss, accu))
                    average_loss = 0
                    tolerance_count += 1
                    learning_rate = max(learning_rate*0.95, 0.0001)
                    sess.run(model.update_lr, feed_dict={model.new_lr: learning_rate})
            print("informable slot: %s, best accu %0.4f" % (slot, best_accu))
            informable_slots_accus.append(best_accu)

def train_requestable(data_tmp_path):
    """
    用于训练模型，先训练完存好了才能用
    训练用 early stopping
    :param data_tmp_path:  data tmp 文件夹位置
    """
    print('载入数据管理器...')
    data_manager = DataManager(data_tmp_path)

    print('载入训练数据...')
    informable_slot_datasets, requestable_slot_datasets = generate_dataset(data_manager.DialogData)

    print('载入 requestable slot detector...')
    init_learning_rate = 0.01
    graph = tf.Graph()
    with graph.as_default():
        requestable_slots_models = {}
        for k, v in All_requestable_slots_order.items():
            requestable_slots_models[k] = RequestableSlotDector(str(v), learning_rate=init_learning_rate)

    with tf.Session(graph=graph,config=tf.ConfigProto(
            allow_soft_placement=True)) as sess:
        sess.run(tf.group(tf.global_variables_initializer()))
        saver = tf.train.Saver()
        saver.restore(sess, "./ckpt/requestable/model.ckpt")
        # 训练 requestable slots
        requestable_slots_F1s = {}
        for slot, model in requestable_slots_models.items():
            average_loss = 0
            learning_rate = init_learning_rate
            best_F1 = 0
            tolerance = 30
            tolerance_count = 0
            display_step = 10
            for step in range(5000):
                step += 1
                batch_data, batch_output = requestable_slot_datasets[slot].next_batch()
                char_emb_matrix, word_emb_matrix, seqlen = data_manager.sent2num(batch_data)

                _, training_loss = sess.run([model.train_op, model.final_loss],
                                            feed_dict={
                                                model.char_emb_matrix: char_emb_matrix,
                                                model.word_emb_matrix: word_emb_matrix,
                                                model.output: batch_output
                                            })
                average_loss += training_loss / display_step
                if step % display_step == 0:
                    batch_data, batch_output = requestable_slot_datasets[slot].get_testset()
                    char_emb_matrix, word_emb_matrix, seqlen = data_manager.sent2num(batch_data)
                    pred, accu = sess.run([model.predict, model.accuracy],
                                          feed_dict={
                                              model.char_emb_matrix: char_emb_matrix,
                                              model.word_emb_matrix: word_emb_matrix,
                                              model.output: batch_output
                                          })
                    F1 = get_F1score(batch_output, pred.tolist())
                    if best_F1 < F1:
                        best_F1 = F1
                        tolerance_count = 0
                        # if not os.path.exists("./ckpt/requestable/"):
                        #     os.makedirs("./ckpt/requestable/")
                        # saver.save(sess, "./ckpt/requestable/model.ckpt")
                    if tolerance_count == tolerance:
                        break
                    print("%s, step % 4d, loss %0.4f, F1 %0.4f, accu %0.4f" % (slot, step, average_loss, F1, accu))
                    average_loss = 0
                    tolerance_count += 1
                    learning_rate = max(learning_rate * 0.98, 0.001)
                    sess.run(model.update_lr, feed_dict={model.new_lr: learning_rate})
            print("requestable slot: %s, best F1 %0.4f" % (slot, best_F1))
            requestable_slots_F1s[slot] = best_F1
        print(requestable_slots_F1s)
        print(sum(requestable_slots_F1s.values())/len(requestable_slots_F1s.values()))


if __name__ == '__main__':
    train_informable('../../../data/tmp')
    train_requestable('../../../data/tmp')
