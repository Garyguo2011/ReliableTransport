algorithm
sendingQueue - store packet that wait to be send
# packetPool - a list that store all of packetsd

sendPacketBuffer 
receivePacketBufer

def start():
	while not_send_all_packet:
		while not sendingQueue.isEmpty:
			self.send(sendingQueue.dequeue());
		response = self.receive()
		self.handle_response(response)

def windowElementGenerator(self, packet):
	msg_type, seqno, data, checksum = self.split_packet(packet)
	return WindowElement(packet, seqno)

def internalACKPacketGenerator(self, packet):
	msg_type, seqno, data, checksum = self.split_packet(packet)
	return InternalACKPacket(msg_type, seqno)

class InternalACKPacket(object):
	def __init__(self, msg_type, seqnoStr):
		self.msg_type = msg_type
		if msg_type = 'sack':
			tmp = seqnoStr.split(';')
			self.cum_ack = tmp[0]
			self.sack = tmp[1].split(',')
		else:
			self.cum_ack = seqnoStr
			self.sack = ()

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
		return self.isAcked
		
class AckPool(Queue):
	def enQueue(self, element):
		if type(element) == InternalACKPacket and self.size() < 4:
			Queue.enQueue(self, element)
		else:
			print("Fast Retransmission didn't happen")

	def cleanQueue(self, element):
		del self._que[:]

class SendQueue(Queue):
	def extendQueue(self, lst):
		if lst != None and len(lst) != 0:
			self._que.extendQueue(lst)
		else:
			print("lst is None or isEmpty")

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