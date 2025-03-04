class Request(object):
    def __init__(self, path):
        while path.startswith('/'):
            path = path[1:]

        while path.endswith('/'):
            path = path[:-1]

        self.path = path
