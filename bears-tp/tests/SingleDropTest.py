import random

from BasicTest import *

"""
This tests random pick the the packet from in_queue to corrupt its checksum, the sender
should treat it as being randomly dropped.
"""
class SingleDropTest(BasicTest):
    appearance = 0
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            msg_type, seqno, data, checksum = self.split_packet(p.full_packet)
            if msg_type == 'ack' and seqno == '3' and SingleDropTest.appearance == 0:
                print('here')
                SingleDropTest.appearance = SingleDropTest.appearance + 1
                continue
                
            else:
                self.forwarder.out_queue.append(p)
        # empty out the in_queue
        self.forwarder.in_queue = []


    def split_packet(self, message):
        # print('here')
        pieces = message.split('|')

        msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
        checksum = pieces[-1] # last is always treated as checksum
        data = '|'.join(pieces[2:-1]) # everything in between is considered data

        return msg_type, seqno, data, checksum


    def make_packet(self,msg_type,seqno,msg,checksum):
        packet = "%s|%d|%s|%d" % (msg_type,seqno,msg,checksum)
        # checksum = Checksum.generate_checksum(body)
        # packet = "%s%s" % (body,checksum)
        return packet
  