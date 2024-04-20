from setuptools import setup, find_packages
from pathlib import Path

data_packages = ['{}'.format(p).replace('/', '.')
                 for p in list(Path('discrete_optimization/data').glob('**'))
                 + list(Path('discrete_optimization').glob('**/minizinc'))]
data_packages = [d for d in data_packages if "data.gpgp" not in d and "data.fleet_rotation" not in d]
# dirty fix to remove some local folder

setup(
    name='discrete_optimization',
    version='0.1',
    packages=find_packages() + data_packages,
    include_package_data=True,
    package_data={'': ['*']},
    install_requires=[
        'shapely>=1.7',
        'mip>=1.9',
        'minizinc>=0.3',
        'deap>=1.3',
        'networkx>=2.4',
        'numba>=0.50',
        'matplotlib>=3.1',
        "seaborn>=0.10.1",
        "pymzn>=0.18.3",
        "ortools>=8.0",
        "tqdm",
        "scikit-learn",
        "sortedcontainers"
    ],
    url='',
    license='',
    # package_dir={'': 'discrete_optimization'},
    author='Airbus-AIR',
    author_email='',
    description='Discrete optimisation library'
)
