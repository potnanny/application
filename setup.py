import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='potnanny',
    version='0.4.11',
    python_requires=">=3.11",
    packages=setuptools.find_packages(),
    description='Potnanny grow room automation controller.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='J Leary',
    author_email='potnanny@gmail.com',
    url='https://github.com/potnanny/application',
    install_requires=[
        'greenlet',
        'bleak',
        'aio-databases[aiosqlite]',
        'peewee-aio',
        'quart',
        'quart-auth',
        'quart-wtforms',
        'pyyaml',
        'gpiozero',
        'marshmallow',
        'pyyaml',
        'python-daemon',
        'markupsafe',
    ],
    package_data = {
        '': ['*.html', '*.css', '*.js', '*.woff2'],
    },
    entry_points = {
        'console_scripts': [
            'potnanny=potnanny.cli:main',
        ],
    },
)
