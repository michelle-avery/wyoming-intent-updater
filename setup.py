from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
module_dir = this_dir / "wyoming_intent_updater"

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

setup(
    name='wyoming_intent_updater',
    version='0.1',
    packages=find_packages(),
    install_requires=[requirements],
    entry_points={
        'console_scripts': [
            'wyoming_intent_updater=wyoming_intent_updater.main:main',
        ],
    },
)
