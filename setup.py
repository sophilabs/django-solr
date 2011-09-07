from setuptools import setup, find_packages

setup(
    name='django-solr',
    version='0.0.1',
    description='Django-Solr search',
    author='Sophilabs',
    author_email='contact@sophilabs.com',
    url='http://github.com/sophilabs/django-solr/',
    packages=find_packages(),
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
