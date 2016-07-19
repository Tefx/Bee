from __future__ import print_function

import inspect

import gevent
import msgpack as serializer
import zmq.green as zmq


class RPCMethod(object):
    def __init__(self, f):
        self.f = f


class Bee(object):
    names = []
    methods = []
    broker = None

    def process(self, address, msg):
        (index, argv, kwargs) = serializer.loads(msg)
        res = self.methods[index](self, *argv, **kwargs) if index >= 0 else self.names
        self.broker.send_multipart([address, b'', serializer.dumps(res)])

    def run(self, address):
        self.names, methods = zip(*inspect.getmembers(self, lambda obj: isinstance(obj, RPCMethod)))
        self.methods = [m.f for m in methods]
        self.broker = zmq.Context().socket(zmq.ROUTER)
        self.broker.bind(address)

        while True:
            address, _, msg = self.broker.recv_multipart()
            gevent.spawn(self.process, address, msg)


class BeeClient(object):
    def __init__(self, address):
        self.content = zmq.Context()
        self.sock = self.content.socket(zmq.REQ)
        self.sock.connect(address)
        self.sock.send(serializer.dumps((-1, (), {})))
        methods = serializer.loads(self.sock.recv())
        for index, value in enumerate(methods):
            setattr(self, value.decode("utf-8"), self.wrap_function(index))

    def wrap_function(self, index):
        def wrapped(*argv, **kwargs):
            self.sock.send(serializer.dumps((index, argv, kwargs)))
            return serializer.loads(self.sock.recv())
        return wrapped


class AsyncBeeClient(object):
    def __init__(self, address):
        self.content = zmq.Context()
        self.address = address
        self.query_methods()

    def query_methods(self):
        sock = self.content.socket(zmq.REQ)
        sock.connect(self.address)
        sock.send(serializer.dumps((-1, (), {})))
        methods = serializer.loads(sock.recv())
        for index, value in enumerate(methods):
            setattr(self, value.decode("utf-8"), self.wrap_function(index))
        sock.close()

    def wrap_function(self, index):
        def wrapped(*argv, **kwargs):
            sock = self.content.socket(zmq.REQ)
            sock.connect(self.address)
            sock.send(serializer.dumps((index, argv, kwargs)))
            res = serializer.loads(sock.recv())
            sock.close()
            return res

        return wrapped
