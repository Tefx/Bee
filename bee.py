from __future__ import print_function

import inspect

import msgpack as serializer
import nanomsg


class RPCMethod(object):
    def __init__(self, f):
        self.f = f


class Bee(object):
    def run(self, address):
        names, methods = zip(*inspect.getmembers(self, lambda obj: isinstance(obj, RPCMethod)))
        methods = [m.f for m in methods]
        sock = nanomsg.Socket(nanomsg.REP)
        sock.bind(address)
        while True:
            (index, argv, kwargs) = serializer.loads(sock.recv())
            res = methods[index](self, *argv, **kwargs) if index >= 0 else names
            sock.send(serializer.dumps(res))


class BeeClient(object):
    def __init__(self, address):
        self.sock = nanomsg.Socket(nanomsg.REQ)
        self.sock.connect(address)
        self.sock.send(serializer.dumps((-1, (), {})))
        methods = serializer.loads(self.sock.recv())
        for index, value in enumerate(methods):
            setattr(self, value, self.wrap_function(index))

    def wrap_function(self, index):
        def wrapped(*argv, **kwargs):
            self.sock.send(serializer.dumps((index, argv, kwargs)))
            return serializer.loads(self.sock.recv())
        return wrapped
