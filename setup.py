"""
USAGE: 
   o install in develop mode: navigate to the folder containing this file,
                              and type `pip install -e . --user`
                              (ommit '--user' if you want to install for 
                               all users)                           
"""


from setuptools import setup

setup(name='pyvisor',
      version='0.0.1',
      description='',
      url='',
      author='Bart Geurten, Ilyas Kuhlemann',
      author_email='ilyasp.ku@gmail.com',
      license='',
      packages=["pyvisor",
                "pyvisor.analysis",
                "pyvisor.exception",
                "pyvisor.GUI",
                "pyvisor.GUI.icon_gallery",
                "pyvisor.GUI.tab_behaviours"],
      entry_points={
          "console_scripts": [],
          "gui_scripts": ["pyvisor-gui = pyvisor.GUI.run_gui:main"]         
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
          "xlsxwriter",
          "PyQt5"
      ],
      zip_safe=False)
