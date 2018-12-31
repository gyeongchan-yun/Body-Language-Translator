import sys, os
from datetime import datetime
import matplotlib.pyplot as plt
from CNN_model import BLSTM, basicModel_best, VGG, AlexNet # Add other model methods here
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping

import matplotlib.pyplot as plt

import configparser


dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(dir_path + '/../config/config.conf')

config = config['MODEL']

MODEL = config['model_path']
ROOT = config['project_root']

CALLBACKS = [
        EarlyStopping(monitor='val_acc', patience=10, mode='max', verbose=1),
        ModelCheckpoint(MODEL, monitor='val_acc', save_best_only=True, mode='max', verbose=1) # verbose shows callback procedure
]

now = datetime.now()
date = '%s_%s_%s_%s' % (now.year, now.month, now.day, now.hour)

# Parameters
LEARNING_RATE = float(config['learning_rate'])
BATCH_SIZE = int(config['batch_size']) # 20
EPOCHS = int(config['epochs']) # 30 -> set small number first to save time

# image Directory
# root_dir = os.environ['OPEN_POSE_HOME'] + '/output/'
# root_dir = os.environ['OPEN_POSE_HOME'] + '/exp_output/'
# root_dir = os.environ['OPEN_POSE_HOME'] + '/test_output/'
# root_dir = os.environ['OPEN_POSE_HOME'] + '/minimal_label_output/'
# root_dir = os.environ['OPEN_POSE_HOME'] + '/crop_output/'
root_dir = config['image_dir']
train_dir = os.path.join(root_dir, 'train')
validation_dir = os.path.join(root_dir, 'validation')
test_dir = os.path.join(root_dir, 'test')

image_size = eval(config['image_size'])  # (200, 200) #(150, 150)
# image_size = (244,244) -> Alexnet must have image size of (244, 244)


def visualize_accuracy(fitting):
    acc = fitting.history['acc']
    val_acc = fitting.history['val_acc']
    loss = fitting.history['loss']
    val_loss = fitting.history['val_loss']

    epochs = range(len(acc))

    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()

    plt.figure()

    plt.plot(epochs, loss, 'bo', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()

    plt.show()


def main():
    train_datagen = ImageDataGenerator(rescale=1./255)
    validation_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=image_size,
            batch_size = BATCH_SIZE,
            class_mode='categorical')

    validation_generator = validation_datagen.flow_from_directory(
            validation_dir,
            target_size=image_size,
            batch_size = BATCH_SIZE,
            class_mode='categorical')

    input_shape = image_size + (3,) # (width, height, depth)

    # model = BLSTM(input_shape)
    model = basicModel_best(input_shape)
    # model = VGG(input_shape)
    model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adam(LEARNING_RATE), metrics = ['accuracy'])

    STEP_SIZE_TRAIN=train_generator.n//train_generator.batch_size
    STEP_SIZE_VALIDATION=validation_generator.n//validation_generator.batch_size

    fitting = model.fit_generator(
                train_generator,
                steps_per_epoch=STEP_SIZE_TRAIN, #10, # batch size x steps_per_epoch = the number of train data
                epochs=EPOCHS,
                validation_data=validation_generator,
                validation_steps=STEP_SIZE_VALIDATION, #10  batch size x validation_stpes = the number of validation data
                callbacks=CALLBACKS)

    bak_model = date + '_model.h5'
    model.save(ROOT + 'model/saved_model/bak/' + bak_model)

    if len(sys.argv) == 2:
        if sys.argv[1] == '-v':
            visualize_accuracy(fitting)
        else:
            print ("USAGE: train.py -v")
            exit()


if __name__ == "__main__":
    main()
