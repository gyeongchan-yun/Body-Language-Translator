import os

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


aug_num = 1

datagen = ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest')

output_dir = '/crop_output/train/'
train_dir = os.environ['OPEN_POSE_HOME'] + output_dir
# train_dir = './test_aug/'
labels_dir = sorted([os.path.join(train_dir, label) for label in os.listdir(train_dir)])

print ('labels_dir: ', labels_dir)

for label_dir in labels_dir:
    for fname in os.listdir(label_dir):
        image_path = label_dir + '/' + fname

        if fname.find('aug_') == -1:
            img = load_img(image_path)
            img = img_to_array(img)
            img = img.reshape((1,) + img.shape)

            i = 0
            for batch in datagen.flow(img, batch_size =1, save_to_dir=label_dir, save_prefix='aug', save_format='png'):
                i += 1
                if i >= aug_num:
                    break
            os.rename(image_path, label_dir + '/aug_' + fname)

        


