#!/bin/bash
virtualenv --system-site-packages -p python3 ./venv
source ./venv/bin/activate

pip install -r requirements.txt

if [[ ! -d ./logs ]]; then
    mkdir ./logs
fi 

if [[ ! -d $PWD/model/saved_model/bak ]]; then
    mkdir $PWD/model/saved_model/bak
fi

cd $PWD/image

if [[ ! -e ./test ]]; then
    mkdir -p ./test/test_image
fi

if [[ ! -e ./user_input ]]; then
    mkdir -p ./user_input/new/input_video
    mkdir -p ./user_input/new/comparison_images
    mkdir -p ./user_input/done
fi

if [[ ! -e ./user_output ]]; then
    mkdir ./user_output
fi
