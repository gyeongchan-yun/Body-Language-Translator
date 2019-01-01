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
set up initially:
```
$ source initial-setup.sh
```
To activate virtual environment:
```
$ source virtualenv.sh
```

Usage
-----
Configuration: (Refer to example.conf)  
```
$ cp config/example.conf config/config.conf
Replace ${user-path} in config.conf to real path.
```
  
To open interface on web-browser:
```
$ python interface/user.py
```

