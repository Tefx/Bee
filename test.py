from gevent import sleep

from bee import Bee, RPCMethod, AsyncBeeClient


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


class Echo(Bee):
    @RPCMethod
    def echo(self, x):
        sleep(1)
        return x


if __name__ == '__main__':
    from sys import argv

    addr = "tcp://127.0.0.1:8888"
    # addr = "ipc://tmp.ipc"

    # if argv[1] == "server":
    #     PointStorage().run(addr)
    # else:
    #     c = BeeClient(addr)
    #     data = [[8.58, 2.29] * 5 for _ in range(100000)]
    #     if argv[1] == "add":
    #         print(all(map(c.add, data)))
    #     elif argv[1] == "add_bulk":
    #         print(c.add_bulk(data))

    from gevent.pool import Pool
    if argv[1] == "server":
        Echo().run(addr)
    else:
        p = Pool()
        c = AsyncBeeClient(addr)
        res = p.map(c.echo, range(100))
        print(list(res))
