from setuptools import find_packages, setup

package_name = 'talker'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Marco Soriano',
    maintainer_email='marco.soriano5102@comunidad.unam.mx',
    description='ROS 2 package for text-to-speech node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'talker = talker.talker:main',
        ],
    },
)

