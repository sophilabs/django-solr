from setuptools import setup, find_packages

setup(
    name='django-solr',
    version='1.0.0alpha3',
    description='Solr Search Engine ORM for Django',
    author='Sophilabs',
    author_email='contact@sophilabs.com',
    url='https://github.com/sophilabs/django-solr',
    download_url='http://github.com/sophilabs/django-solr/tarball/v1.0.0alpha3#egg=django-solr-1.0.0alpha3',
    license='BSD',
    packages=find_packages(exclude=('example')),
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
