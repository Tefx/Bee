# Bee
An micro Python service framework based on zeromq and messagepack

# Install dependencies

    pip install pyzmq msgpack-python


# Use

## Server

    from bee import Bee, RPCMethod, BeeClient
    
    class PointStorage(Bee):
        def __init__(self):
            self.data = []

        @RPCMethod
        def add(self, p):
            self.data.append(p)
            return True

        @RPCMethod
        def add_bulk(self, ps):
            self.data.extend(ps)
            return True
    
    addr = "tcp://127.0.0.1:8888"
    PointStorage().run(addr)

## Client

    addr = "tcp://127.0.0.1:8888"
    c = BeeClient(addr)
    
    data = [[8.58, 2.29] * 5 for _ in xrange(1000000)]
    print all(map(c.add, data))
    print c.add_bulk(data)
