import random

from BasicTest import *

"""
This tests random packet drops. We randomly decide to drop about half of the
packets that go through the forwarder in either direction.

Note that to implement this we just needed to override the handle_packet()
method -- this gives you an example of how to extend the basic test case to
create your own.
"""
class SingleDropTest(BasicTest):
	appearance = 0
	def handle_packet(self):
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)
         #    print(p)
        	# msg_type, seqno, data, checksum = self.split_packet(p)
        	# if msg_type == "ack" and seqno == "3" and SingleDropTest.appearance == 0:
        	# 	continue
        	# else:
                # self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []


    # def split_packet(self, message):
    #     pieces = message.split('|')
    #     msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
    #     checksum = pieces[-1] # last is always treated as checksum
    #     data = '|'.join(pieces[2:-1]) # everything in between is considered data
    #     return msg_type, seqno, data, checksum
