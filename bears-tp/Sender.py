import sys
import getopt

import Checksum
import BasicSender


# Global Constant
CUMACK = 0
SACK = 1
TIMEOUT_CONSTANT = 0.5
MAX_BUFFER_PACKETS = 20
MAX_PACKET_SIZE = 1440    # 1472 - 32
MAX_WINDOW_SIZE = 5

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        # File Spliter and put all packet into packetPool
        # initial first 5 packet to window
        # put first 5 packets to sendingQueue
        self.packetPool = PacketPool(filename, self)
        self.window = Window()
        self.sendingQueue = SendQueue()
        self.ackPool = AckPool()
        self.initialComponentLoad()
        if sackMode:
            self.mode = SACK
        else:
            self.mode = CUMACK

    def initialComponentLoad(self):
        count = 0
        while self.window.size() < MAX_WINDOW_SIZE and not self.packetPool.isEmpty():
            packet = self.packetPool.deQueue()
            self.sendingQueue.enQueue(packet)
            self.window.enQueue(self.windowElementGenerator(packet))

    # Main sending loop.
    def start(self):
        tmp = 1
        while not self.window.isEmpty():
            # print(self.window)
            
            # print("Round: " + str(tmp))
            # print("--- Sending out ---")
            while not self.sendingQueue.isEmpty():
                sendingPacket = self.sendingQueue.deQueue()
                self.send(sendingPacket)
                # print(sendingPacket)
                # msg_type, seqno, data, checksum = self.split_packet(sendingPacket)
                # print msg_type, '***', seqno
                # print(self.split_packet(sendingPacket)[0:2])

            response = self.receive(TIMEOUT_CONSTANT)
            # print("---- receive ACK---")
            # print(response)
            # print(" ")

            if response == None:
                self.handle_timeout()
            else:
                self.handle_response(response)
            tmp += 1

    def handle_timeout(self):
        if self.mode == CUMACK:
            self.sendingQueue.extendQueue(self.window.getAllPackets())
        else:
            self.sendingQueue.extendQueue(self.window.getUnACKPackets())

    # [Add]: Handles a response from the receiver.
    def handle_response(self, response_packet):
        if Checksum.validate_checksum(response_packet):
            internalACKPacket = self.internalACKPacketGenerator(response_packet)
            if internalACKPacket.getMsgtype() == 'ack' and self.window.validateAckPacket(internalACKPacket):
                self.handle_cum_ack(internalACKPacket)
            elif internalACKPacket.getMsgtype() == 'sack'and self.window.validateAckPacket(internalACKPacket):
                self.handle_sack_ack(internalACKPacket)
        else:
            print('checksum drop or Window does not contain seqno')

    # [add]: Handle selective ACKs.
    def handle_sack_ack(self, internalACKPacket):
        for each_sAck in internalACKPacket.getSack():
            self.window.setIsAcked(each_sAck)
        self.handle_cum_ack(internalACKPacket)

    # [add]: Handle general incoming cumulative ACKs.
    # Start from here ..........................................
    def handle_cum_ack(self, internalACKPacket):
        ack_seqno = internalACKPacket.getCumAckNo()
        if self.ackPool.largestAckSoFar() == ack_seqno:
            self.handle_dup_ack(ack_seqno)
        elif self.ackPool.largestAckSoFar() < ack_seqno:
            self.handle_new_ack(ack_seqno)

    # ack_seqno - a integer that represent a ack sequence number
    def handle_new_ack(self, ack_seqno):
        self.ackPool.cleanQueue()
        self.ackPool.enQueue(ack_seqno)
        space = self.window.processAck(ack_seqno)
        # print("space" + str(space))
        while space > 0 and not self.packetPool.isEmpty():
            tmp_packet = self.packetPool.deQueue()
            self.sendingQueue.enQueue(tmp_packet)
            # print("window Size" + str(self.window.size()))
            # print("tmp_packet:" + tmp_packet)
            self.window.enQueue(self.windowElementGenerator(tmp_packet))
            space -= 1

    def handle_dup_ack(self, ack_seqno):
        if self.ackPool.size() == 3:
        # implement fast retransmit
            self.ackPool.cleanQueue()
            if self.mode == CUMACK:
                packet = self.window.locatePacket(ack_seqno)
                self.sendingQueue.enQueue(packet)
            else:
                self.sendingQueue.extendQueue(self.window.getUnACKPackets())
        elif self.ackPool.size() < 3:
            self.ackPool.enQueue(ack_seqno)
        else:
            print("error, current ackPool size more than 3")

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
        self._msg_type = msg_type
        self._sAcks = []
        if self._msg_type == 'sack':
            tmp = seqnoStr.split(';')
            self._cumAckNo = int(tmp[0])
            if len(tmp[1]) != 0:
                tmpStrLst = tmp[1].split(',')
                for el in tmpStrLst:
                    self._sAcks.append(int(el))
        else:
            self._cumAckNo = int(seqnoStr)

    def getMsgtype(self):
        return self._msg_type

    def getCumAckNo(self):
        return self._cumAckNo

    def getSack(self):
        return self._sAcks

