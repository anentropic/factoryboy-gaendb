from google.appengine.ext import ndb

import factory
from factory.base import BaseFactory, FactoryMetaClass


class KeyProxy(ndb.Key):
    """
    A Key that returns a factory-built instance when you get() on it
    """

    __metaclass__ = type  # prevent some ndb.Key magic

    def __new__(cls, *args, **kwargs):
        """
        We still need to be able to pass an isinstance(ndb.Key) check
        due to validation in ndb.Model when setting a KeyProperty...
        so we inherit from ndb.Key but strip out all the evil magic.
        """
        self = object.__new__(cls)
        return self

    def __init__(self, kind_factory, *args, **kwargs):
        self._key = ndb.Key(*args, **kwargs)
        self._kind_factory = kind_factory

    def get(self, _create=False, **ctx_options):
        """
        NOTE: `ctx_options` are ignored
        """
        if _create:
            return self._kind_factory.create(key=self)
        else:
            return self._kind_factory(key=self)

    def __getattribute__(self, name):
        # proxy anything except our own attrs thru to the real ndb.Key
        if name.startswith('__') or name in ('get', '_key', '_kind_factory'):
            return object.__getattribute__(self, name)
        return getattr(self._key, name)


class KeyAttribute(factory.LazyAttributeSequence):
    """
    A factory_boy LazyAttributeSequence that acts like an ndb.KeyProperty
    """
    def __init__(self, kind_factory, _parent=None, _id=None, type=int):
        def key_func(obj, seq):
            if hasattr(_id, 'evaluate'):
                key_id = _id.evaluate(seq, obj, None)
                if key_id is None:
                    key_id = seq
            else:
                key_id = seq

            if hasattr(_parent, 'evaluate'):
                key_parent = _parent.evaluate(seq, obj, None)
            else:
                key_parent = _parent

            return KeyProxy(
                kind_factory,
                kind_factory._get_model_class().__name__,
                key_id,
                parent=key_parent
            )
        super(KeyAttribute, self).__init__(function=key_func, type=type)


class NDBFactoryMetaClass(FactoryMetaClass):
    """
    Needed so we can auto generate a key = KeyAttribute(cls) onto the factory.

    We also add `id` and `parent` attributes to the factory allowing you
    to pass those in the kwargs to create() or build() to specify id and parent
    of the auto-generated ndb key (same signature as ndb Model constructor).
    """
    def __new__(meta_cls, class_name, bases, attrs):
        new_cls = super(NDBFactoryMetaClass, meta_cls).__new__(meta_cls,
                                                               class_name,
                                                               bases, attrs)
        # these SelfAttributes allow us to specify `id` and `parent` for
        # key when generating the instance
        key_attr = KeyAttribute(
            new_cls,
            _parent=factory.SelfAttribute('parent', default=None),
            _id=factory.SelfAttribute('id'),
        )
        new_cls.key = key_attr
        new_cls._meta.declarations['key'] = key_attr

        key_id_attr = factory.Sequence(lambda seq: seq)
        new_cls.id = key_id_attr
        new_cls._meta.declarations['id'] = key_id_attr
        if 'id' not in new_cls._meta.exclude:
            new_cls._meta.exclude += ('id',)

        new_cls.parent = None
        new_cls._meta.declarations['parent'] = None
        if 'parent' not in new_cls._meta.exclude:
            new_cls._meta.exclude += ('parent',)

        return new_cls


class NDBBaseMeta:
    abstract = True
    strategy = factory.BUILD_STRATEGY


class NDBBaseFactory(BaseFactory):
    """
    BaseFactory for GAE NDB models.
    """
    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        if not create:
            return
        # convert proxied keys to real ones (i.e. create related)
        for name, property_ in obj.to_dict().items():
            value = getattr(obj, name)
            if isinstance(value, KeyProxy):
                real = value._key.get()
                if real is None:
                    value.get(_create=True).put()
                setattr(obj, name, value._key)
        proxy_key = obj.key
        obj._key = obj.key._key
        obj.put()
        # put our proxy key back in place
        obj._key = proxy_key

    @classmethod
    def _setup_next_sequence(cls):
        """
        GAE NDB keys cannot have id=0, that generates an invalid key

        Returns:
            int: the first available ID to use for instances of this factory.
        """
        return 1


NDBFactory = NDBFactoryMetaClass('NDBFactory', (NDBBaseFactory,), {
    'Meta': NDBBaseMeta,
    '__doc__': """
    Factory base with build and create support.

    Extended to support GAE NDB Model.
    """,
})
