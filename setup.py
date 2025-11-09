"""
USAGE: 
   o install in develop mode: navigate to the folder containing this file,
                              and type `pip install -e . --user`
                              (ommit '--user' if you want to install for 
                               all users)                           
"""


from setuptools import find_packages, setup

setup(name='pyvisor',
      version='0.0.1',
      description='Desktop toolkit for manual ethology scoring with a PyQt GUI.',
      url='https://github.com/bartgeurten/pyVISOR',
      author='Bart Geurten, Ilyas Kuhlemann',
      author_email='ilyasp.ku@gmail.com',
      license='GPL-3.0-or-later',
      packages=find_packages(include=['pyvisor', 'pyvisor.*']),
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
      include_package_data=True,
      package_data={
          'pyvisor.GUI': [
              'guidefaults_animals.json',
              'guidefaults_movscoregui.pkl',
              'ana.npy',
              'pictures/*',
              'xwing.png'
          ],
          'pyvisor.resources': ['**/*'],
      },
      zip_safe=False)
