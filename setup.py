from setuptools import setup, find_packages

setup(
    name="formula-student-track-builder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
        "numpy>=1.24.3",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A track builder tool for Formula Student competitions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/formula-student-track-builder",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "track-builder=main:main",
        ],
    },
)
