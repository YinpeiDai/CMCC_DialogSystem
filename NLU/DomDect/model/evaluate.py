import sys
sys.path.append('../../..')
import tensorflow as tf
import copy, pprint, os
from data.DataManager import DataManager
from NLU.DomDect.input_data import *
# from NLU.DomDect.model import *
os.environ["CUDA_VISIBLE_DEVICES"]="1"

def evaluate(domain_dataset):
    """
    用于训练模型，先训练完存好了才能用
    :param data_tmp_path:  data tmp 文件夹位置
    """
    print('载入 Domain 模型...')
    model = DomainDetector("DomDect")

    with tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True)) as sess:
        sess.run(tf.group(tf.global_variables_initializer()))
        saver = tf.train.Saver()
        saver.restore(sess, "./ckpt/model.ckpt")

        # 训练 domain detector model
        for domain in domains:
            step_count = 0
            average_loss = 0
            average_accu = 0
            domain_dataset.batch_id[domain] = 0
            while True:
                step_count += 1
                batch_data, batch_output, end_flag = domain_dataset.test_data_batch(domain, 100)
                char_emb_matrix, word_emb_matrix, seqlen = data_manager.sent2num(batch_data, 40, 6)
                loss, accu, predictions = sess.run(
                    [model.final_loss, model.accuracy, model.predict],
                    feed_dict={ model.char_emb_matrix: char_emb_matrix,
                                       model.word_emb_matrix: word_emb_matrix,
                                       model.output: batch_output})
                average_loss += loss
                average_accu += accu
                if domain == "号卡":
                    print(predictions)
                # print(testing_accu)
                if end_flag:
                    average_loss /= step_count
                    average_accu /= step_count
                    break
            print("domain:"+domain+ ", loss %0.4f, accu %0.4f" % (average_loss, average_accu))
            print("domain:"+domain+ ", num %d" %len(domain_dataset.data[domain]))
            with open('test_result.txt', 'a') as f:
                f.write("domain:"+domain+ ", loss %0.4f, accu %0.4f\n" % (average_loss, average_accu))

if __name__ == '__main__':
    print('载入数据管理器...')
    data_manager = DataManager('../../../data/tmp')

    print('载入训练数据...')
    domain_dataset = generate_domain_dataset(data_manager.DialogData,
        domain_data_ids)

    evaluate(domain_dataset)

