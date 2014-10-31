import random

from BasicTest import *

"""
This tests random pick the the packet from in_queue to corrupt its checksum, the sender
should treat it as being randomly dropped.
"""
class SackDataCorruptionTest(BasicTest):
	# def __init__(self, forwarder, input_file):
 #        super(SackRandomDropTest, self).__init__(forwarder, input_file, sackMode = True)

    def handle_packet(self):

    	
        for p in self.forwarder.in_queue:
            
            if random.choice([True, False]):

                p.update_packet(None, None, 'bao bao is a big fool, do not change it', update_checksum=False)
            self.forwarder.out_queue.append(p)
        # empty out the in_queue
        self.forwarder.in_queue = []