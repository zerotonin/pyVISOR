# README #


### What is this repository for? ###

This is the Manual Ethology Scorer (MES) BAsically it can run image sequences and movies while you type in through a gamepad what the organisms are doing.

* Version: 0
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### ToDo ###

* Core 
    * Update dataIO to include analysis data if present

* GUI
    * Annotation Plots A time axis showing activities (seperate thread)
    * Analysis Graphics - Results Tab
    * Autosave
    * hidden dirs should be changed to the multiplatform qt
        $ settings = QSettings("gwdg", "patras")
        $ lastDir = settings.value("lastDir", "")
        $ settings.setValue("lastDir", self.__from)
        

* Binaries for all platforms (Win, Mac,Linux, Rasp)


### How do I get set up? ###

You might need an Xbox One Gamepad driver:

https://github.com/paroj/xpad

```
sudo git clone https://github.com/paroj/xpad.git /usr/src/xpad-0.4
sudo dkms install -m xpad -v 0.4
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
```
OpenCV installation:

https://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html

```
sudo apt install build-essential
sudo apt install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
sudo apt-get install libsdl-ttf2.0-0
```

Anaconda is a package that includes all sub packages we need except opencv, pyav and pims, which can be installed easily:

Download from https://www.continuum.io/downloads

Than install everything through Anaconda
```
sudo apt install qt5-default
bash ~/Downloads/Anaconda2-4.0.0-Linux-x86_64.sh 

???pip install https://github.com/soft-matter/pims/archive/master.zip

```

Make conda environment
```

conda env create -f visor.yaml
conda activate visor
conda install -c conda-forge av
python -m pip install pygame
conda install -c conda-forge moviepy 

python setup.py install # Installing pymovscore
```
