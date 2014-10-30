import random

from BasicTest import *

"""
This tests random pick the the packet from in_queue to corrupt its checksum, the sender
should treat it as being randomly dropped.
"""
class DataCorruptionTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            
            if random.choice([True, False]):

                p.update_packet(None, None, 'xu he is a big fool', update_checksum=False)
            self.forwarder.out_queue.append(p)
        # empty out the in_queue
        self.forwarder.in_queue = []