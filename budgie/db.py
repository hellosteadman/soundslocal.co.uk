from .exceptions import ComparerNotFoundError


class Comparer(object):
    def __init__(self, key):
        self.key = key

    @classmethod
    def infer(self, key):
        parts = key.split('__')

        if len(parts) == 2:
            key, comparer = parts

            if comparer == 'exact':
                return EqualsComparer(key)

            raise ComparerNotFoundError(comparer)

        if len(parts) > 2:
            return MultiCompare(parts)

        return EqualsComparer(key)


class EqualsComparer(Comparer):
    def compare(self, a, b):
        return a == b


class MultiCompare(Comparer):
    def __init__(self, parts):
        raise Exception(parts)

    def compare(self, a, b):
        pass
