import xmlrpc.client

if __name__ == '__main__':
    IP = '127.0.0.1'
    PORT = '8888'

    s = xmlrpc.client.ServerProxy("http://{0}:{1}".format(IP, PORT))
    print(s.signalSlave())