class WindowElement(object):
    def __init__(self, packet, seqno):
        self._packet = packet
        self._seqno = int(seqno)
        self._isAcked = False

    def setAcked (self):
        self._isAcked = True

    def seqno(self):
        return self._seqno

    def isAcked(self):
        return self._isAcked

    def getPacket(self):
        return self._packet

#####################################################

################## Data Structure and Interface ####################

class Queue(object):
    def __init__(self):
        self._que = []

    def deQueue(self):
        if not self.isEmpty():
            return self._que.pop(0)
        else:
            print("que is isEmpty")

    def enQueue(self, element):
        self._que.append(element)

    def isEmpty(self):
        return len(self._que) == 0

    def size(self):
        return len(self._que)

# Packet Pool
class PacketPool(Queue):
    def __init__(self, filename, sender):
        Queue.__init__(self)
        self._sizeLimit = MAX_BUFFER_PACKETS
        self.filename = filename
        self.finished = False
        self.sender = sender
        self.seqno = 0

        try:
            if self.isEmptyfile():
                self._filePtr = sys.stdin
                # print("empty filename")
                # print(self._filePtr.read())
            else:
                self._filePtr = open(self.filename, 'r')
            self.initialLoad()
        except IOError:
            print(filename + "doesn't exist")
    
    def deQueue(self):
        return_packet = Queue.deQueue(self)
        if not self.finished:
            content = self._filePtr.read(MAX_PACKET_SIZE)
            # print(content)
            if len(content) == 0:
                self.finish_load()
            else:
                packet = Sender.make_packet(self.sender, 'data', self.seqno, content)
                self.enQueue(packet)
                self.seqno += 1
        return return_packet

    def initialLoad(self):
        self.seqno = 0
        self.enQueue(Sender.make_packet(self.sender, 'start', self.seqno, ""))
        self.seqno += 1
        content = self._filePtr.read(MAX_PACKET_SIZE)
        while self.size() < self._sizeLimit and len(content) != 0:
            packet = Sender.make_packet(self.sender, 'data', self.seqno, content)
            self.enQueue(packet)
            if self.size() < self._sizeLimit:
                content = self._filePtr.read(MAX_PACKET_SIZE)
            self.seqno += 1
        if len(content) == 0:
            self.finish_load()
            
    def finish_load(self):
        if not self.isEmpty():
            self.finished = True
            self._filePtr.close()
            tail = self._que.pop(-1)
            msg_type, seqno, data, checksum = Sender.split_packet(self.sender, tail)
            packet = Sender.make_packet(self.sender, 'end', int(seqno), data)
            self.enQueue(packet)

    def isEmptyfile(self):
        tmpPtr = open(self.filename, 'r')
        length = len(tmpPtr.read())
        tmpPtr.close()
        return length == 0

    def handle_empty_file(self):
        tmpPtr = open(self.filename, 'w')
        tmpPtr.write(raw_input(">"))
        tmpPtr.close()
        tmpPtr = open(self.filename, 'r')
        return tmpPtr
        
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
                unAckLst.append(winElt.getPacket())
        return unAckLst

    def getAllPackets(self):
        allPacket = []
        for winElt in self._que:
            allPacket.append(winElt.getPacket())
        return allPacket
    
    def processAck(self, cumAckNo):
        removeList = []
        for winElt in self._que:
            if winElt.seqno() < cumAckNo:
                removeList.append(winElt)
        space = 0
        for winElt in removeList:
            # print("Queue Rmove" + str(winElt.seqno()))
            self._que.remove(winElt)
            space += 1;
        return space

    def locatePacket(self, ack_seqno):
        for elem in self._que:
            if elem.seqno() == ack_seqno:
                return elem.getPacket()

    def setIsAcked(self, ack_seqno):
        for elem in self._que:
            if elem.seqno() == ack_seqno:
                elem.setAcked()

    def validateAckPacket(self, internalACKPacket):
        valid = True
        seqnoInWindow = []
        largestSeqno = -1
        for elem in self._que:
            if largestSeqno < elem.seqno():
                largestSeqno = elem.seqno()
            seqnoInWindow.append(elem.seqno())
        if (not internalACKPacket.getCumAckNo() in seqnoInWindow) and internalACKPacket.getCumAckNo() != largestSeqno + 1:
            valid = False
        if internalACKPacket.getMsgtype() == 'sack' and len(internalACKPacket.getSack()) != 0:
            for sackno in internalACKPacket.getSack():
                if not sackno in seqnoInWindow:
                    valid = False
        return valid

    def __str__(self):
        inWindow = []
        for elem in self._que:
            inWindow.append((elem.seqno(), elem.isAcked()))
        return str(inWindow)

# sending queue class
class SendQueue(Queue):
    def extendQueue(self, lst):
        if lst != None and len(lst) != 0:
            self._que.extend(lst)
        else:
            print("lst is None or isEmpty")

# ack pool class
class AckPool(Queue):
    def __init__(self):
        Queue.__init__(self)
        self._largestAckSoFar = -1

    def largestAckSoFar(self):
        return self._largestAckSoFar

    def enQueue(self, element):
        if element > self._largestAckSoFar:
            self._largestAckSoFar = element
        if type(element) == int and self.size() < 4:
            if not self.isEmpty():
                assert element == self._que[0], "ERROR: In ACK pool, element ACKNO != que[0] ACKNO"
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
