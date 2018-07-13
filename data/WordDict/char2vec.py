"""
训练字符向量
"""
import tensorflow as tf
import numpy as np
import math,random,collections,pickle

class NCE_char2vec:
    def __init__(self, char2vec_traindata, char_dict_size,
                 lr=1.0, num_sampled = 64, embedding_size = 25):
        self.char2vec_traindata = char2vec_traindata
        self.data_index = 0
        self.train_inputs = tf.placeholder(tf.int32, shape=[None])
        self.train_labels = tf.placeholder(tf.int32, shape=[None, 1])
        self.embeddings = tf.Variable(
            tf.random_uniform([char_dict_size, embedding_size], -.3, .3))
        self.embed = tf.nn.embedding_lookup(self.embeddings, self.train_inputs)

        # Construct the variables for the NCE loss
        self.nce_weights = tf.Variable(
            tf.truncated_normal([char_dict_size, embedding_size],
                                stddev=1.0 / math.sqrt(embedding_size)))
        self.nce_biases = tf.Variable(tf.zeros([char_dict_size]))

        # Compute the average NCE loss for the batch.
        # tf.nce_loss automatically draws a new sample of the negative labels each
        # time we evaluate the loss.

        self.loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=self.nce_weights,
                           biases=self.nce_biases,
                           labels=self.train_labels,
                           inputs=self.embed,
                           num_sampled=num_sampled,
                           num_classes=char_dict_size))
        # Construct the SGD optimizer using a learning rate of 1.0.
        self.optimizer = tf.train.GradientDescentOptimizer(lr).minimize(self.loss)

    def run_train(self, session, num_steps):
        session.run(tf.global_variables_initializer())
        average_loss = 0
        for i in range(1,num_steps+1):
            inputs, labels = self.generate_batch()
            # update parameters
            feed_dict = {self.train_inputs: inputs,
                         self.train_labels: labels}
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
            buffer.append(self.char2vec_traindata[self.data_index])
            self.data_index = (self.data_index + 1) % len(self.char2vec_traindata)
        for i in range(batch_size // num_skips):
            target = skip_window  # target label at the center of the buffer
            targets_to_avoid = [skip_window]
            for j in range(num_skips):
                while target in targets_to_avoid:
                    target = random.randint(0, span - 1)
                targets_to_avoid.append(target)
                batch[i * num_skips + j] = buffer[skip_window]
                labels[i * num_skips + j, 0] = buffer[target]
            buffer.append(self.char2vec_traindata[self.data_index])
            self.data_index = (self.data_index + 1) % len(self.char2vec_traindata)
        # Backtrack a little bit to avoid skipping words in the end of a batch
        self.data_index = (self.data_index + len(self.char2vec_traindata) - span) % len(self.char2vec_traindata)
        return batch, labels

if __name__ == '__main__':
    nce_char2vec = NCE_char2vec([2, 3, 4, 1, 5, 6, 7, 8, 9, 10, 1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 1, 22, 23, 24, 25, 26],
                                27,
                                num_sampled=10)
    with tf.Session() as sess:
        print(nce_char2vec.run_train(sess, 500))