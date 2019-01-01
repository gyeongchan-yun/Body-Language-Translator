import os
import sys
import shutil
from flask import Flask, abort, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
import utils.video_segment as video_segment
from collections import OrderedDict
from utils.config import config


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
    if len(os.listdir(TEST_IMAGE_FOLDER)) == 1:  # check 1 file exists
        for fname in os.listdir(TEST_IMAGE_FOLDER):
            file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
            f = open("meaning_temp.txt", "r")
            prediction = f.read()
            label = refine_content(prediction)
            train_dir = os.path.join(LABELS, label.strip())
            shutil.move(file_path, train_dir)

            os.remove("meaning_temp.txt")


'''
    Function moves test image to train directory of feedback label.
'''
def move_test_image(dst_path):
    if len(os.listdir(TEST_IMAGE_FOLDER)) == 1:  # check 1 file exists
        for fname in os.listdir(TEST_IMAGE_FOLDER):
            file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
            shutil.move(file_path, dst_path)


def remove_test_image():
    for fname in os.listdir(TEST_IMAGE_FOLDER):
        file_path = os.path.join(TEST_IMAGE_FOLDER, fname)
        os.remove(file_path)


@app.route('/')
def render_file():
    return render_template('/main.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        remove_test_image()  # Initial step: remove previous test image

        f = request.files['file']
        if f and allowed_file(f.filename):
            filename_list = []
            filename = secure_filename(f.filename)

            parsed_name = filename.split(".")
            file_type = parsed_name[len(parsed_name)-1]
            if file_type == 'avi' or file_type == 'mp4':  # video file
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
                # store images uploaded by user
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # call open pose and running model by forking background process
            os.system('sh %s &' % config['background'])

            return redirect(url_for('uploaded_file',
                                    filename=filename))


@app.route('/new_meaning', methods=['GET', 'POST'])  # TODO: rename route with /feedback/new
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
    if not os.path.isfile("meaning.txt"):
        abort(404)
    f = open("meaning.txt", "r")
    content = f.read()
    if not content:
        abort(404)
    else:
        # copy predicted label in the case of corrcet feedback
        shutil.copyfile("meaning.txt", "meaning_temp.txt")
    f.close()

    os.remove("meaning.txt")

    text = refine_content(content)
    text = simple_NLP(text)

    if check_video(content):
        remove_test_image()
        os.remove("meaning_temp.txt")  # no feedback
    # TODO: change it as log
    print("\n================text: {} ==================\n".format(text))
    return text


@app.route('/yes')  # TODO: rename route to /feedback/correct
def move_to_correct_feedback_label():
    if os.path.exists("meaning_temp.txt"):
        move_correct_test_image()
    return redirect(url_for('render_file'))


@app.route('/list')
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
