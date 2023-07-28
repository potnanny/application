import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='potnanny',
    version='0.1.1',
    python_requires=">=3.9",
    packages=setuptools.find_packages(),
    include_package_data=True,
    description='Potnanny grow room automation controller.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='J Leary',
    author_email='potnanny@gmail.com',
    url='https://github.com/potnanny/application',
    install_requires=[
        'requests==2.31.0',
        'scrypt==0.8.20',
        'cryptography==41.0.1',
        'aiofiles==23.1.0',
        'aiohttp==3.8.4',
        'aiohttp-jinja2==1.5.1',
        'aiohttp-cors==0.7.0',
        'aiohttp-session==2.12.0',
        'aiosqlite==0.19.0',
        'aiosmtplib==2.0.2',
        'bleak==0.20.2',
        'gpiozero==1.6.2',
        'greenlet==2.0.2',
        'marshmallow==3.19.0',
        'pyyaml==6.0',
        'python-daemon==3.0.1',
        'sqlalchemy==2.0.16',
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
