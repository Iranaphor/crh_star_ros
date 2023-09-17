from setuptools import setup
from glob import glob
import os

package_name = 'crh_star_ros'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
#        (f"share/{package_name}/launch", glob(os.path.join('launch', '*launch.[pxy][yml]*'))),
    ],
    zip_safe=True,
    maintainer='james',
    maintainer_email='primordia@live.com',
    description='Deployment of crh_star_ros',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'route_calculator.py = crh_star_ros.route_calculator:main'
        ],
    },
)
