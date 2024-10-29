from setuptools import setup, find_packages

setup(
    name="kg-irm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
        'selenium',
        'webdriver-manager',
        'python-dotenv',
        'pyyaml'
    ]
)