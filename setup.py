import json
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def load_requirements_from_pipfile_lock(dev: bool):
    with open("Pipfile.lock") as f:
        pipfile_lock = json.load(f)

    if dev:
        mode = "develop"
    else:
        mode = "default"

    return [
        f"{pkg_name}{pkg_info['version']}"
        for pkg_name, pkg_info in pipfile_lock[mode].items()
    ]


setup(
    name="botsh",
    version="0.1.1",
    description="A task runner powered by OpenAI and Docker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Paul Butler",
    author_email="paul@driftingin.space",
    url="https://github.com/drifting-in-space/botsh",
    packages=find_packages("src"),
    package_data={
        "": ["Pipfile", "Pipfile.lock"],
    },
    include_package_data=True,
    package_dir={"": "src"},
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=load_requirements_from_pipfile_lock(False),
    extras_require={
        "dev": load_requirements_from_pipfile_lock(True),
    },
    entry_points={
        "console_scripts": [
            "botsh=botsh.main:main",
        ],
    },
)
