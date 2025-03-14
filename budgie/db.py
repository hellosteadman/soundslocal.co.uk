from .exceptions import ComparerNotFoundError


class Comparer:
    comparers = {}

    def __init__(self, key):
        self.key = key

    @classmethod
    def register(cls, name, comparer_cls):
        cls.comparers[name] = comparer_cls

    @classmethod
    def infer(cls, key):
        parts = key.split('__')

        if len(parts) > 1:
            attr_chain = parts[:-1]
        else:
            attr_chain = [parts.pop()]

        comparer_name = parts[-1] if len(parts) > 1 else 'exact'
        comparer_cls = cls.comparers.get(comparer_name)

        if not comparer_cls:
            raise ComparerNotFoundError('Comparer \'%s\' not found' % key)

        return comparer_cls(attr_chain)

    def resolve_attr_chain(self, obj):
        for attr in self.key:
            if not hasattr(obj, attr):
                raise ComparerNotFoundError('Comparer \'%s\' not found' % attr)

            obj = getattr(obj, attr)

        return obj


class EqualsComparer(Comparer):
    def compare(self, obj, value):
        return self.resolve_attr_chain(obj) == value


class LessThanComparer(Comparer):
    def compare(self, obj, value):
        attr_value = self.resolve_attr_chain(obj)
        return attr_value is not None and attr_value < value


class LessThanOrEqualComparer(Comparer):
    def compare(self, obj, value):
        attr_value = self.resolve_attr_chain(obj)
        return attr_value is not None and attr_value <= value


class GreaterThanComparer(Comparer):
    def compare(self, obj, value):
        attr_value = self.resolve_attr_chain(obj)
        return attr_value is not None and attr_value > value


class GreaterThanOrEqualComparer(Comparer):
    def compare(self, obj, value):
        attr_value = self.resolve_attr_chain(obj)
        return attr_value is not None and attr_value >= value


class InComparer(Comparer):
    def compare(self, obj, value):
        return value in self.resolve_attr_chain(obj)


Comparer.register('exact', EqualsComparer)
Comparer.register('lt', LessThanComparer)
Comparer.register('lte', LessThanOrEqualComparer)
Comparer.register('gt', GreaterThanComparer)
Comparer.register('gte', GreaterThanOrEqualComparer)
Comparer.register('in', InComparer)
