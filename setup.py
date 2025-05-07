from setuptools import setup, find_packages

setup(
    name='pi-weather-display',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'pi-weather-display=pi_weather_display.main:main',
        ],
    },
    author='Your Name',
    description='Raspberry Pi weather display using Waveshare e-paper',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
