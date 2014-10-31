import random

from BasicTest import *

"""
This tests random pick the the packet from in_queue to corrupt its checksum, the sender
should treat it as being randomly dropped.
"""
class Msg_TypeCorruptionTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            
            if random.choice([True, False]):
            	msg_type, seqno, data, checksum = self.split_packet(p.full_packet)
            	if msg_type == 'ack':
                	p.update_packet('start', 0, None, None)
                self.forwarder.out_queue.append(p)
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)
        # empty out the in_queue
        self.forwarder.in_queue = []




    def split_packet(self, message):
        pieces = message.split('|')
        msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
        checksum = pieces[-1] # last is always treated as checksum
        data = '|'.join(pieces[2:-1]) # everything in between is considered data
        return msg_type, seqno, data, checksum