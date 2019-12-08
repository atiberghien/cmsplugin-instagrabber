from setuptools import setup, find_packages

setup(name='instagrabber',
      version='0.1.0',
      description='Django CMS plugin providing instagram social wall',
      url='https://github.com/atiberghien/cmsplugin-instagrabber',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
           'Django',
           'django-cms',
           'instagram-scraper',
           'instalooter',
           'django-sekizai',
           'beautifulsoup4',
           'lxml',
           'requests',
           'django-taggit',
      ],
      zip_safe=False)
