from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


class sequential(object):
    def __init__(self, *args):
        """
        Sequential Object to serialize the NN layers
        Please read this code block and understand how it works
        """
        self.params = {}
        self.grads = {}
        self.layers = []
        self.paramName2Indices = {}
        self.layer_names = {}

        # process the parameters layer by layer
        for layer_cnt, layer in enumerate(args):
            for n, v in layer.params.items():
                self.params[n] = v
                self.paramName2Indices[n] = layer_cnt
            for n, v in layer.grads.items():
                self.grads[n] = v
            if layer.name in self.layer_names:
                raise ValueError("Existing name {}!".format(layer.name))
            self.layer_names[layer.name] = True
            self.layers.append(layer)

    def assign(self, name, val):
        # load the given values to the layer by name
        layer_cnt = self.paramName2Indices[name]
        self.layers[layer_cnt].params[name] = val

    def assign_grads(self, name, val):
        # load the given values to the layer by name
        layer_cnt = self.paramName2Indices[name]
        self.layers[layer_cnt].grads[name] = val

    def get_params(self, name):
        # return the parameters by name
        return self.params[name]

    def get_grads(self, name):
        # return the gradients by name
        return self.grads[name]

    def gather_params(self):
        """
        Collect the parameters of every submodules
        """
        for layer in self.layers:
            for n, v in layer.params.items():
                self.params[n] = v

    def gather_grads(self):
        """
        Collect the gradients of every submodules
        """
        for layer in self.layers:
            for n, v in layer.grads.items():
                self.grads[n] = v

    def apply_l1_regularization(self, lam):
        """
        Gather gradients for L1 regularization to every submodule
        """
        for layer in self.layers:
            for n, v in layer.grads.items():
                param = self.params[n]
                grad = (param > 0).astype(np.float32) - (param < 0).astype(np.float32)
                self.grads[n] += lam * grad

    def apply_l2_regularization(self, lam):
        """
        Gather gradients for L2 regularization to every submodule
        """
        for layer in self.layers:
            for n, v in layer.grads.items():
                self.grads[n] += lam * self.params[n]


    def load(self, pretrained):
        """
        Load a pretrained model by names
        """
        for layer in self.layers:
            if not hasattr(layer, "params"):
                continue
            for n, v in layer.params.items():
                if n in pretrained.keys():
                    layer.params[n] = pretrained[n].copy()
                    print ("Loading Params: {} Shape: {}".format(n, layer.params[n].shape))

