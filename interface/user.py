import os, sys, shutil
from flask import Flask, abort, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
import configparser
import VideoSegment as video_segment
from collections import OrderedDict


config = configparser.ConfigParser()
config.read('../config/config.conf') # {user_path}/project/config/config.conf TODO: change absoulte path
config = config['WEB']

UPLOAD_FOLDER = config['upload']
UPLOAD_DONE_FOLDER = config['done']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'avi', 'mp4'])
LABELS = config['labels'] # have to change to real label list folder
HOST = config['host']
PORT = int(config['port'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

'''
    :param content: ex) ['you']
    :return: you
    
    :param content: ex) ['why', 'you', 'good']
    :return: why you good?
'''
def refine_content(content):
    text = content.replace('[', '').replace(']','').replace('\'','').replace('\'','').replace(',', ' ')
    # remove repeated word
    text_list = text.split()
    text = ' '.join(list(OrderedDict.fromkeys(text_list)))

    if text.find('why') > -1:
        text += '?'

    return text


def check_video(content):
    isVideo = False
    if content.find(',') > -1:
        isVideo = True

    return isVideo

    
'''
    Assume user already submitted image once.
    Then, it's called when user click 'home' and 'yes' button.
    We consider this UX means user was conscious of correctness.

    Function moves predicted image to predicted label train directory.
''' 
def move_correct_prediction():
    predicted_files = os.path.join(config['predict_dir'], 'predict') # TODO: add config
    if len(os.listdir(predicted_files)) == 1: # exists  1 file TODO: move several files
        for fname in os.listdir(predicted_files):
            file_path = os.path.join(predicted_files, fname)
            f = open("meaning_temp.txt", "r")
            prediction = f.read()
            label = refine_content(prediction)
            train_dir = os.path.join(LABELS, label.strip())
            shutil.move(file_path, train_dir)

            os.remove("meaning_temp.txt")         

'''
    Function moves predicted image to feedback label train directory.
'''
def move_prediction(dst_path):
    predicted_files = os.path.join(config['predict_dir'], 'predict')
    if len(os.listdir(predicted_files)) == 1: # exists  1 file TODO: move several files
        for fname in os.listdir(predicted_files):
            file_path = os.path.join(predicted_files, fname)
            shutil.move(file_path, dst_path)


def remove_prediction():
    predicted_files = os.path.join(config['predict_dir'], 'predict')
    for fname in os.listdir(predicted_files):
        file_path = os.path.join(predicted_files, fname)
        os.remove(file_path)


@app.route('/')
def render_file():
   return render_template('/main.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        remove_prediction() # Initial step: remove remaining previous predicted image
 
        f = request.files['file']
        if f and allowed_file(f.filename):
            filename_list = []
            filename = secure_filename(f.filename)

            parsed_name = filename.split(".")
            file_type = parsed_name[len(parsed_name)-1]
            if file_type == 'avi' or file_type == 'mp4' : # video file
                #call video_segment function
                comparison_image_path = config['comparison']
                video_path = os.path.join(config['upload'], filename)
                f.save(video_path)
                input_image_path = config['image_dir']
                count = video_segment.image_selector(input_image_path, comparison_image_path)
                filename_list = video_segment.image_reader(video_path, UPLOAD_FOLDER, comparison_image_path)

            else :
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # store images uploaded by user
                
            # call open pose and running model by forking background process
            os.system('sh %s &' % config['background'])

            return redirect(url_for('uploaded_file',
                                                 filename=filename))


@app.route('/new_meaning', methods=['GET', 'POST'])
def move_to_new_label():
    if request.method == 'POST':
        new_meaning = request.form['meaning']

        new_label_dir = os.path.join(LABELS, new_meaning)
        if not os.path.isdir(new_label_dir):
            os.makedirs(new_label_dir)

        move_prediction(new_label_dir)
        return redirect(url_for('render_file'))


@app.route('/feedback/<label>')
def move_to_label(label):
    feedback_label_dir = os.path.join(LABELS, label)
    move_prediction(feedback_label_dir)
    return redirect(url_for('render_file'))


@app.route('/meaning')
def processing():
    if not os.path.isfile("meaning.txt"):
        abort(404)
    f = open("meaning.txt", "r")
    content = f.read()
    if not content:
        abort(404)
    else:
        shutil.copyfile("meaning.txt", "meaning_temp.txt") # copy predicted label for corrcet feedback
    f.close()

    os.remove("meaning.txt")

    text = refine_content(content)

    if check_video(content):
        remove_prediction() # remove previous predicted image --> temp for dev TODO: remove comment
        os.remove("meaning_temp.txt") # no feedback
    print("\n================text: {} ==================\n".format(text)) # TODO: change it as log
    return text


@app.route('/yes')
def moveImgToTrainFolder():
    if os.path.exists("meaning_temp.txt"):
        move_correct_prediction()
    return redirect(url_for('render_file'))


@app.route('/list')
def sendLabelList():
    label_list = os.listdir(LABELS)
    print(label_list)
    return '/'.join(label_list)


@app.route('/show/<filename>')
def uploaded_file(filename):
    return render_template('/loading.html', filename=filename)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
   app.run(host=HOST, port=PORT, debug = True)
