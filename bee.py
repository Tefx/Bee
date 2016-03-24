from __future__ import print_function

import inspect

import msgpack as libpack
import nanomsg


class RPCMethod(object):
    def __init__(self, f):
        self.f = f


class Bee(object):
    def __init__(self):
        self.index, methods = zip(*inspect.getmembers(self, lambda obj: isinstance(obj, RPCMethod)))
        self.methods = [x.f for x in methods]

    def run(self, address):
        sock = nanomsg.Socket(nanomsg.REP)
        sock.bind(address)
        while True:
            msg = sock.recv()
            (index, argv, kwargs) = libpack.loads(msg)
            if index == -1:
                res = self.index
            else:
                res = self.methods[index](self, *argv, **kwargs)
            sock.send(libpack.dumps(res))


class BeeClient(object):
    def __init__(self, address):
        self.address = address
        self.sock = nanomsg.Socket(nanomsg.REQ)
        self.sock.connect(address)
        self.sock.send(libpack.dumps((-1, (), {})))
        methods = libpack.loads(self.sock.recv())
        for index, value in enumerate(methods):
            setattr(self, value, self.wrap_function(index))

    def wrap_function(self, index):
        def wrapped(*argv, **kwargs):
            self.sock.send(libpack.dumps((index, argv, kwargs)))
            res = libpack.loads(self.sock.recv())
            return res

        return wrapped
