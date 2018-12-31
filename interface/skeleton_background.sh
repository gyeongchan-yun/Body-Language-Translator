#!/bin/bash

PROJECT=/home/kaka/Body-Language-Translator
OPEN_POSE_HOME=/home/kaka/openpose

input_dir=${PROJECT}/image/user_input
output_dir=${PROJECT}/image/user_output/

new_dir=${input_dir}/new
done_dir=${input_dir}/done/

cd ${OPEN_POSE_HOME}
# ./build/examples/openpose/openpose.bin --image_dir ${new_dir} --face --hand --write_images ${output_dir}
./build/examples/openpose/openpose.bin --image_dir ${new_dir} --face --hand --disable_blending --write_images ${output_dir}

cd ${new_dir}  # move only files to done/ dir
rm -rf ${new_dir}/comparison_images/*
find . -type f -exec mv -t ${done_dir} {} + 

mv ${PROJECT}/image/user_output/* ${PROJECT}/image/test/predict/

python3 ${PROJECT}/model/dev_predict.py | tail -1 > ${PROJECT}/interface/meaning.txt



