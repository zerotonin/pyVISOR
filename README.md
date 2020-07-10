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
    $ sudo apt-get install xboxdrv
    $ sudo systemctl enable xboxdrv.service
    $ sudo systemctl start xboxdrv.service
```


Anaconda is a package that includes all sub packages we need except opencv, pyav and pims, which can be installed easily:

Download from https://www.continuum.io/downloads

Than install everything through Anaconda
```
    $ conda env create -f visor.yaml
    $ conda activate visor
    $ conda install -c conda-forge av
    $ python -m pip install pygame
    $ conda install -c conda-forge moviepy S
    $ python setup.py install # Installing pymovscore
```

### Troubleshouting

after installation resource json and del.png are not found copy those files resources to /path/to/ANACONDA/env/visor/lib/python/sitepackeges/pymovscore

```
    $ cp -rvf /visor/resources....
    $ cp -rvf json
    $ cp -rvf pictures Gui
```
