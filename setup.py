from setuptools import setup, find_packages

setup(
    name="instadown",
    version="0.1.0",
    author="Stefan Trajanov",
    author_email="trajanovstefan@yahoo.com",
    description="A Simple and Fast Python package to download Instagram images and reels using Selenium",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stefantrajanov/instadown",  # Your GitHub repo
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver-manager",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)