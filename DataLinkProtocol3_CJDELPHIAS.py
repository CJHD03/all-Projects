# Author: Clayton S. Ferner
# Edited for lab5 by: CJ Delphias
# Date: 9/12/2023
# Edited by CJ: 9/19/2023
# Description: This program demonstrates the Data Link protocol 1-3.
# These protocols are simplex, meaning that we have data being transmitted
# one-way, although acknowledgements are sent back on the reverse channel.
# The physical layer can be configured to drop frames at a given rate, produce
# 1-bit errors at a certain rate, or do a utopian channel, were everything
# works perfectly.
#
# The packets contain ASCII characters, which are 7-bits.  The extra bit,
# The highest order bit, will be used to add even-parity to the byte. The
# receiver runs a check of the parity as well as clears that extra bit.


# The threading module is needed to do multi-threading
from threading import Thread, Semaphore, Timer
from Event import Event
from Frame import Frame
from PhysicalLayer import PhysicalLayer
from NetworkLayer import NetworkLayer
import random
import time
import sys
import os


class DataLinkLayer:
    def __init__(self, N=10, Max_seq=2, errorRate=0.0, droppedPacketRate=0.0, timeout=10, name=""):
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
        self.__eventFull = Semaphore(0)  # How many events are in the queue

        # We need to have access to the Physical Layer as well as the Network Layer.
        self.__physicalLayer = PhysicalLayer(Max_seq, errorRate, droppedPacketRate)
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

    def computeCheckSum(self, packet):
        '''
        Computes the parity for each character in the packet.  The packet is assumed to
        be a string of ASCII characters. ASCII characters are 7-bits.  This means that the
        most-significant bit of each character is a zero.  This function will compute the
        parity, then set the most-significant bit to a one (or not) to make sure that the
        parity of the byte is even parity.  This transforms the ASCII character into a
        unicode character.

        :param: packet: string: a string of ASCII characters, which must be between 0 and 128.
        :return: string: a string of Unicode characters between 0 and 256.
        '''

        # packet is a string of 7-bit ASCII characters
        # Convert the string to a list of integers
        listOfBytes = []
        for c in packet:
            listOfBytes.append(ord(c))

        # Count the number of 1's in the binary representation (bit_count())
        # and it it is odd, then add a 1 to the left-most bit.  We can use
        # the left-most bit because ASCII only uses the lest significant 7 bits
        # of the byte.  The most-significant is not used.  This would be 2**7 or 128.
        for i in range(len(listOfBytes)):
            sum = listOfBytes[i].bit_count()
            if sum % 2 == 1:
                listOfBytes[i] = listOfBytes[i] | 2 ** 7  # 10000000

        # Convert back to a string, which would not be unicodes.
        newPacket = ""
        for b in listOfBytes:
            newPacket += chr(b)
        return newPacket
        # return packet

    def verifyCheckSum(self, packet):
        '''
        Computes the parity for each character in the packet.  If the parity of any byte
        is odd, the return an error.

        If all bytes are even parity, then convert (and return) the packet back to a string
        of ASCII characters. ASCII characters are 7-bits.  This means that the
        most-significant bit of each character is a zero.

        :param: packet: string: a string of Unicode characters, where the most-significant bit
            is the parity.
        :return: boolean,string tuple: an error and a string of Unicode characters between 0 and 256.
        '''
        error = False

        # If we have an empty packet, then it isn't a parity error.
        if packet == "":
            return False, ""

        # packet is a string of 8-bit unicode characters
        # Convert the string to a list of integers
        listOfBytes = []
        for c in packet:
            listOfBytes.append(ord(c))

        # Count the number of 1's in the binary representation (bit_count())
        # and it it is odd, it's an error because we are using even parity.
        # the left-most bit because ASCII only uses the lest significant 7 bits
        # of the byte.  The most-significant is not used.  This would be 2**7 or 128.
        for i in range(len(listOfBytes)):
            sum = listOfBytes[i].bit_count()
            if sum % 2 == 1:
                error = True
                # print("checksum error with packet = " + str(packet))
                return error, packet
            # Make the most significant bit a zero again to convert from an 8-bit
            # unicode back to 7-bit ASCII.
            listOfBytes[i] = listOfBytes[i] & (2 ** 7 - 1)  # 01111111

        # Convert back to a string, which would not be ASCII.
        newPacket = ""
        for b in listOfBytes:
            newPacket += chr(b)
        return False, newPacket

    def sender(self, name):
        '''
        Sends n frames to the receiver, where each frame is a packet that comes from the
        network layer. Frames are expected to be acknowledged. A timer is set so that if
        the frame is not acknowledged (either not received or received in error), then
        retransmit the frame.
        :param name: string: just a name for debugging purposes.
        :return: None
        '''
        sentCompleteData = ""
        next_frame_to_send = 0

        try:
            done = False
            EOTsent = False
            EOTreceived = False

            while not done:
                packet = self.__networkLayer.from_network_layer()

                if packet == "":
                    print(name + " Empty packet, Stopping ")
                    outFrame = Frame(type=Frame.eot, payload=packet)
                    EOTsent = True
                    done = True

                else:
                    packetWcheckSum = self.computeCheckSum(packet)
                    outFrame = Frame(type=Frame.data, payload=packetWcheckSum)
                    sentCompleteData += packetWcheckSum + "\n"

                outFrame.setSeq(next_frame_to_send)
                print(name + " sending frame " + str(outFrame) + " ")
                self.__physicalLayer.to_physical_layer(outFrame)

                if not done:
                    self.__timer = Timer(self.__timeout, self.addTimeoutEvent())
                    self.__timer.start()
                    print("Waiting for ACK frame \n")

                    event = self.wait_for_event()

                    if event.getType():
                        inFrame = self.__returnDataLink.__physicalLayer.from_physical_layer()
                        if inFrame.getAck() == next_frame_to_send:                   # this line causes errors sometimes
                            self.__timer.cancel()
                            packet = self.__networkLayer.from_network_layer()
                            print(" Resent Frame ")
                            next_frame_to_send = (next_frame_to_send + 1) % self.__MAX_SEQ

                    print("ACK Frame Arrived")

        except ConnectionError:
            print(name + " Connection lost")
        print(name + " sent data: \n" + str(sentCompleteData))

    def receiver(self, name):
        '''
        Receives n frames from the sender, where each frame contains a packet.  Then the packet
        is sent up to the network layer. Each frame must be acknowledged. If a frame has a
        checksum error, then it is not acknowledged, so that it can be resent.
        :param name: string: just a name for debugging purposes.
        :return: None
        '''

        receivedCompData = ""
        try:
            frame_expected = 0
            done = False

            while not done:
                self.wait_for_event()
                inFrame = self.__returnDataLink.__physicalLayer.from_physical_layer()

                if inFrame.getSeq() == frame_expected:
                    if inFrame.getType() == Frame.eot:
                        error = False
                        done = True

                    else:
                        packetWcheckSum = inFrame.getPayload()
                        error, packet = self.verifyCheckSum(packetWcheckSum)
                        receivedCompData += packet + "\n"
                        print("error True Message: " + str(packet))

                        if not error:
                            if not done:
                                self.__networkLayer.to_network_layer(packet)
                            frame_expected = (frame_expected + 1) % self.__MAX_SEQ

                # if inFrame.getAck() == Frame.ack:
                ackFrame = Frame(type=Frame.ack, ack=inFrame.getSeq())
                self.__physicalLayer.to_physical_layer(ackFrame)
                print("ACK frame sent " + str(ackFrame) + "\n")  # I put this here for neatness in the output
                print(name + " received frame = " + str(inFrame) + " ")

            self.__physicalLayer.disconnect()
            self.__returnDataLink.__physicalLayer.disconnect()

        except ConnectionError:
            print(name + " connection lost")
        print(name + " received date: \n" + str(receivedCompData))

    def addTimeoutEvent(self):
        '''
        Adds a timeout event.  This is called by the timer automatically after the timeout
        period has expired.
        :param: None
        :return: None
        '''

        if self.__timer is not None:
            self.__timer.cancel()

        # Don't put in multiple timeout events.  One is sufficient.
        for event in self.__eventQueue:
            if event.getType() == Event.timeout:
                return

        self.__eventQueue.append(Event(Event.timeout))
        print(self.__name + " addTimeoutEvent, eventQueue = ", self.__eventQueue)
        self.__eventFull.release()


def main(argv):
    # The seed is printed to the console first. If you want to run the program again
    # with the same sequence of events, you can run the program with the -s option
    # providing the seed.  For example:
    #   python3 DataLinkProtocol3.py -s 563818617

    seed = 0
    if len(argv) > 2 and argv[1] == "-s":
        seed = float(argv[2])
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

    # We have to have two datalinks so that the receiver can send back packets
    # to acknowledge frames.
    numLinks = 2

    # Create the DataLink
    dataLinks = []
    for i in range(numLinks):
        dataLinks.append(DataLinkLayer(N=numOfIterations, Max_seq=2,
                                       errorRate=0.0, droppedPacketRate=0.0, timeout=5,
                                       name="Sender " + str(i)))

    # The return link is so that the physical layer can put frame_arrival events
    # on the return link.
    for i in range(numLinks):
        dataLinks[i].setReturnLink(dataLinks[1 - i])

    # Create threads that will be concurrent senders
    for i in range(numSenders):
        senders.append(Thread(target=dataLinks[i].sender, args=("Sender " + str(i),)))

    # Create threads that will be concurrent senders
    for i in range(numReceivers):
        receivers.append(Thread(target=dataLinks[1 - i].receiver, args=("Reciever " + str(i),)))

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
