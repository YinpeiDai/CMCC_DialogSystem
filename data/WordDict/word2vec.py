"""
训练词向量
"""
import tensorflow as tf
import numpy as np
import math,random,collections,pickle

class NCE_word2vec:
    def __init__(self, word2vec_traindata, word_dict_size, word_dict, synonym_words,
                 lr=1.0, num_sampled = 64, embedding_size = 25):
        self.word2vec_traindata = word2vec_traindata
        self.data_index = 0
        self.train_inputs = tf.placeholder(tf.int32, shape=[None])
        self.train_labels = tf.placeholder(tf.int32, shape=[None, 1])
        self.embeddings = tf.Variable(
            tf.random_uniform([word_dict_size, embedding_size], -1.0, 1.0))
        self.embed = tf.nn.embedding_lookup(self.embeddings, self.train_inputs)
        # 同义词影响
        self.synonym_words = synonym_words
        self.synonym_inputs = tf.placeholder(tf.int32, shape=[None, 2])
        self.embed0 = tf.nn.embedding_lookup(self.embeddings, self.synonym_inputs[:, 0])
        self.embed1 = tf.nn.embedding_lookup(self.embeddings, self.synonym_inputs[:, 1])
        self.synonym_loss = tf.sqrt(tf.reduce_mean(tf.square(self.embed0 - self.embed1)))

        # Construct the variables for the NCE loss
        self.nce_weights = tf.Variable(
            tf.truncated_normal([word_dict_size, embedding_size],
                                stddev=1.0 / math.sqrt(embedding_size)))
        self.nce_biases = tf.Variable(tf.zeros([word_dict_size]))

        # Compute the average NCE loss for the batch.
        # tf.nce_loss automatically draws a new sample of the negative labels each
        # time we evaluate the loss.

        self.loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=self.nce_weights,
                           biases=self.nce_biases,
                           labels=self.train_labels,
                           inputs=self.embed,
                           num_sampled=num_sampled,
                           num_classes=word_dict_size))
        self.final_loss = self.loss + 0.023 * self.synonym_loss
        # Construct the SGD optimizer using a learning rate of 1.0.
        self.optimizer = tf.train.GradientDescentOptimizer(lr).minimize(self.final_loss)

    def run_train(self, session, num_steps):
        session.run(tf.global_variables_initializer())
        average_loss = 0
        for i in range(1,num_steps+1):
            inputs, labels = self.generate_batch()
            # update parameters
            feed_dict = {self.train_inputs: inputs,
                         self.train_labels: labels,
                         self.synonym_inputs: self.synonym_words}
            loss, _ = session.run([self.loss, self.optimizer], feed_dict)
            average_loss += loss
            if i % 100 == 0:
                print("average_loss %0.4f at step %d:" %(average_loss/100,i))
                average_loss = 0
        return self.embeddings.eval(session)


    def generate_batch(self, batch_size=128, num_skips=2, skip_window=1):
        assert batch_size % num_skips == 0
        assert num_skips <= 2 * skip_window
        batch = np.ndarray(shape=(batch_size,), dtype=np.int32)
        labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
        span = 2 * skip_window + 1  # [ skip_window target skip_window ]
        buffer = collections.deque(maxlen=span)
        for _ in range(span):
            buffer.append(self.word2vec_traindata[self.data_index])
            self.data_index = (self.data_index + 1) % len(self.word2vec_traindata)
        for i in range(batch_size // num_skips):
            target = skip_window  # target label at the center of the buffer
            targets_to_avoid = [skip_window]
            for j in range(num_skips):
                while target in targets_to_avoid:
                    target = random.randint(0, span - 1)
                targets_to_avoid.append(target)
                batch[i * num_skips + j] = buffer[skip_window]
                labels[i * num_skips + j, 0] = buffer[target]
            buffer.append(self.word2vec_traindata[self.data_index])
            self.data_index = (self.data_index + 1) % len(self.word2vec_traindata)
        # Backtrack a little bit to avoid skipping words in the end of a batch
        self.data_index = (self.data_index + len(self.word2vec_traindata) - span) % len(self.word2vec_traindata)
        return batch, labels



if __name__ == '__main__':
    nce_word2vec = NCE_word2vec([2, 1, 3, 4, 5, 1, 6, 7, 8, 9, 10, 11, 12, 1, 13, 14, 15],
                                16,
                                {"UNK": 0, "是": 1, "李小福": 2, "创新办": 3, "主任": 4, "也": 5, "云": 6, "计算": 7, "方面": 8,
                                 "的": 9, "专家": 10, "；": 11, "什么": 12, "八一": 13, "双鹿": 14, "\n": 15},
                                num_sampled=2)
    with tf.Session() as sess:
        print(nce_word2vec.run_train(sess, 500))
