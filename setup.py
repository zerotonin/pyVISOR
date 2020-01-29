"""
USAGE: 
   o install in develop mode: navigate to the folder containing this file,
                              and type 'python setup.py develop --user'.
                              (ommit '--user' if you want to install for 
                               all users)                           
"""


from setuptools import setup

## use setup to install SDF package and executable scripts
setup(name='pymovscore',
      version='0.99',
      description='',
      url='',
      author='Bart Geurten, Ilyas Kuhlemann',
      author_email='ilyasp.ku@gmail.com',
      license='',
      packages=["pymovscore",
                "pymovscore.GUI",
                "pymovscore.GUI.tab_behaviours"],
      entry_points={
          "console_scripts": [],
          "gui_scripts" : ["pymovscore-gui = pymovscore.GUI.run_gui:main"]         
      },
      install_requires=[
          "pillow",
          "pygame",
          "numpy",
          "matplotlib",
          "pims",
          "av",
          "pandas",
          "scipy",
          "dill",
          "xlsxwriter"
      ],
      zip_safe=False)
