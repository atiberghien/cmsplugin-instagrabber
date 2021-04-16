from setuptools import setup, find_packages

setup(name='cmsplugin-instagrabber',
      version='0.1.1',
      description='Django CMS plugin providing instagram social wall',
      url='https://github.com/atiberghien/cmsplugin-instagrabber',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
           'django-cms',
           'instagram-scraper',
           'instalooter',
           'beautifulsoup4',
           'lxml',
           'requests',
           'django-taggit',
      ],
      zip_safe=False)
