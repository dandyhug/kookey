import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="kookey",
    version="1.0.3",
    author="Hyeyeon Koo",
    author_email="go8476@naver.com",
    description="This is an Extractor for keywords and synonyms with corpus which are composed of korean, english and special-characters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HyeyeonKoo/extractor",
    packages=setuptools.find_packages(),
    keywords = [
        'keyword_extractor',
        'synonym_extractor',
        'nlp',
        'korean&english',
        'korean&english&chracter'
    ],
    install_requires=[
        "gensim==3.8.3",
        "tensorflow>=2.0.0",
        "numpy>=1.12.1",
        "soynlp>=0.0.493",
        "nltk>=3.5",
        "konlpy>=0.5.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)