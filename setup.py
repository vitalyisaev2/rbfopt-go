from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

setup(name='plecoptera',
      version='0.1.0',
      description='Find better configuration of your Go service with global optimization algorithms',
      author='Vitaly Isaev',
      author_email='vitalyisaev2@gmail.com',
      url='https://github.com/vitalyisaev2/plecoptera',
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      license_file="LICENSE",
      package_dir={
          '': '.'
      },
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
      ],
      entry_points={
          'console_scripts': [
              'plecoptera = plecoptera.main:main',
          ]
      },
      zip_safe=False,
      python_requires=">=3.7",
      )