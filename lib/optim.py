from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


""" Super Class """
class Optimizer(object):
    """
    This is a template for implementing the classes of optimizers
    """
    def __init__(self, net, lr=1e-4):
        self.net = net  # the model
        self.lr = lr    # learning rate

    """ Make a step and update all parameters """
    def step(self):
        #### FOR RNN / LSTM ####
        if hasattr(self.net, "preprocess") and self.net.preprocess is not None:
            self.update(self.net.preprocess)
        if hasattr(self.net, "rnn") and self.net.rnn is not None:
            self.update(self.net.rnn)
        if hasattr(self.net, "postprocess") and self.net.postprocess is not None:
            self.update(self.net.postprocess)
        
        #### MLP ####
        if not hasattr(self.net, "preprocess") and \
           not hasattr(self.net, "rnn") and \
           not hasattr(self.net, "postprocess"):
            for layer in self.net.layers:
                self.update(layer)


""" Classes """
class SGD(Optimizer):
    """ Some comments """
    def __init__(self, net, lr=1e-4, weight_decay=0.0):
        self.net = net
        self.lr = lr
        self.weight_decay = weight_decay

    def update(self, layer):
        for n, dv in layer.grads.items():
            #############################################################################
            # TODO: Implement the SGD with (optional) Weight Decay                      #
            #############################################################################
            layer.params[n] = layer.params[n] - (self.lr * dv ) - (self.weight_decay * layer.params[n])
            #############################################################################
            #                             END OF YOUR CODE                              #
            #############################################################################



class Adam(Optimizer):
    """ Some comments """
    def __init__(self, net, lr=1e-3, beta1=0.9, beta2=0.999, t=0, eps=1e-8, weight_decay=0.0):
        self.net = net
        self.lr = lr
        self.beta1, self.beta2 = beta1, beta2
        self.eps = eps
        self.mt = {}
        self.vt = {}
        self.t = t
        self.weight_decay=weight_decay

    def update(self, layer):
        #############################################################################
        # TODO: Implement the Adam with [optinal] Weight Decay                      #
        #############################################################################
        pass
        self.t +=1
        mt_correct ={}
        vt_correct = {}
        for n, dv in layer.grads.items():
            if n not in self.mt:
                self.mt[n] = (1 - self.beta1) * dv
            else:
                self.mt[n] = self.beta1 * self.mt[n] + (1 - self.beta1) * dv

            if n not in self.vt:
                self.vt[n] = (1 - self.beta2)*(dv**2)
            else:
                self.vt[n] = self.beta2 * self.vt[n] + (1 - self.beta2)*(dv**2)

            if self.weight_decay > 0:
                layer.params[n] = layer.params[n] -  self.weight_decay * layer.params[n]

            mt_correct[n] = self.mt[n]/(1 - self.beta1**self.t)
            vt_correct[n] = self.vt[n]/(1 - self.beta2**self.t)
            layer.params[n] = layer.params[n] - ((self.lr * mt_correct[n])/(np.sqrt(vt_correct[n])+self.eps))
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
