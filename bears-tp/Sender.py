import sys
import getopt

import Checksum
import BasicSender


# Global Constant
CUMACK = 0
SACK = 1
TIMEOUT_CONSTANT = 0.5

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        # File Spliter and put all packet into packetPool
        # initial first 5 packet to window
        # put first 5 packets to sendingQueue
        self.packetPool = Queue()
        self.window = Window()
        self.sendingQueue = SendQueue()
        self.ackPool = AckPool()
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
            self.mode = SACK
            # only affect two function:
            #   handle_timeout()
            #   Faster_Retransmit
        else:
            self.mode = CUMACK

    # Main sending loop.
    def start(self):
        while not self.packetPool.isEmpty():
            while not self.sendingQueue.isEmpty():
                self.send(self.sendingQueue.deQueue())
            response = self.receive(TIMEOUT_CONSTANT)
            if response == None:
                self.handle_timeout()
            else:
                self.handle_response(response)

    def handle_timeout(self):
        if self.mode == CUMACK:
            for elem in self.window:
                self.sendingQueue.enQueue(elem.packet)
        else:
            for elem in self.window:
                if elem.isAcked() == False:
                    self.sendingQueue.enQueue(elem.packet)

    # [Add]: Handles a response from the receiver.
    def handle_response(self, response_packet):
        if Checksum.validate_checksum(response_packet):
            internalACKPacket = internalACKPacketGenerator(response_packet)
            if self.mode = CUMACK:
                self.handle_cum_ack(internalACKPacket)
            else:
                self.handle_sack_ack(internalACKPacket)


    # [add]: Handle selective ACKs.
    def handle_sack_ack(self, internalACKPacket):
        sAcks = internalACKPacket.sAck()
        for sAck in sAcks:
            



    # [add]: Handle general incoming cumulative ACKs.
    def handle_cum_ack(self, interalACKPacket):
        ack = interalACKPacket.cumAckNo()
        if self.ackPool.isEmpty() == True:
            if self.ackpool.largestAckSoFar() == ack:
                self.handle_dup_ack(ack)
            elif self.ackpool.largestAckSoFar() < ack:
                self.handle_new_ack(ack)
            else:
                break
        elif ack in self.ackPool:
            self.handle_dup_ack(ack)
        else:
            if ack > self.ackPool.peek():
                self.handle_new_ack(ack)



    def handle_new_ack(self, ack):
        while self.ackpool.isEmpty() == False:
            self.ackPool.deQueue()
        self.ackPool.enQueue(ack)
        space = self.window.processAck()
        while space > 0:
            tmp_packet = self.packetPool.deQueue()
            self.sendingQueue.enQueue(tmp_packet)
            self.window.enQueue(self.windowElementGenerator(tmp_packet))




    def handle_dup_ack(self, ack):
        if ackPool.length == 3:
        # implement fast retransmit
            while self.ackPool.isEmpty() == False:
                self.ackPool.deQueue()
            if self.mode = CUMACK:
                packet = self.window.locatePacket(ack)
                self.sendingQueue.enQueue(packet)
            else:
                self.handle_timeout
        elif ackPool < 3:
            self.ackPool.enQueue(ack)
        else:
            print("error, current ackpool size more than 3")



    #################### Helper Functions ##############################

    def windowElementGenerator(self, packet):
        msg_type, seqno, data, checksum = self.split_packet(packet)
        return WindowElement(packet, seqno)

    def internalACKPacketGenerator(self, packet):
        msg_type, seqno, data, checksum = self.split_packet(packet)
        return InternalACKPacket(msg_type, seqno)

    ####################################################################

    def log(self, msg):
        if self.debug:
            print msg



################## Helper Packet Classes ####################

class InternalACKPacket(object):
    def __init__(self, msg_type, seqnoStr):
        self.msg_type = msg_type
        if msg_type == 'sack':
            tmp = seqnoStr.split(';')
            self.cumAckNo = tmp[0]
            self.sAcks = tmp[1].split(',')
        else:
            self.cumAckNo = seqnoStr
            self.sAcks = []

    def msgtype(self):
        return self.msg_type

    def cumAckNo(self):
        return self.cumAckNo

    def sAcks(self):
        return self.sAcks



class WindowElement(object):
    def __init__(self, packet, seqno):
        self.packet = packet
        self._seqno = seqno
        self._isAcked = False

    def setAcked (self):
        self._isAcked = True

    def seqno(self):
        return self.seqno

    def isAcked(self):
        return self._isAcked


#####################################################

################## Data Structure and Interface ####################

class Queue(object):
    def __init__(self):
        self._que = []


    def deQueue(self):
        if not self.isEmpty():
            self._que.pop(0)
        else:
            print("que is isEmpty")

    def enQueue(self, element):
        self._que.append(element)

    def isEmpty(self):
        return len(self._que) == 0

    def size(self):
        return len(self._que)

    def peek(self):
        return self._que(0)

# sliding windown class
class Window(Queue):
    def enQueue(self, element):
        if type(element) == WindowElement and self.size() < 5:
            Queue.enQueue(self, element);
        else:
            print("element is not WindowElement or current size > 5")

    def getUnACKPackets(self):
        unAckLst = []
        for winElt in self._que:
            if not winElt.isAcked():
                unAckLst.append(winElt)
        return unAckLst
    
    def processAck(self, cumAckNo):
        space = 0
        for winElt in self.que:
            if winElt.seqno() < cumAckNo:
                self.que.remove(winElt)
                space += 1;
        return space

    def locatePacket(self, ack):
        for elem in self._que:
            if elem.seqno == ack:
                return elem.packet


# sending queue class
class SendQueue(Queue):
    def extendQueue(self, lst):
        if lst != None and len(lst) != 0:
            self._que.extendQueue(lst)
        else:
            print("lst is None or isEmpty")

# ack pool class
class AckPool(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.largestAckSoFar = -1

    def largestAckSoFar(self):
        return self.largestAckSoFar()

    def enQueue(self, element):
        if element > self.largestAckSoFar:
            self.largestAckSoFar = element
        if type(element) == InternalACKPacket and self.size() < 4:
            if not self.isEmpty():
                assert element.cumAckNo == self.que[0].cumAckNo, "ERROR: In ACK pool, element ACKNO != que[0] ACKNO"
            Queue.enQueue(self, element)
        else:
            print("Fast Retransmission didn't happen")

    def cleanQueue(self):
        del self._que[:]

####################################################################

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
