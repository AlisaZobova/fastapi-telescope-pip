from setuptools import setup, find_packages
import os

# Get long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Package data (include static files for the frontend)
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('static')

setup(
    name="fastapi-telescope",
    version="0.1.0",
    author="Alisa Zobova",
    author_email="zobovaalice@gmail.com",
    description="Middleware and tool for FastApi HTTP requests and DB queries debugging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "": extra_files,
    },
    include_package_data=True,
    install_requires=[
        "fastapi==0.115.8",
        "uvicorn==0.34.0",
        "psycopg2-binary==2.9.10",
        "SQLAlchemy==2.0.38",
        "alembic==1.14.1",
        "pydantic==2.10.6",
        "loguru==0.7.3",
        "asyncpg==0.30.0",
        "pytz==2025.1",
        "python-dotenv==1.0.1",
        "pydantic-settings==2.8.0",
        "fastapi-pagination==0.12.34",
        "aiofiles==23.2.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)