class ConvLayer2D(object):
    def __init__(self, input_channels, kernel_size, number_filters, 
                stride=1, padding=0, init_scale=.02, name="conv"):
        
        self.name = name
        self.w_name = name + "_w"
        self.b_name = name + "_b"

        self.input_channels = input_channels
        self.kernel_size = kernel_size
        self.number_filters = number_filters
        self.stride = stride
        self.padding = padding

        self.params = {}
        self.grads = {}
        self.params[self.w_name] = init_scale * np.random.randn(kernel_size, kernel_size, 
                                                                input_channels, number_filters)
        self.params[self.b_name] = np.zeros(number_filters)
        self.grads[self.w_name] = None
        self.grads[self.b_name] = None
        self.meta = None
    
    def get_output_size(self, input_size):
        '''
        :param input_size - 4-D shape of input image tensor (batch_size, in_height, in_width, in_channels)
        :output a 4-D shape of the output after passing through this layer (batch_size, out_height, out_width, out_channels)
        '''
        output_shape = [None, None, None, None]
        #############################################################################
        # TODO: Implement the calculation to find the output size given the         #
        # parameters of this convolutional layer.                                   #
        #############################################################################
        pass
        output_shape = [input_size[0], (input_size[1] - self.kernel_size + 2*self.padding)//self.stride + 1, (input_size[1] - self.kernel_size + 2*self.padding)//self.stride + 1, self.number_filters]
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        return output_shape

    def forward(self, img):
        output = None
        assert len(img.shape) == 4, "expected batch of images, but received shape {}".format(img.shape)

        output_shape = self.get_output_size(img.shape)
        _ , input_height, input_width, _ = img.shape
        _, output_height, output_width, _ = output_shape

        #############################################################################
        # TODO: Implement the forward pass of a single convolutional layer.       #
        # Store the results in the variable "output" provided above.                #
        #############################################################################
        pass
        padded_img = np.pad(img,((0, 0), (self.padding, self.padding), (self.padding, self.padding), (0, 0)), 'constant', constant_values = 0)
        output = np.zeros(output_shape)
        for h in range(output_height):
            for w in range(output_width): 
                weight = self.params[self.w_name] 
                b = self.params[self.b_name] 
                s_h = h * self.stride
                s_w = w * self.stride
                img_p = padded_img[:, s_h : s_h + self.kernel_size, s_w : s_w + self.kernel_size, :].reshape(padded_img.shape[0], self.kernel_size, self.kernel_size, padded_img.shape[-1], 1)
                mul = np.sum(np.multiply(img_p, weight), axis=(1,2,3))
                output[:, h, w, :] = mul + b
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        self.meta = img
        
        return output


    def backward(self, dprev):
        img = self.meta
        if img is None:
            raise ValueError("No forward function called before for this module!")

        dimg, self.grads[self.w_name], self.grads[self.b_name] = None, None, None
        
        #############################################################################
        # TODO: Implement the backward pass of a single convolutional layer.        #
        # Store the computed gradients wrt weights and biases in self.grads with    #
        # corresponding name.                                                       #
        # Store the output gradients in the variable dimg provided above.           #
        #############################################################################
        pass

        output_shape = self.get_output_size(img.shape)
        _, output_height, output_width, _ = output_shape

        self.grads[self.w_name] = np.zeros(self.params[self.w_name].shape)
        self.grads[self.b_name] = np.zeros(self.params[self.b_name].shape)

        padded_img = np.pad(img,((0, 0), (self.padding, self.padding), (self.padding, self.padding), (0, 0)), 'constant', constant_values = 0)
        dimg = np.zeros(img.shape)
        d_pad = np.zeros(padded_img.shape)

        for h in range(output_height):
            for w in range(output_width):

                s_h = h * self.stride
                s_w = w * self.stride

                img_p = padded_img[:, s_h :s_h + self.kernel_size, s_w : s_w + self.kernel_size, :].reshape(padded_img.shape[0], self.kernel_size, self.kernel_size, padded_img.shape[-1], 1)

                dprev_reshaped = dprev[:, h, w, :].reshape(padded_img.shape[0], 1, 1, 1, self.number_filters)
                d_pad[:, s_h : s_h + self.kernel_size, s_w : s_w + self.kernel_size, :] += np.sum(self.params[self.w_name] * dprev_reshaped, axis = 4) 
                self.grads[self.w_name] += np.sum(img_p * dprev_reshaped, axis = 0)
                self.grads[self.b_name] += np.sum(dprev_reshaped, axis = (0,1,2,3))

        if self.padding > 0:
            dimg = d_pad[:, self.padding:-self.padding, self.padding:-self.padding, :]
        else:
            dimg = d_pad
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

        self.meta = None
        return dimg


class MaxPoolingLayer(object):
    def __init__(self, pool_size, stride, name):
        self.name = name
        self.pool_size = pool_size
        self.stride = stride
        self.params = {}
        self.grads = {}
        self.meta = None

    def forward(self, img):
        output = None
        assert len(img.shape) == 4, "expected batch of images, but received shape {}".format(img.shape)
        
        #############################################################################
        # TODO: Implement the forward pass of a single maxpooling layer.            #
        # Store your results in the variable "output" provided above.               #
        #############################################################################
        pass
        batch_size, h_in, w_in, channel = img.shape
        h_out = (h_in - self.pool_size) // self.stride + 1
        w_out = (w_in - self.pool_size) // self.stride + 1
        output = np.zeros((batch_size, h_out, w_out, channel))
        for h in range(h_out):
            for w in range(w_out):
                h_s = h * self.stride
                w_s = w * self.stride
                img_p = img[:, h_s : h_s + self.pool_size, w_s : w_s + self.pool_size, :]
                output[:, h, w, :] = np.max(img_p,  axis = (1, 2))
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        self.meta = img

        return output

    def backward(self, dprev):
        img = self.meta

        dimg = np.zeros_like(img)
        _, h_out, w_out, _ = dprev.shape
        h_pool, w_pool = self.pool_size,self.pool_size

        #############################################################################
        # TODO: Implement the backward pass of a single maxpool layer.              #
        # Store the computed gradients in self.grads with corresponding name.       #
        # Store the output gradients in the variable dimg provided above.           #
        #############################################################################
        pass
        batch_size , h_out, w_out, channel = dprev.shape
        for h in range(h_out):
            for w in range(w_out):
                h_s = h * self.stride
                w_s = w * self.stride
                img_p = img[:, h_s : h_s + self.pool_size, w_s : w_s + self.pool_size, :] 
                mask = img_p == np.max(img_p, axis = (1, 2)).reshape((batch_size, 1, 1, channel))
                dimg[:, h_s : h_s + self.pool_size, w_s : w_s + self.pool_size, :] += mask * dprev[:, h, w, :].reshape(batch_size, 1, 1, channel)
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        return dimg
