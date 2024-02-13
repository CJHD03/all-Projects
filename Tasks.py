# Student: Charles "CJ" Delphias
# Date: 1/30/2024

"""
Implements a Task in the Simulator.

Classes:
    Task extends SimTask

"""

from Globals import Globals
from Threads import Thread
from Memory import PageTable
from Hardware import CPU
from Interrupts import Interrupt
from Files import File, Directory, OpenFileDescriptor
from SimTasks import SimTask
from SimExceptions import SimException
from Devices import Device


class Task(SimTask):
    """
    Implements a Task in the Simulator.

    Functions:
        Class(Static) Functions:
            initTasks(cls)
            create(cls, nonPreemptive) -> Task
            killTask(cls)

        Instance Functions:
            __init__(self, id, user, nonPreemptive) (Constructor)
            kill(self)
            spawn(self)
            __str__(self) -> string
            getId(self) -> int
            getNonPreemptive(self) -> boolean
            getStatus(self) -> Task Status
            getPriority(self) -> int
            getPageTable(self) -> PageTable
            getUser(self) -> User
            getSwapFile(self) -> OpenfileDescriptor

            The following functions are related to maintaining a list of threas:
                getNumThreads(self) -> int
                addThread(self, Thread)
                removeThread(self, Thread)
                getThread(self, id) -> Thread
                getActiveThread(self) -> Thread
                setActiveThread(self, thread)
                getThreadList(self) -> list of threads
            The following functions are related to maintaining a list of open files:
                addOpenFile(self, fileDescriptor)
                removeOpenFile(self, fileDescriptor)
                getOpenFileList(self) -> list of OpenFileDescriptors
    """

    @classmethod
    def initTasks(cls):
        """
        This is a class method that is called at boot time to initialize any class data.

        Parameters:
            None

        Returns:
            None
        """
        # s# This function should:
        #     - Register the class functions create() and killTask() functions
        #       as interrupt handlers for the TaskCreate and ThreadKillInterrupt interrupts.
        Interrupt.registerHandler(Globals.TaskCreate, cls.create)
        Interrupt.registerHandler(Globals.TaskKillInterrupt, cls.killTask)
        Globals.logMessage("Task.initTask(): Interrupt Table: " + Interrupt.interruptTable2String())

    def __init__(self, id, user=None, nonPreemptive=False):
        """
        This is the constructor.

        Parameters:
            id: int
                This will be the task id

            user: User
                This is the user that owns the task

            nonPreemptive: boolean (default is False)
                nonPreemptive means that the task is a high priority task and should not
                be preempted from the CPU once it is running.  Such tasks are Operating
                System tasks that need to do important, although very short, work.  All
                User-level tasks may be preemptive.

        Returns:
            None
        """
        # p# This function should:
        #     - Call the super class constructor passing the same parameters as arguments.
        #     - Initialize instance data (all should be private) for:
        #         * status (initialized to TaskNew)
        #         * id
        #         * user
        #         * non-preemptive status
        #         * priority (-1 if this task is non-preemptive, zero otherwise)
        #         * list of threads (initially empty)
        #         * the next thread number (or id) - This variable is used so that each thread
        #           that is created for this particular task will have a unique id. The first
        #           thread should have an id of zero.
        #         * list of OpenFileDescriptors (initially empty)
        #         * active thread (this is the thread that is currently executing) (initially None)
        #         * PageTable (which should be a new PageTable)
        #         * swap file (which should be an OpenFileDescriptor). Create a swap file by:
        #           + Get the "/swap" directory (see getFullPathFile() in the Directory class)
        #           + Determine the size of the swap file, which should be 2 to the power of the number
        #             of bits in an address (see getNumAddressBits() in the Globals class).
        #           + Get the swap file from the swap directory (see getFileEntry() in the Directory class.
        #             The name of the file same as task id (except that it needs to be a string).
        #           + If the file doesn't exist (i.e. getFileEntry() returns None), then create a new file
        #             with that name and a size that you just calculated above.
        #           + Open the swap file (see open() in the File class).  This will give you an open file descriptor
        #             (which is what you will use for the swap file). (The open file descriptor is the same thing
        #             as a file handle. This is what you used to manipulate a file.)
        #     - Add the swap file to the list of open files.

        super().__init__(id, user, nonPreemptive)
        self.__status = Globals.TaskNew
        self.__id = id
        self.__user = user
        self.__nonPreemptive = nonPreemptive
        if self.__nonPreemptive:
            self.__priority = -1
        else:
            self.__priority = 0
        self.__threadsList = []
        self.__nextThreadNum = 0
        self.__openFileDescriptor = []
        self.__activeThread = None
        self.__pageTable = PageTable(self)

        swapDirectory = File.getFullPathFile("/swap")
        swapFileSize = 2 ** Globals.getNumAddressBits()
        swapFile = Directory.getFileEntry(swapDirectory, str(self.__id))

        # print(swapDirectory) prints /swap
        # print(swapFile) this is printing None 
        self.__swapDirFile = swapDirectory

        if swapFile is None:
            createdSwapFile = Directory.newFile(swapDirectory, str(self.__id), swapFileSize)
            opendedSwapFile = File.open(createdSwapFile, self)
            self.__openFileDescriptor.append(opendedSwapFile)
            self.__swapFile = opendedSwapFile
            # print(createdSwapFile) prints 0
            # print(opendedSwapFile) print OpenFile: 0
        else:
            opendedSwapFile = File.open(swapFile, self)
            self.__openFileDescriptor.append(opendedSwapFile)
            self.__swapFile = opendedSwapFile

    @classmethod
    def create(cls, nonPreemptive=False):
        """
        Creates a new task. This is NOT the constructor.  It is a class or static
        function.  It does, however, call the constructor. This is a system call
        and should only be invoked using a trap.  That is why it is static. Tasks
        should only be created using a trap.

        Parameters:
            nonPreemptive: boolean (default False)
                nonPreemptive means that the task is a high priority task and should not
                be preempted from the CPU once it is running.  Such tasks are Operating
                System tasks that need to do important, although very short, work.  All
                User-level tasks may be preemptive.

        Returns:
            Task
        """
        # r# This function should:
        #     - Make an assertion that the mode is privileged mode. An assertion can be made with
        #       the python keyword "assert" followed by a boolean expression that you expect to be
        #       true. If the boolean expression is not true, then an AssertionException is raised.
        #       You need to assert that the mode is in privileged mode. See the getMode() function in
        #       the Globals class as well as the PrivilegedMode constant.
        #     - Make sure that the number of tasks has not exceeded the maximum number of tasks (see
        #       getNumTasks() in the super class as well as getMaxNumTasks() in the Globals class).
        #       If it has, then set the mode back to user mode (see setUserMode() in the Globals class)
        #       and return None.
        #     - Get the user from register number 6 (see getRegister() in the CPU class).
        #       (The appropriate register is given in the documentation on the Interrupt class.)
        #     - Use the getUniqueTaskId() of the super class to get a unique task id.
        #     - Create a new task (this calls the constructor) with the id, user and
        #       non-preemptive status as parameters
        #     - Use the registerTask() of the super class to register the task with its id.
        #     - Spawn one new thread using your spawn() function below, because the task has to have at
        #       least one thread to execute.
        #     - Set the status of the new task for Globals.TaskReady
        #     - Set the mode back to user mode (see setUserMode() in the Globals class) and return the
        #       new Task

        assert Globals.getMode() == Globals.PrivilegedMode  # bullet p1
        if SimTask.getNumTasks() < Globals.getMaxNumTasks():
            user = CPU.getRegister(6)
            uniqueid = SimTask.getUniqueTaskId()
            newTask = Task(uniqueid, user, nonPreemptive)
            SimTask.registerTask(newTask)
            newTask.spawn()
            newTask.__status = Globals.TaskReady
            Globals.setUserMode()
            return newTask
        else:
            Globals.setUserMode()
            return None

    @classmethod
    def killTask(cls):
        """
        Kills a task. It is a class or static function because it is a system call
        and should only be invoked using a trap.  That is why it is static. Tasks
        should only be killed (including normal termination) using a trap.

        Parameters:
            None

        Returns:
            None
        """
        # i# This function should:
        #     - Assert that the mode is currently in privilege mode. (See the directions above for the
        #       create() function for how to do this.)
        #     - Get the task from the appropriate register (see getRegister() in the CPU class as well as the
        #       documentation on the Interrupt class for the appropriate register).
        #     - If the task is not None, then call the kill() function with the task (using your kill()
        #       function below)
        #     - Set the mode back to user mode (see setUserMode() in the Globals class).
        assert Globals.getMode() == Globals.PrivilegedMode
        taskInRegister = CPU.getRegister(1)
        if taskInRegister is not None:
            taskInRegister.kill()
        Globals.setUserMode()

    def kill(self):
        """
        Kills the task. This function should not be called direction
        from anywhere except the above killTask() function.

        Parameters:
            None

        Returns:
            None
        """
        # n# This function should:
        #     - Call the super class kill()
        #     - Set the status of the task to Globals.TaskKill
        #     - Iterate backwards through the thread list and kill each thread (see the kill() function in
        #       the Thread class).  (Why is it necessary to iterate backwards?) Note that there is a kill()
        #       function in the Thread class that is different that this kill() function. In other words,
        #       there is a difference between killing a thread and killing a task.
        #     - Iterate backwards through the open file list and close each file (see the close() function in
        #       the OpenFileDescriptor class). (Why is it necessary to iterate backwards?)
        #     - Deallocated the pages of the PageTable (see deallocatePages() in the PageTable class)
        #     - Get the swap directory in the same way you did in the constructor.
        #     - Remove the swap file that was created in the constructor (see the rm() function in the
        #       Directory class). (It is not necessary to close the swap file because you just
        #       iterated through the open file list and closed them all. The swap file is among those that
        #       you just closed.)
        SimTask.kill(self)

        self.__status = Globals.TaskKill
        # print("thread list kill?: ", self.__threadsList)
        for i in self.__threadsList[::-1]:
            i.kill()
            # print("i = ", i)

        filesToClose = Task.getOpenFileList(self)
        for i in filesToClose[::-1]:
            OpenFileDescriptor.close(i)

        PageTable.deallocatePages(self.__pageTable)

        self.__swapDirFile.rm(self.__swapFile)  # needs fixing

    def spawn(self):
        """
        Spawns (creates) a new thread.

        Parameters:
            None

        Returns:
            None
        """
        # g# This function should:
        #     - Call the super class spawn()
        #     - If the number of threads has not exceeded the maximum number of
        #       threads allowed (see getMaxNumThreads() in the Globals class), then:
        #           * Create a new thread and with the nextThreadNum (the instance variable you created in the
        #             constructor) and the same non-preemptive status of this task.
        #           * Add this new thread to the list of threads
        #           * Increment the nextThreadNum
        #             (Note that you are using the instance variable nextThreadNum to give each thread a unique
        #             thread id.  Since a task could have 100 threads (hopefully not), and they all need to
        #             have a unique id, you use this variable to give each new thread a new number.)
        #           * Set the flag to reschedule (see setRescheduleNeeded() in the Globals class) because spawning
        #             a new thread is an opportunity to reschedule.

        SimTask.spawn(self)
        if Task.getNumThreads(self) < Globals.getMaxNumTasks():
            newThread = Thread(self.__nextThreadNum, self, self.__nonPreemptive)
            Task.addThread(self, newThread)
            self.__nextThreadNum += 1
            Globals.setRescheduleNeeded()
        else:
            pass

    def __str__(self):
        """
        Returns string representation of a task (suitable for printing).

        Parameters:
            None

        Returns:
            A string representation of a task: string
        """
        # Feel free to modify this if you don't like the way tasks are printing.
        return "Task " + str(self.getId()) + "(" + self.getPrettyStatus() + ")"

    def getId(self):
        """
        Gets the id of the task.

        Parameters:
            None

        Returns:
            id: int
        """
        return self.__id

    def getNonPreemptive(self):
        """
        Indicates whether the task is non-preemptive.  Non-preemptive means that it is a critical task
        (e.g. an O/S task or a real-time task) and therefore should not be preempted from the CPU.

        Parameters:
            None

        Returns:
            non-preemptive: boolean
        """
        return self.__nonPreemptive

    def getStatus(self):
        """
        Gets the status of the task.

        Parameters:
            None

        Returns:
            status: int
        """
        return self.__status

    def getPriority(self):
        """
        Gets the priority of the task.

        Parameters:
            None

        Returns:
            priority: int
        """
        return self.__priority

    def getPageTable(self):
        """
        Gets the page table for this task.

        Parameters:
            None

        Returns:
            pageTable: PageTable
        """
        return self.__pageTable

    def getUser(self):
        """
        Gets the user for this task

        Parameters:
            None

        Returns:
            user: User
        """
        return self.__user

    def getSwapFile(self):
        """
        Gets the swap file for this task. Note that this is an OpenFileDescriptor, not a File.
        Therefore, it is already opened and can be read or written to without any other processing.

        Parameters:
            None

        Returns:
            swap file: OpenFileDescriptor
        """

        return self.__swapFile

    def getNumThreads(self):
        """
        Returns the number of threads.

        Parameters:
            None

        Returns:
            Number of threads: int
        """
        return self.__nextThreadNum

    def addThread(self, thread):
        """
        Adds a thread to the list of threads.

        Parameters:
            thread: Thread

        Returns:
            None
        """
        self.__threadsList.append(thread)

    def removeThread(self, thread):
        """
        Removes a thread from the list of threads.

        Parameters:
            thread: Thread

        Returns:
            None
        """
        # 2# This function should:
        #     - Depending on the data structure used for the list of threads, if you call
        #       remove() (not this function) on the list, it might raise an exception if the thread
        #       is not in the list. Such an exception should be ignored, because this function should
        #       NOT raise an exception.
        #     - If the thread being removed is the active thread, then set the
        #       active thread to None.
        #     - Remove the thread from the list of threads
        # print(f"thread to remove = {thread}")
        try:
            activeThread = self.__activeThread
            if thread is activeThread:
                # print("setting active to NONE in remove thread", self.__threadsList.index(thread), thread)
                self.__activeThread = None
            self.__threadsList.remove(thread)
            # print(f"{thread} has been removed")
        except:
            pass
        # print("thread list: ", self.__threadsList)

    def getThread(self, id):
        """
        Gets a thread (using its id) from the list of threads

        Parameters:
            id: int

        Returns:
            The thread from the list of threads that has a thread id given as a parameter
            or returns None.
        """
        # 0# This function should:
        #     - Iterate over the list of threads until you find the one that has a thread id
        #       that matches the parameter.
        #     - return None if there is no such thread.

        for x in self.__threadsList:
            if x.getId() == id:
                return x
        # print("returning None")
        return None

    def getActiveThread(self):
        """
        Returns the active thread for the task. The "active" thread is the thread
        of a task that is the one currently executing.

        Parameters:
            None

        Returns:
            The active thread or None
        """
        return self.__activeThread

    def setActiveThread(self, thread):
        """
        Sets the active thread for the task. The "active" thread is the thread
        of a task that is the one currently executing. If the thread is not in
        the task's list of threads, then it raises a SimException.

        Parameters:
            thread: Thread

        Returns:
            None
        """
        # 2# This function should:
        #     - If the parameter is None, then set the current thread to None
        #     - Otherwise, check to make sure the thread is in the list of threads
        #         * If it is, then set the current thread to the parameter
        #         * If it is not, then raise an exception. The message of the SimException is up to you,
        #           but it should be descriptive enough. In other words, if you don't give enough of a
        #           description of the error for someone to know what when wrong, then I will deduct points.

        # for x in self.__threadsList:
        #     print("thread in list:", x)

        if thread is None:
            self.__activeThread = None
        elif thread is not None:
            # print(thread)
            if thread in self.__threadsList:
                # print("thread is in list")
                self.__activeThread = thread
            else:
                raise Exception(f"SimException: Thread DNE in List: {thread}")

    def getThreadList(self):
        """
        Gets the thread list. (The entire list)

        Parameters:
            None

        Returns:
            The list of threads
        """
        return self.__threadsList

    def addOpenFile(self, fileDescriptor):
        """
        Adds an open file descriptor to the list of open files if it is not
        already in the list. A task should not open the same file twice.

        Parameters:
            fileDescriptor: OpenFileDescriptor

        Returns:
            None
        """
        # 4# This function should:
        #  - Check to see if the open files is already in the list of open files.
        #  - If not, then add it.

        if fileDescriptor not in self.__openFileDescriptor:
            self.__openFileDescriptor.append(fileDescriptor)
        else:
            pass

    def removeOpenFile(self, fileDescriptor):
        """
        Removes an open file from the list of open files.

        Parameters:
            None
        Returns:
            None
        """
        # # This function should:
        #     - Remove the open file from the list of open files.
        #     - Depending on the data structure used for the list of files, if you call
        #       remove() (not this function) on the list, it might raise an exception if the open file
        #       is not in the list. Such an exception should be ignored, because this function should
        #       NOT raise an exception.

        try:
            self.__openFileDescriptor.remove(fileDescriptor)
        except:
            pass

    def getOpenFileList(self):
        """
        Returns the list of open files (the entire list)

        Parameters:
            None

        Returns:
            list of open files: list
        """
        return self.__openFileDescriptor
