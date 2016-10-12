# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

'''
    This file has been prepared to iterate by all the generalised parameters
    to check its correctness.
'''


from datetime import datetime
import multiprocessing
from optparse import OptionParser
from random import randint
from GeneralizedRijndael import GeneralizedRijndael
from GeneralizedRijndael.Logger import levelFromMeaning as _levelFromMeaning
import traceback


def prepareSingleTest(nTests, logLevel,
                      nRounds, nRows, nColumns, wordSize, nKeyColumns):
    print("nRounds = %d, nRows = %d, nColumns = %d, wordSize = %d, "
          "nKeyColumns = %d"
          % (nRounds, nRows, nColumns, wordSize, nKeyColumns))
    queue = multiprocessing.Queue()
    queue.put([nRounds, nRows, nColumns, wordSize, nKeyColumns])
    doTest(queue, nTests, logLevel)


def prepareMultipleTest(parallel, processors, nTests, logLevel):
    def write2File(msg):
        with open(fileName, 'a') as f:
            f.write("%s\t%s" % (datetime.now().isoformat(), msg))
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = "%s_MultiprocessingTest.log" % (now)
    queue = multiprocessing.Queue()
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(2, 17):
                blockSize = nRows*nColumns*wordSize
                # TODO: discard too small sizes for keys
                for nKeyColumns in range(2, 8):
                    keySize = nRows*nKeyColumns*wordSize
                    # TODO: discard too small number of rounds
                    # for nRounds in range(1, 40):
                    nRounds = max(nKeyColumns, nColumns) + 6
                    queue.put([nRounds, nRows, nColumns, wordSize,
                               nKeyColumns])
    write2File("preparing %s tests" % queue.qsize())
    if parallel:
        doParallelTest(processors)
    else:
        while not queue.empty():
            doTest(queue, nTests, logLevel)


def doTest(queue, nTests, logLevel):
    while not queue.empty():
        nRounds, nRows, nColumns, wordSize, nKeyColumns = queue.get()
        blockSize = nRows*nColumns*wordSize
        keySize = nRows*nKeyColumns*wordSize
        k = randint(0, 2**keySize-1)
        g = GeneralizedRijndael(k, nRounds, nRows, nColumns, wordSize,
                                nKeyColumns, loglevel=logLevel)
        g.log2file = True
        g.fileSuffix = "%d,%d,%d,%d,%d"\
                       % (nRounds, nRows, nColumns, wordSize, nKeyColumns)
        # loop to do nTests
        tested = []
        for i in range(nTests):
            testBlock = randint(0, 2**blockSize-1)
            while testBlock in tested:
                testBlock = randint(0, 2**blockSize-1)
            cipheredBlock = g.cipher(testBlock)
            if testBlock != g.decipher(cipheredBlock):
                break


def doParallelTest(processors):
    def buildWorker(id):
        return multiprocessing.Process(target=doTest, name=str("%d" % (id)),
                                       args=(queue, nTests, logLevel))
    maxParallelprocesses = multiprocessing.cpu_count()
    if processors is None or processors == 'max':
        processors = maxParallelprocesses
    else:
        processors = int(processors)
        if processors < 0:
            processors = maxParallelprocesses + processors
    workersLst = []
    for k in range(processors):
        workersLst.append(buildWorker(k))
    for w in workersLst:
        w.start()


def extractParams(paramsStr):
    paramsSet = paramsStr.split(',')
    if len(paramsSet) not in [4, 5]:
        raise Exception("Cannot extract the test parameters using %r"
                        % paramsStr)
    nRounds = int(paramsSet[0])
    nRows = int(paramsSet[1])
    nColumns = int(paramsSet[2])
    wordSize = int(paramsSet[3])
    try:
        nKeyColumns = int(paramsSet[4])
    except:
        nKeyColumns = int(paramsSet[2])
    return (nRounds, nRows, nColumns, wordSize, nKeyColumns)


def arginOptions(parser):
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                      "{error,warning,info,debug,trace}.")
    parser.add_option('', "--test-all", action="store_true",
                      help="Do a iterative test of all the generalised "
                      "parameters.")
    parser.add_option('', "--test", type='str',
                      help="Comma separated set of Rijndael's generalised"
                      "parameters. For example from the original Rijndael: "
                      "10,4,4,8 for 128, or 12,4,4,8,6 for 192 or "
                      "14,4,4,8,8 for 256 "
                      "(nRounds, nRows, nColumns, wordSize[, nKeyColumns])")
    parser.add_option('', "--parallel-processing", action="store_true",
                      help="Only valid when test many combinations, "
                      "launch each of them using multiprocessing.")
    parser.add_option('', "--processors", type="str",
                      help="In case of parallel processing, it can be "
                      "specified the number of parallel jobs to be working. "
                      "With the string 'max' the program will use all the "
                      "available cores. A positive number of them will force "
                      "this number of parallel jobs in execution, and a "
                      "negative number will decrease from the maximum of "
                      "available")
    parser.add_option('', "--max-tests", type="int",
                      help="Tell the test procedure to execute, as maximum, "
                      "the given number of checks")


def main():
    parser = OptionParser()
    arginOptions(parser)
    (options, args) = parser.parse_args()
    logLevel = _levelFromMeaning(options.loglevel)
    if options.test is not None:
        parameters = extractParams(options.test)
        prepareSingleTest(options.max_tests, options.loglevel, *parameters)
    elif options.test_all is not None:
        prepareMultipleTest(options.parallel_processing, options.processors,
                            options.max_tests, options.loglevel)
    else:
        print("\n\tNo default action, check help to know what can be done.\n")

if __name__ == "__main__":
    main()
