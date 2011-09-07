from setuptools import setup, find_packages

setup(
    name='django-solr',
    version='0.0.2',
    description='Django-Solr search',
    author='Sophilabs',
    author_email='contact@sophilabs.com',
    url='https://github.com/sophilabs/django-solr/',
    download_url='https://github.com/sophilabs/django-solr/downloads/'
    license='BSD'
    packages=packages=find_packages(exclude=('example')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
