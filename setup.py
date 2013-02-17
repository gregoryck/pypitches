from distutils.core import setup

setup (
        name = "PyPitches",
        version = "0.1.0",
        author = "Greg Kettler",
        author_email = "gkettler@gmail.com",
        packages=['pypitches', 'pypitches.test'],
        #scripts=[],
        url="http://thefamilyatomics.com/pypitches",
        description="Analyzing Major League Baseball pitch data from PITCHf/x",
        long_description=open('README.rst').read(),
        requires=[
            "SQLAlchemy (>=0.7)",
            "BeautifulSoup (>=3.2.0)",
            "matplotlib (>=1.0.0)",
            "numpy (>=1.6.1)",
            "flask (>=0.8)",
            "ipython (>=0.12)",
            "PyYAML (>=3.10)",
            "nose (>=1.1.2)",
            "coverage (>=3.5.2)",
            "Jinja2 (>=2.6)",
            "psycopg2 (>=2.4.4)",
            ],
        )

