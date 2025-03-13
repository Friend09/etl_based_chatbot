from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="weather_etl_chatbot",
    version="0.1.0",
    author="Raghuvamsi Ayapilla",
    author_email="vamsi.ay@gmail.com",
    description="ETL pipeline and chatbot for Louisville weather data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Friend09/etl_based_chatbot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "run-etl=etl.weather_collector:main",
            "run-webapp=web.app:main",
        ],
    },
)
