import os
import sys
import shutil

from flask import Flask, abort, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from collections import OrderedDict

import utils.video_segment as video_segment
from utils.config import config
from utils.logger import infolog, errorlog

config = config['WEB']

UPLOAD_FOLDER = config['upload']
UPLOAD_DONE_FOLDER = config['done']
TEST_IMAGE_FOLDER = config['test_image_dir']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'avi', 'mp4'])
LABELS = config['labels']
HOST = config['host']
PORT = int(config['port'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def simple_NLP(text):
    if text.find('why') > -1:
        text += '?'
    # TODO: add more expressions

    return text


def refine_content(content):
    '''
    :param content: ex) ['you']
    :return: you

    :param content: ex) ['why', 'you', 'good']
    :return: why you good?
    '''
    text = content
    replace_dict = {'[': '', ']': '', '\'': '', ',': ' '}
    for k, v in replace_dict.items():
        text = text.replace(k, v)
    # remove repeated word
    text_list = text.split()
    text = ' '.join(list(OrderedDict.fromkeys(text_list)))

    return text


def check_video(content):
    isVideo = False
    if content.find(',') > -1:
        isVideo = True

    return isVideo


def move_correct_test_image():
    infolog(__file__, "MOVE test image to correct label directory")
    if len(os.listdir(TEST_IMAGE_FOLDER)) == 1:  # check 1 file exists
        for fname in os.listdir(TEST_IMAGE_FOLDER):
            file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
            try:
                f = open("meaning_temp.txt", "r")
            except Exception as e:
                errorlog(__file__, e)
            else:
                prediction = f.read()
                label = refine_content(prediction)
                train_dir = os.path.join(LABELS, label.strip())
                shutil.move(file_path, train_dir)
                os.remove("meaning_temp.txt")
            finally:
                f.close()


def move_test_image(dst_path):
    """ Move test image to train directory on feedback label.

    Args:
        dst_path: path of train directory on feedback label.
    """
    infolog(__file__, "MOVE test image to feedback label directory")
    if len(os.listdir(TEST_IMAGE_FOLDER)) == 1:  # check 1 file exists
        for fname in os.listdir(TEST_IMAGE_FOLDER):
            file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
            shutil.move(file_path, dst_path)


def remove_test_image():
    infolog(__file__, "REMOVE existing test image")
    for fname in os.listdir(TEST_IMAGE_FOLDER):
        file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
        os.remove(file_path)


@app.route('/')
def render_file():
    return render_template('/main.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        infolog(__file__, "UPLOAD FILE SUCCESS")
        remove_test_image()  # Initial step: remove previous test image

        f = request.files['file']
        if f and allowed_file(f.filename):
            filename_list = []
            filename = secure_filename(f.filename)

            parsed_name = filename.split(".")
            file_type = parsed_name[len(parsed_name)-1]
            if file_type == 'avi' or file_type == 'mp4':  # video file
                infolog(__file__, "START VIDEO SEGMENTATION")
                # call video_segment function
                comparison_image_path = config['comparison']
                video_path = os.path.join(config['video'], filename)
                f.save(video_path)
                input_image_path = os.path.join(config['image_dir'], 'train')
                count = video_segment.image_selector(
                    input_image_path, comparison_image_path)
                filename_list = video_segment.image_reader(
                    video_path, UPLOAD_FOLDER, comparison_image_path)

            else:
                infolog(__file__, "STORE UPLOAD IMAGE")
                # store images uploaded by user
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # call open pose and running model by forking background process
            os.system('sh %s &' % config['background'])

            return redirect(url_for('uploaded_file',
                                    filename=filename))


@app.route('/feedback/new', methods=['GET', 'POST'])
def move_to_new_feedback_label():
    if request.method == 'POST':
        new_meaning = request.form['meaning']

        new_label_dir = os.path.join(LABELS, new_meaning)
        if not os.path.isdir(new_label_dir):
            os.makedirs(new_label_dir)

        move_test_image(new_label_dir)
        return redirect(url_for('render_file'))


@app.route('/feedback/<label>')
def move_to_feedback_label(label):
    feedback_label_dir = os.path.join(LABELS, label)
    move_test_image(feedback_label_dir)
    return redirect(url_for('render_file'))


@app.route('/meaning')
def send_prediction():
    infolog(__file__, "REQUEST PREDICTION")

    while True:
        if os.path.isfile("meaning.txt"):
            with open("meaning.txt", "r") as f:
                content = f.read()
            if content:
                infolog(__file__, "RECEIVE PREDICTION FILE SUCCESS")
                break

    # copy predicted label in the case of corrcet feedback
    shutil.copyfile("meaning.txt", "meaning_temp.txt")

    os.remove("meaning.txt")

    text = refine_content(content)
    text = simple_NLP(text)

    if check_video(content):
        remove_test_image()
        os.remove("meaning_temp.txt")  # no feedback

    infolog(__file__, "RESPONSE PREDICTION: {}".format(text))
    return text


@app.route('/feedback/correct')
def move_to_correct_feedback_label():
    if os.path.exists("meaning_temp.txt"):
        move_correct_test_image()
    return redirect(url_for('render_file'))


@app.route('/feedback/labels')
def send_label_list():
    label_list = os.listdir(LABELS)
    return '/'.join(label_list)


@app.route('/show/<filename>')
def uploaded_file(filename):
    return render_template('/loading.html', filename=filename)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
