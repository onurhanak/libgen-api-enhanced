import setuptools

with open("README.md", "r", errors="replace") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libgen_api_enhanced",
    packages=["libgen_api_enhanced"],
    version="1.0.5",
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
)
