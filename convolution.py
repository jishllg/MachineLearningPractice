from __future__ import division
import numpy as np
from PIL import Image
from scipy import misc
from skimage import data
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import tensorflow as tf

# Checking for saved image
try:
    img_arr = np.genfromtxt("img_array.csv", delimiter=",")

# Getting and saving image if none exists
except:
    response = requests.get('http://vignette2.wikia.nocookie.net/grayscale/images/4/47/Lion.png/revision/latest?cb=20130926182831')
    img_arr = np.array(Image.open(BytesIO(response.content)))[:, :, 0]
    np.savetxt("img_array.csv", img_arr, delimiter=",")

# Plot and show image
def show_img(image):
    plt.imshow(image, cmap = plt.get_cmap('gray'))
    plt.show()

# Squash pixels to range of 0 to 255
def squash_value(x):
    if x > 255:
        return 255
    if x < 0:
        return 0
    return x

# 2D kernel convolution
def conv_2d_kernel(kernel):
    padded_array = np.pad(img_arr, (1, 1), 'constant')
    output_array = np.zeros(img_arr.shape)
    for i in range(padded_array.shape[0] - kernel.shape[0] + 1):
        for j in range(padded_array.shape[1] - kernel.shape[1] + 1):
            temp_array = padded_array[i:i+kernel.shape[0], j:j+kernel.shape[1]]
            output_array[i, j] = squash_value(np.sum(temp_array * kernel))
    return output_array

# List of kernels
edge_detect = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
gaussian_blur = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) / 16
# show_img(conv_2d_kernel(edge_detect)) # Uncomment to show kernel transformation

# Reshaping arrays to work with TF functions
img_arr_4d = img_arr.reshape(-1, img_arr.shape[0], img_arr.shape[1], 1)
kernel_4d = gaussian_blur.reshape(3, 3, 1, 1)

# Computing convolution
tf_img = tf.Variable(np.array(img_arr_4d, dtype = np.float32))
tf_edge_kernel = tf.Variable(np.array(kernel_4d, dtype = np.float32))
transformed_img = tf.nn.conv2d(tf_img, tf_edge_kernel, strides = [1, 1, 1, 1], padding = "SAME")
transformed_img = transformed_img[0, :, :, 0]

# Testing if TF output is equal to test convolution
show_img(transformed_img)
np.testing.assert_array_almost_equal(conv_2d_kernel(gaussian_blur), transformed_img, decimal = 4)