from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

setup(name='rbfopt-go',
      # version_config={
      #     "dev_template": "{tag}",
      # },
      setuptools_git_versioning={
          "enabled": True,
          "template": "{tag}",
          "dirty_template": "{tag}",
      },
      description='Find better configuration of your Go service with derivative-free optimization algorithms',
      author='Vitaly Isaev',
      author_email='vitalyisaev2@gmail.com',
      url='https://github.com/vitalyisaev2/rbfopt-go',
      packages=find_packages(),
      setup_requires=["setuptools-git-versioning"],
      install_requires=(
          "jsons==1.6.0",
          "numpy>=1.22",
          "Pyomo==6.1.2",
          "rbfopt==4.2.2",
          "requests==2.26.0",
          "urllib3==1.26.7",
          "pandas==1.3.5",
          "matplotlib==3.5.1",
          "scipy",
          "colorhash==1.0.4"
      ),
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
              'rbfopt-go-wrapper = wrapper.main:main',
          ]
      },
      zip_safe=False,
      python_requires=">=3.7",
      )
