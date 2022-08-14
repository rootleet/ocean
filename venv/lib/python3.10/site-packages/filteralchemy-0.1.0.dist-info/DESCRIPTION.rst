Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Description: =============
        filteralchemy
        =============
        
        .. image:: https://img.shields.io/pypi/v/filteralchemy.svg
            :target: http://badge.fury.io/py/filteralchemy
            :alt: Latest version
        
        .. image:: https://readthedocs.org/projects/filteralchemy/badge/?version=latest
            :target: https://filteralchemy.readthedocs.org/en/latest/?badge=latest
            :alt: Documentation Status
        
        .. image:: https://img.shields.io/travis/jmcarp/filteralchemy/dev.svg
            :target: https://travis-ci.org/jmcarp/filteralchemy
            :alt: Travis-CI
        
        .. image:: https://img.shields.io/codecov/c/github/jmcarp/filteralchemy/dev.svg
            :target: https://codecov.io/github/jmcarp/filteralchemy
            :alt: Code coverage
        
        **filteralchemy** is a declarative query builder for SQLAlchemy. **filteralchemy** uses marshmallow-sqlalchemy_ to auto-generate filter fields and webargs_ to parse field parameters from the request.
        
        Install
        -------
        
        .. code-block::
        
            pip install filteralchemy
            
        Quickstart
        ----------
        
        .. code-block:: python
        
            import flask
            from models import Album, session
            from webargs.flaskparser import parser
            from filteralchemy import FilterSet
        
            class AlbumFilterSet(FilterSet):
                class Meta:
                    model = Album
                    query = session.query(Album)
                    parser = parser
        
            app = flask.Flask(__name__)
        
            @app.route('/albums')
            def get_albums():
                query = AlbumFilterSet().filter()
                return flask.jsonify(query.all())
        
        .. _marshmallow-sqlalchemy: https://marshmallow-sqlalchemy.readthedocs.org/
        .. _webargs: https://webargs.readthedocs.org/
        
Keywords: filteralchemy
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
