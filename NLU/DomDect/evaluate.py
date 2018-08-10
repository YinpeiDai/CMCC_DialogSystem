import sys
sys.path.append('../..')
import tensorflow as tf
import copy, pprint, os
from data.DataManager import DataManager
from NLU.DomDect.input_data import *
# from NLU.DomDect.model import *
os.environ["CUDA_VISIBLE_DEVICES"]="1"

# requestable slots 对应的 DialogData20180613 的 id, 用于指导生成训练数据
class DomainDetector:
    """
    一个简单的 CNN
    文字描述，输出为 高、中、低、无
    功能费、流量、通话
    """
    def __init__(self, name,
                 max_sent_length=40,
                 max_word_length=6, # 没用到，因为我 charCNN 取得是均值
                 word_embed_size=20,
                 char_embed_size=20,
                 hidden_size=60,
                 learning_rate=0.01,
                 word_feature_map=10 # window 1,2,3
                 ):
        self.name = name
        with tf.device('/gpu:0'), tf.variable_scope(name_or_scope=self.name,
                                                    initializer=tf.truncated_normal_initializer(0, 0.1)):
            self.word_emb_matrix = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, word_embed_size])
            self.char_emb_matrix = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, char_embed_size])
            self.input = tf.concat([self.word_emb_matrix, self.char_emb_matrix], 2)
            self.output = tf.placeholder(dtype=tf.int32, shape=(None))
            self.batch_size = tf.shape(self.word_emb_matrix)[0]

            def conv_relu(inputs, filters, kernel, poolsize):
                conv = tf.layers.conv1d(
                    inputs=inputs,
                    filters=filters,
                    kernel_size=kernel,
                    strides=1,
                    padding='same',
                    activation=tf.nn.relu,
                    kernel_initializer=tf.random_normal_initializer(0, 0.01)
                )
                # print('conv:', conv.get_shape())
                pool = tf.layers.max_pooling1d(
                    inputs=conv,
                    pool_size=poolsize,
                    strides=1,
                )
                # print('pool:', pool.get_shape())
                _pool = tf.squeeze(pool, [1])
                # print('_pool:', _pool.get_shape())
                return _pool
            def cnn(inputs, maxlength):
                with tf.variable_scope("winsize2"):
                    conv2 = conv_relu(inputs, word_feature_map, 1, maxlength)
                with tf.variable_scope("winsize3"):
                    conv3 = conv_relu(inputs, word_feature_map, 2, maxlength)
                with tf.variable_scope("winsize4"):
                    conv4 = conv_relu(inputs, word_feature_map, 3, maxlength)
                return tf.concat([conv2, conv3, conv4], 1)
            with tf.variable_scope("CNN_output"):
                self.feature = cnn(self.input, max_sent_length)
                # print('cnn_output:', self.feature.get_shape())
            with tf.variable_scope("projection"):
                self.final_output_logits = tf.layers.dense(inputs=self.feature,
                                                    units=7,
                                                    activation=tf.nn.relu)

                # print(self.final_output_logits.get_shape())

            with tf.variable_scope("loss"):
                self.loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                    logits=self.final_output_logits,
                    labels=self.output)
                # print(self.loss.get_shape())

                # self.final_loss = tf.reduce_mean(self.loss)
                # print(self.final_loss.get_shape())

            with tf.variable_scope("train"):
                self.lr = tf.Variable(learning_rate, trainable=False)
                self.new_lr = tf.placeholder(dtype=tf.float32, shape=[], name="new_learning_rate")
                self.lr_update = tf.assign(self.lr, self.new_lr)
                self.tvars = tf.get_collection(key=tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)
                self.optimizer = tf.train.AdamOptimizer(self.lr)
                self.l2_loss = [tf.nn.l2_loss(v) for v in self.tvars]
                self.final_loss = tf.reduce_mean(self.loss) + 0.0001 * tf.add_n(self.l2_loss)
                self.train_op = self.optimizer.minimize(self.final_loss)

            with tf.variable_scope("predict"):
                # predict
                self.predict = tf.argmax(self.final_output_logits, axis=1)
                # print(self.predict.get_shape())
                self.correct = tf.equal(tf.cast(self.predict, tf.int32),
                                        tf.cast(self.output, tf.int32))
                self.accuracy = tf.reduce_mean(tf.cast(self.correct, tf.float32))

    def assign_lr(self, session, lr_value):
        session.run(self.lr_update, feed_dict={self.new_lr: lr_value})


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
    data_manager = DataManager('../../data/tmp')

    print('载入训练数据...')
    domain_dataset = generate_domain_dataset(data_manager.DialogData,
        domain_data_ids)

    evaluate(domain_dataset)



