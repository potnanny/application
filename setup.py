import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='potnanny',
    version='0.1.0',
    packages=setuptools.find_packages(),
    include_package_data=True,
    description='PotNanny greenhouse automation controller.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='J Leary',
    author_email='potnanny@gmail.com',
    url='https://github.com/potnanny',
    install_requires=[
        'cryptography',
        'aiofiles',
        'aiohttp',
        'aiohttp-jinja2',
        'aiohttp-cors',
        'aiohttp-session',
        'aiosqlite',
        'aiosmtplib',
        'argon2-cffi',
        'bleak',
        'gpiozero',
        'greenlet',
        'marshmallow',
        'passlib',
        'pyyaml',
        'python-daemon',
        'requests',
        'sqlalchemy',
    ],
    package_data = {
        '': ['*.html', '*.css', '*.js'],
    },
    entry_points = {
        'console_scripts': [
            'potnanny=potnanny.cli:main',
        ],
    },
)
