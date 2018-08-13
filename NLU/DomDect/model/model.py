"""
领域检测模型
"""
import tensorflow as tf

# requestable slots 对应的 DialogData20180613 的 id, 用于指导生成训练数据
class DomainModel:
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
                 word_feature_map=100, # window 1,2,3
                 dropout_rate = 0.7,
                 noise_scale = 0,
                 LSR_mix_rate = 0.1,
                 ):
        self.name = name
        with tf.device('/gpu:0'), tf.variable_scope(name_or_scope=self.name,
                                                    initializer=tf.truncated_normal_initializer(0, 0.1)):
            self.is_training = tf.placeholder(dtype=tf.bool)
            self.word_emb_matrix = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, word_embed_size])
            self.char_emb_matrix = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, char_embed_size])
            self.input = tf.concat([self.word_emb_matrix, self.char_emb_matrix], 2)
            self.input_noise = noise_scale * tf.random_normal(tf.shape(self.input))
            self.input = tf.cond(self.is_training, lambda: self.input + self.input_noise,
                                                                     lambda:  self.input )
            self.output = tf.placeholder(dtype=tf.int32, shape=(None))
            self.batch_size = tf.shape(self.word_emb_matrix)[0]
            self.dropout_rate = dropout_rate
            self.LSR = LSR_mix_rate


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
                # conv_bn = tf.contrib.layers.batch_norm(conv, is_training=self.is_training)
                # conv_bn_activated = tf.nn.relu(conv_bn)
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
                # self.feature = tf.layers.batch_normalization(self.feature, training=self.is_training)
                # self.feature =
                self.feature = tf.layers.dropout(self.feature, rate=self.dropout_rate,
                    training=self.is_training)

                # print('cnn_output:', self.feature.get_shape())
            # with tf.variable_scope("hidden"):
            #     self.hidden_layer = tf.layers.dense(inputs=self.feature, units=hidden_size,
            #         activation=tf.nn.relu)
            #     # self.hidden_layer = tf.layers.batch_normalization(self.hidden_layer, training=self.is_training)
            #     self.hidden_layer = tf.layers.dropout(self.hidden_layer , rate=self.dropout_rate,
            #         training=self.is_training)
            with tf.variable_scope("projection"):
                self.final_output_logits = tf.layers.dense(inputs=self.feature ,
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
                self.unbalance_loss = self.loss
                self.final_loss = tf.reduce_mean(self.loss)*(1-self.LSR) + 1/7*self.LSR
                # tf.reduce_mean(self.loss) + 0.001 * tf.add_n(self.l2_loss)
                self.train_op = self.optimizer.minimize(self.final_loss)

            with tf.variable_scope("predict"):
                # probability
                self.probs = tf.nn.softmax(self.final_output_logits)
                # predict
                self.predict = tf.argmax(self.final_output_logits, axis=1)
                # print(self.predict.get_shape())
                self.correct = tf.equal(tf.cast(self.predict, tf.int32),
                                        tf.cast(self.output, tf.int32))
                self.accuracy = tf.reduce_mean(tf.cast(self.correct, tf.float32))

    def assign_lr(self, session, lr_value):
        session.run(self.lr_update, feed_dict={self.new_lr: lr_value})



if __name__ == '__main__':
    informable_slots = DomainModel(name='test')







