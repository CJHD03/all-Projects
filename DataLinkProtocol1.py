# Author: Clayton S. Ferner
# Date: 9/12/2023
# Description: This program demonstrates the Data Link protocol 3.
# This protocol is simplex, meaning that we have data being transmitted
# one-way, although acknowledgements are sent back on the reverse channel.
# This protocol assumes that the network can dropped frames as well
# as introduce 1-bit errors.  The receiver sends back a packet with
# an acknowledgement of the frame that was received. There is a timer,
# so that if we do not receive the acknowledgement within a certain time
# we will retransmit.
#
# The packets contain ASCII characters, which are 7-bits.  The extra bit,
# The highest order bit, will be used to add even-parity to the byte. The
# receiver runs a check of the parity as well as clears that extra bit.
# If the parity is incorrect, the receiver sends back nak, so that the
# sender can retransmit.


# The threading module is needed to do multi-threading
from threading import *
from Event import Event
from Frame import Frame
from PhysicalLayer import PhysicalLayer
from NetworkLayer import NetworkLayer
import random
import time
import sys
import os

class DataLinkLayer:
    def __init__(self, N = 10, Max_seq = 2, errorRate = 0.0, droppedPacketRate = 0.0, timeout = 10, name=""):
        '''
        This is the constructor.
        :param: Max_seq: int: number of sequences numbers to use (default = 2)
        :param: errorRate: float: percent of packets to have a 1-bit error (default 0.0)
        :param: droppedPacketRate: float: percent of packets lost (default 0.0)
        :param: timout: int: number of seconds before a timeout, in which case we retransmit (default 10)
        :param: name: string: used for debugging so that we can prepend each message with an identifier
                             to know which thread produced it.
        :return: None
        '''
        self.__MAX_SEQ = Max_seq
        self.__name = name

        self.__timeout = timeout
        self.__timer = None

        self.__eventQueue = []
        self.__eventFull = Semaphore(0) # How many events are in the queue

        # We need to have access to the Physical Layer as well as the Network Layer
        self.__physicalLayer = PhysicalLayer(Max_seq, errorRate, droppedPacketRate, utopian=True)
        self.__networkLayer = NetworkLayer(N, self.__eventQueue, self.__eventFull)
        self.__returnDataLink = None
    def wait_for_event(self):
        '''
        Wait for an event to occur.  The thread is blocked until an event happens.
        :param: None
        :return: Event
        '''
        self.__eventFull.acquire()
        return self.__eventQueue.pop(0)
    def eventQueue2String(self):
        '''
        Produces a string representation of the event queue for debugging purposes.
        :param: None
        :return: string
        '''
        results = ""
        for i in range(len(self.__eventQueue)):
            results += str(self.__eventQueue[i]) + " "
        # results += "\n semaphore value = " + str(self.__eventFull._value)
        return results
    def setReturnLink(self, datalink):
        '''
        Sets the return datalink, so that the physical layer can add events when a frame arrives.
        :param: DataLinkLayer
        :return: None
        '''
        self.__returnDataLink = datalink
        self.__physicalLayer.setReturnChannel(datalink.__eventQueue, datalink.__eventFull)


    def sender(self, name):
        '''
        Sends n frames to the receiver, where each frame is a packet that comes from the
        network layer.
        :param name: string: just a name for debugging purposes.
        :return: None
        '''
        # These are used to display all the data that was transmitted and received so that we
        # can easily see that the data was exchanged correctly.
        sentCompleteData = ""

        next_frame_to_send = 0

        done = False
        EOTsent = False  # EOT stands for end of transmission
        EOTreceived = False  # EOT stands for end of transmission

        try:
            # If the connection is lost, then just quit

            while not done:

                packet = self.__networkLayer.from_network_layer()

                if packet == "":
                    print(name + " empty packet, stopping")
                    outFrame = Frame(type=Frame.eot, payload=packet)
                    EOTsent = True
                    done = True
                else:
                    sentCompleteData += packet + "\n"
                    outFrame = Frame(type=Frame.data, payload=packet)

                print(name + " sending frame " + str(outFrame))
                self.__physicalLayer.to_physical_layer(outFrame)


            # self.__physicalLayer.disconnect()
            # self.__returnDataLink.__physicalLayer.disconnect()
        except ConnectionError:
            print(name + " Connection Lost")
        print(name + " sent data: \n" + str(sentCompleteData))
    def receiver(self, name):
        '''
        Receives n frames from the sender, where each frame contains a packet.  Then the packet
        is sent up to the network layer.
        :param name: string: just a name for debugging purposes.
        :return: None
        '''
        try:
            # If the connection is lost, then just quit
            receivedCompleteData = ""

            done = False
            while not done:

                event = self.wait_for_event()

                inFrame = self.__returnDataLink.__physicalLayer.from_physical_layer()
                print(name + " received frame = " + str(inFrame))
                if inFrame.getType() == Frame.eot:
                    done = True
                else:
                    packet = inFrame.getPayload()
                    self.__networkLayer.to_network_layer(packet)
                    receivedCompleteData += packet + "\n"

                    # time.sleep(random.randint(1, 2))

            self.__physicalLayer.disconnect()
            self.__returnDataLink.__physicalLayer.disconnect()
        except ConnectionError:
            print(name + " Connection Lost")
        print(name + " received data: \n" + str(receivedCompleteData))


def main(argv):
    seed = 0
    if len(argv) > 2 and argv[1] == "-s":
            seed = float (argv[2])
    else:
        newSeed = os.urandom(4)
        for i in range(len(newSeed)):
            seed = seed << 8
            seed = seed + newSeed[i]

    random.seed(seed)
    print("seed = " + str(seed))

    receivers = []
    senders = []

    numOfIterations = 10
    numSenders = 1
    numReceivers = 1
    numLinks = 2

    # Create the DataLink
    dataLinks = []
    for i in range(numLinks):
        dataLinks.append(DataLinkLayer(N=numOfIterations, Max_seq = 2,
                             errorRate = 0.0, droppedPacketRate = 0.0, timeout = 5,
                                       name="Sender " + str(i)))

    for i in range(numLinks):
        dataLinks[i].setReturnLink(dataLinks[1-i])

    # Create threads that will be concurrent senders
    for i in range(numSenders):
        senders.append(Thread(target=dataLinks[i].sender, args=("Sender " + str(i),)))

    # Create threads that will be concurrent senders
    for i in range(numReceivers):
        receivers.append(Thread(target=dataLinks[1-i].receiver, args=("Reciever " + str(i),)))

    print("Main: staring threads")
    # starting the threads
    for i in range(len(receivers)):
        receivers[i].start()
    for i in range(len(senders)):
        senders[i].start()

    print("Main: threads are running")

    # Wait for threads to finish
    for i in range(len(senders)):
        senders[i].join()

    print("Main: threads are done")

if __name__ == "__main__":
    main(sys.argv)
