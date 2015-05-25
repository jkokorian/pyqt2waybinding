from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pyqt2waybinding',
      version='0.2',
      description='Simple framework for easy 2-way binding with PyQt',
      long_description=readme(),
      url='http://github.com/jkokorian/pyqt2waybinding',
      author='J. Kokorian',
      author_email='J.Kokorian@TUDelft.nl',
      license='MIT',
      packages=[
          'pyqt2waybinding'
          ],
      install_requires=[],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)