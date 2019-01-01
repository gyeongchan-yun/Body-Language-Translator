import os
import time
import schedule

dir_path = os.path.dirname(os.path.realpath(__file__))


def train():
    path = dir_path + '/../model'
    print("TRAIN START")
    os.system('python3 %s/train.py' % path)


schedule.every().hour.do(train)  # train in every hour


while True:
    print("TRAIN SCHEDULER EXECUTE")
    schedule.run_pending()
    time.sleep(60)
