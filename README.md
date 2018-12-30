Body Language Translator
========================

UNIST CSE 2018-fall Deep Learning Project
-----------------------------------------
![v0 0 1-demo](https://user-images.githubusercontent.com/30262658/50344588-f7983680-056e-11e9-9134-aef8ca680149.gif)  

Version
-------
v0.0.1

Prerequisites
-------------
- Python 3.5
- OpenPose
  - https://github.com/CMU-Perceptual-Computing-Lab/openpose
  - [Installation](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md#installation)

OS
---
- Ubuntu

Set Up
------
To activate virtual environment:    
```
$ virtualenv --system-site-packages -p python3 ./venv
$ source ./venv/bin/activate
```    
To install site-packages:    
```
(venv)$ pip install -r requirements.txt
```

Usage
-----
Configuration: (Refer to example.conf)
```
$ cd config/
$ vi config.conf
```

To open interface on web-browser:
```
$ cd interface/
$ python user.py
```
