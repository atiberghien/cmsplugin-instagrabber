from setuptools import setup, find_packages

setup(name='instagrabber',
      version='0.0.1',
      description='Django CMS plugin providing instagram social wall',
      url='https://github.com/atiberghien/cmsplugin-instagrabber',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
           'Django<2.0',
           'django-cms',
           'instagram-scraper',
           'django-sekizai',
           'beautifulsoup4',
           'requests',
           'django-taggit',
      ],
      zip_safe=False)
