import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='seller-stats',
    version='0.0.3',
    author='Artem Kiselev',
    author_email='artem.kiselev@gmail.com',
    description='Various statistics for marketplace sellers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wondersell/seller-stats',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
