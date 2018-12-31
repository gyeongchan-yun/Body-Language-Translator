from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.layers import Dense, Flatten, Input
from keras.models import Model
from keras.applications.vgg16 import VGG16
from keras import layers
from keras import models
import os
from utils.config import config


config = config['MODEL']

root_dir = config['image_dir']
train_dir = os.path.join(root_dir, 'train')

window_size = (3, 3)
pool_size = (2, 2)
num_class = len(os.listdir(train_dir))


def basicModel(input_shape):
    model = models.Sequential()
    model.add(layers.Conv2D(32, window_size,
                            activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization())  # add Batch Norm
    # model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(32, window_size, activation='relu'))  # 64
    model.add(layers.BatchNormalization())
    # model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Flatten())
    model.add(layers.Dropout(0.5))  # Dropout
    # model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(64, use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.Activation('relu'))
    model.add(layers.Dense(num_class, activation='softmax'))

    return model


def basicModel_original(input_shape):
    model = models.Sequential()
    model.add(layers.Conv2D(32, window_size,
                            activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization())  # add Batch Norm
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Dropout(0.25))  # Dropout
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Dropout(0.25))  # Dropout
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Dropout(0.25))  # Dropout
    model.add(layers.Flatten())
    # model.add(layers.Dropout(0.5)) # Dropout
    # model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(64, use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.Activation('relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_class, activation='softmax'))

    return model


def basicModel_best(input_shape):
    model = models.Sequential()
    model.add(layers.Conv2D(32, window_size,
                            activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization())  # add Batch Norm
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Flatten())
    model.add(layers.Dropout(0.5))  # Dropout
    # model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(64, use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.Activation('relu'))
    model.add(layers.Dense(num_class, activation='softmax'))

    return model


def BLSTM(input_shape):  # TODO upade
    model = models.Sequential()
    model.add(layers.Conv2D(32, window_size,
                            activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization())  # add Batch Norm
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Flatten())
    model.add(layers.Dropout(0.5))
    model.add(layers.Bidirectional(layers.LSTM(64), merge_mode='concat'))
    model.add(layers.Dense(64, use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.Activation('relu'))
    model.add(layers.Dense(num_class, activation='softmax'))

    return model


def basicModel_base(input_shape):
    model = models.Sequential()
    model.add(layers.Conv2D(32, window_size,
                            activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Conv2D(64, window_size, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size))
    model.add(layers.Flatten())
    model.add(layers.Dropout(0.5))  # Dropout
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(num_class, activation='softmax'))

    return model


def VGG(input_shape):
    base_model = VGG16(include_top=False, weights='imagenet')
    # base_model.summary()

    inputs = Input(shape=input_shape)

    output = base_model(inputs)
    net = Flatten(name='flatten')(output)
    net = Dense(64, activation='relu')(net)
    predictions = Dense(num_class, activation='softmax')(net)
    model = Model(inputs=inputs, outputs=predictions)

    for layer in base_model.layers:
        layer.trainable = False

    for layer in model.layers[:249]:
        layer.trainable = False
    for layer in model.layers[249:]:
        layer.trainable = True

    return model


def AlexNet(input_shape):
    # Instantiate an empty model
    model = Sequential()

    # 1st Convolutional Layer
    model.add(Conv2D(filters=96, input_shape=input_shape,
                     kernel_size=(11, 11), strides=(4, 4), padding='valid'))
    model.add(Activation('relu'))
    # Max Pooling
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

    # 2nd Convolutional Layer
    model.add(Conv2D(filters=256, kernel_size=(
        11, 11), strides=(1, 1), padding='valid'))
    model.add(Activation('relu'))
    # Max Pooling
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

    # 3rd Convolutional Layer
    model.add(Conv2D(filters=384, kernel_size=(
        3, 3), strides=(1, 1), padding='valid'))
    model.add(Activation('relu'))

    # 4th Convolutional Layer
    model.add(Conv2D(filters=384, kernel_size=(
        3, 3), strides=(1, 1), padding='valid'))
    model.add(Activation('relu'))

    # 5th Convolutional Layer
    model.add(Conv2D(filters=256, kernel_size=(
        3, 3), strides=(1, 1), padding='valid'))
    model.add(Activation('relu'))
    # Max Pooling
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

    # Passing it to a Fully Connected layer
    model.add(Flatten())
    # 1st Fully Connected Layer
    model.add(Dense(64, input_shape=input_shape))
    model.add(Activation('relu'))
    # Add Dropout to prevent overfitting
    model.add(Dropout(0.4))

    # 2nd Fully Connected Layer
    model.add(Dense(num_class))
    model.add(Activation('softmax'))
    # Add Dropout
    model.add(Dropout(0.4))

    return model
