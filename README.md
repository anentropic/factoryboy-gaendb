factoryboy-gaendb
=================

Factoryboy base factories and helpers for Google App Engine ndb models

Example:

```
from gaendb.factories import NDBFactory, KeyAttribute

class UserFactory(NDBFactory):
    class Meta:
        model = User

    name = fuzzy.FuzzyText()
    gender = fuzzy.FuzzyChoice(['M', 'F'])

class ArticleFactory(FromSessionFactory):
    class Meta:
        model = Article

    author = KeyAttribute(UserFactory)
    title = fuzzy.FuzzyText()

In  [1]: article = ArticleFactory()  # build
In  [2]: article.author
Out [2]: Key('User', 1)
In  [3]: article.author.get()
Out [3]: User(key=Key('User', 1), gender='F', name=u'UvaxfhCjiwlg')  # built instance
```
