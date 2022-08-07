from setuptools import setup

setup(
    name='iris-ioc-velo-module',
    python_requires='>=3.9',
    version='0.1.0',
    packages=['iris_ioc_velo_module', 'iris_ioc_velo_module.velo_handler'],
    url='https://github.com/BadBloopZ/iris-ioc-velo-module',
    license='Lesser GNU GPL v3.0',
    author='Stephan Mikiss',
    author_email='stephan.mikiss@gmail.com',
    description='`iris-ioc-velo-module` is a IRIS processor module created with https://github.com/dfir-iris/iris-skeleton-module. It parses added IOCs and starts hunts in Velociraptor across all devices.',
    install_requires=[
        "pyvelociraptor",
        "setuptools==59.6.0"
    ]
)
