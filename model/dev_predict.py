import sys, os
from datetime import datetime
import matplotlib.pyplot as plt

from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model

import numpy as np

import cv2
''' [code reference]
    bar chart with value - https://stackoverflow.com/questions/6282058/writing-numerical-values-on-the-plot-with-matplotlib
'''

import configparser 

abs_path = os.environ['PROJECT']

config = configparser.ConfigParser()
config.read(abs_path + '/config/config.conf')

config = config['MODEL']


root_path = config['project_root']
MODEL = config['model_path']

now = datetime.now()
date = '%s-%s-%s-%s-%s' % (now.year, now.month, now.day, now.hour, now.minute)

image_size = eval(config['image_size']) # (200, 200)

# Parameters
BATCH_SIZE = int(config['batch_size'])
LEARNING_RATE = float(config['learning_rate'])

# image Directory
root_dir = config['image_dir']
train_dir = os.path.join(root_dir, 'train')

test_dir = config['predict_dir']
# test_dir = os.path.join(root_dir, 'dev_test')


def visualize_prediction(filenames, labels, pred, predictions):
    data_x = np.array(list(labels.values()))
    data_y = np.array(pred[0])
    
    plt.bar(data_x, data_y, color='b')
    for a,b in zip(data_x, data_y):
        plt.text(a, b, str(b))

    plt.title('distribution of prediction on '+ filenames[0])
    plt.savefig(root_path + 'model/chart/predict/predicts_{}.png'.format(predictions[0])) 
    plt.show()


def main():
    train_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=image_size, 
            batch_size = BATCH_SIZE,
            class_mode='categorical')

    test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=image_size,
            batch_size=1,
            class_mode=None)
    
    loaded_model = load_model(MODEL)
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics = ['accuracy'])

    test_generator.reset()
    pred = loaded_model.predict_generator(test_generator)
    print("prediction: \n", pred * 100)
    
    predicted_class_indices=np.argmax(pred,axis=1)
    labels = (train_generator.class_indices)
    labels = dict((v,k) for k,v in labels.items())
    print(labels)
    predictions = [labels[k] for k in predicted_class_indices]
    filenames = test_generator.filenames
    filenames.reverse()
    print("filenames: ", filenames)
    print("predictons: \n", predictions)

    if len(sys.argv) == 2:
        if sys.argv[1] == '-v':
            visualize_prediction(filenames, labels, pred, predictions)
        else:
            print ("USAGE: dev_predict.py -v")
            exit()


if __name__ == "__main__":
    main()
