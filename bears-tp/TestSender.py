import sys
import socket
import random
import getopt

import Checksum
import BasicSender

'''
This is a simple interactive sender.
'''
class InteractiveSender(BasicSender.BasicSender):
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))

    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            msg_type, seqno, data, checksum = self.split_packet(response_packet)
            print(type(seqno))
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # Main sending loop.
    def start(self):
        # seqno = 0
        # msg_type = None
        packet0 = self.make_packet('start', 0, "test1")
        packet1 = self.make_packet('data', 1, "test2")
        packet2 = self.make_packet('data', 2, "test3")
        packet3 = self.make_packet('data', 3, "test4")
        packet4 = self.make_packet('end', 4, "test5")
        self.send(packet0)
        print "sent: %s" % packet0
        self.send(packet1)
        print "sent: %s" % packet1
        self.send(packet2)
        print "sent: %s" % packet2
        self.send(packet3)
        print "sent: %s" % packet3
        self.send(packet4)
        print "sent: %s" % packet4    
        response = self.receive()
        self.handle_response(response)
        response = self.receive()
        self.handle_response(response)
        response = self.receive()
        self.handle_response(response)
        response = self.receive()
        self.handle_response(response)
        response = self.receive()
        self.handle_response(response)

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Interactive Sender"
        print "Type 'done' to end the session."
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "p:a:", ["port=", "address="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None


    for o,a in opts:
        if o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a

    s = InteractiveSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
