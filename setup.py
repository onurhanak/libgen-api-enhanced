import setuptools
from pathlib import Path

version = {}
exec(Path("libgen_api_enhanced/_version.py").read_text(encoding="utf-8"), version)

long_description = Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="libgen_api_enhanced",
    packages=["libgen_api_enhanced"],
    version=version["__version__"],
    description="Search Library genesis by Title or Author",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/onurhanak/libgen-api-enhanced",
    author="Onurhan Ak",
    author_email="",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords=["libgen search", "libgen api", "search libgen", "search library genesis"],
    install_requires=["bs4", "requests"],
    python_requires=">=3.10",
)
