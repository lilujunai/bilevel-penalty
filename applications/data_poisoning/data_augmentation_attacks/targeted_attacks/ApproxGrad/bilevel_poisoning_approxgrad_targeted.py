import sys
sys.path.append("../../../../../optimizers/approxgrad")
import tensorflow as tf
import numpy as np
from bilevel_approxgrad import bilevel_approxgrad
from cleverhans.utils_keras import KerasModelWrapper

class bilevel_poisoning(object):

    def __init__(self, sess, x_train_tf, x_val_tf, x_test_tf, x_poison_tf, x_original_tf, y_train_tf, y_val_tf, y_test_tf, y_poison_tf,
                 Npoison, height, width, nch,
                 var_cls, sig):
    
        self.sess = sess
        self.x_train_tf = x_train_tf
        self.x_val_tf = x_val_tf
        self.x_test_tf = x_test_tf
        self.x_poison_tf = x_poison_tf
        self.x_original_tf = x_original_tf
        
        self.y_train_tf = y_train_tf
        self.y_val_tf = y_val_tf
        self.y_test_tf = y_test_tf
        self.y_poison_tf = y_poison_tf
        
        self.cls_train = tf.matmul(self.x_train_tf, var_cls)
        self.cls_val = tf.matmul(self.x_val_tf, var_cls)
        self.cls_test = tf.nn.softmax(tf.matmul(self.x_test_tf, var_cls))
        
        self.Npoison = Npoison
        self.height = height
        self.width = width
        self.nch = nch
        
        self.u = tf.get_variable('u', shape=(Npoison, self.height*self.width*self.nch), constraint=lambda t: tf.clip_by_value(t,0,1))
        self.assign_u = tf.assign(self.u, self.x_poison_tf)
        
        self.cls_poison = tf.matmul(self.u, var_cls)
        
        self.v = var_cls
        
        self.f = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.cls_val, labels=self.y_val_tf))
        )
        self.weight_decay = tf.nn.l2_loss(var_cls)
        
        self.g = 0.5 * 0.01 * self.weight_decay + tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=tf.concat([self.cls_poison, self.cls_train], 0), labels=tf.concat([self.y_poison_tf, self.y_train_tf], 0)))

        self.bl = bilevel_approxgrad(sess, self.f, self.g, self.u, [self.v], sig)
        
        self.loss_simple = 0.5 * 0.01 * self.weight_decay + tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.cls_train, labels=self.y_train_tf))
        self.optim_simple = tf.train.AdamOptimizer(1E-3).minimize(self.loss_simple, var_list=self.v)
        
    def train(self, x_train, y_train, x_val, y_val, x_poisoned, y_poisoned, x_original, lr_u, lr_v, lr_p, niter1 = 1, niter2 = 1):
        
        self.sess.run(self.assign_u,feed_dict={self.x_poison_tf:x_poisoned})
        feed_dict={self.x_train_tf:x_train, self.y_train_tf:y_train, self.x_val_tf:x_val, self.y_val_tf:y_val, self.y_poison_tf:y_poisoned, self.x_original_tf:x_original}
        
        fval, gval, hval = self.bl.update(feed_dict, lr_u, lr_v, lr_p, niter1, niter2)
        new_x_poisoned = self.sess.run(self.u)
        
        return [fval, gval, hval, new_x_poisoned]
        
    def train_simple(self, x_train, y_train, x_test, y_test, nepochs):
        for epoch in range(nepochs):
            self.sess.run(self.optim_simple,feed_dict={self.x_train_tf:x_train,self.y_train_tf:y_train})
        
        print("Accuracy simple")
        print("Train Accuracy:", self.eval_accuracy(x_train, y_train))
        print("Test Accuracy:", self.eval_accuracy(x_test, y_test), "\n")
        
    def eval_accuracy(self, x_test, y_test):
        acc = 0
        pred = self.sess.run(self.cls_test, {self.x_test_tf:x_test})
        acc += np.sum(np.argmax(pred,1)==np.argmax(y_test,1))
        acc /= np.float32(len(x_test))
        return acc