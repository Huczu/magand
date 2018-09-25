import sys, os, getopt
import shutil
import csv 
import re
import json
import threading
from timeit import default_timer as timer

inputFilename = ''
outputFoldername = ''
separateFiles = False

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def findHeader(pattern, splittedLine):
    if splittedLine and splittedLine[0] == pattern:
        return True

    return False

def findPattern(file, pattern, skipLinesCount = 0):
    for line in file:
        if re.match(pattern, line) is not None:
            if skipLinesCount > 0:
                skipLines(file, skipLinesCount)
            return True

    return False

def getLineByPattern(file, pattern):
    for line in file:
        if re.match(pattern, line) is not None:
            return line

    return ""

def skipLines(file, lines):
    for i in range(lines):
        next(file)

def removeDuplicatesFromList(arg):
    return list(dict.fromkeys(arg))

def isAnyNumberInArray(array):
    return any(item.replace('.','',1).isdigit() for item in array)

def getShiftedValue(file, pattern):
    shiftedValueLine = getLineByPattern(file, pattern)
    splittedLine = shiftedValueLine.split()
    for line in splittedLine:
        if isfloat(line):
            return float(line)

    return 0.0

def findExpectedDMValues(inputFilename, allValues, element, outputFilename, axis):
    start = timer()
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Property matrix of the DM' + axis + ' operator'
    skilLinesCount = 3
    with open(inputFilename) as file:
        while findPattern(file, pattern, 3):
            for line in file:
                splittedLine = line.split()
                if findHeader('Nr', splittedLine): # found header
                    splittedLine[1:4] = [''.join(splittedLine[1:4])]
                    header += splittedLine
                    row = 0
                    blankLineCount = 0
                elif len(splittedLine) > 1 and isAnyNumberInArray(splittedLine):
                    rowStart = 0
                    if row % 2 == 0:
                        rowStart = 2
                    if len(data) > row:
                        data[row] += splittedLine[rowStart:]
                    else:
                        if rowStart == 0:
                            rowStart = 2
                        else:
                            rowStart = 0
                        data.append(splittedLine)
                        data[row] = ['']*rowStart + data[row]
                    blankLineCount = 0
                    row += 1
                else:
                    blankLineCount += 1
                if blankLineCount == 3: #time to stop
                    count += 1
                    data.append([])
                    header = removeDuplicatesFromList(header) #Fix the header
                    writeToCSV(outputFilename, 'a', allValues, count, header, data)
                    header = []
                    data = []
                    blankLineCount = 0
                    break
    print('Found %d matrixes' % count) #debug only
    end = timer()
    print('%s%s: %f' % ('Expectation values DM', axis, (end-start)))

def findSpinOrbitEigenvectors(inputFilename, allValues, element, outputFilename):
    start = timer()
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Composition of spin-orbit eigenvectors'
    skipLinesCount = 2
    with open(inputFilename) as file:
        while findPattern(file, pattern, skipLinesCount):
            for line in file:
                splittedLine = line.split()
                if findHeader('Nr', splittedLine): # found header
                    splittedLine[4:7] = [''.join(splittedLine[4:7])]
                    header += splittedLine
                    row = 0
                    blankLineCount = 0
                elif len(splittedLine) > 1 and isAnyNumberInArray(splittedLine):
                    rowStart = 5
                    splittedLine[4:6] = [''.join(splittedLine[4:6])]
                    if len(data) > row:
                        data[row] += splittedLine[rowStart:]
                    else:
                        data.append(splittedLine)
                    row += 1
                    blankLineCount = 0
                else:
                    blankLineCount += 1
                if blankLineCount == 3: #time to stop
                    count += 1
                    data.append([])
                    header = removeDuplicatesFromList(header) #Fix the header
                    header.insert(3, 'Sym') # special hack
                    writeToCSV(outputFilename, 'a', allValues, count, header, data)
                    header = []
                    data = []
                    blankLineCount = 0
                    break
    print('Found %d matrixes' % count) #debug only
    end = timer()
    print('%s: %f' % ('Composition of spin-orbit eigenvectors', (end-start)))

def findSpinOrbitMatrixBlock(inputFilename, allValues, element, outputFilename, symmetry):
    start = timer()
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    symmetryPattern = '  Results for symmetry ' + str(symmetry)
    matrixPattern = ' => Spin-Orbit Matrixblock \(\S+\)'
    shiftPattern = '    The diagonal matrixelements are shifted by'
    skipLinesCount = 3
    with open(inputFilename) as file:
        while findPattern(file, symmetryPattern) and findPattern(file, matrixPattern, skipLinesCount):
            shiftRow = ['Shift:', getShiftedValue(file, shiftPattern)]
            for line in file:
                splittedLine = line.split()
                if re.match(' => Eigenvalues ', line) is not None:
                    blankLineCount += 1
                elif findHeader('State', splittedLine):
                    splittedLine[2:5] = [''.join(splittedLine[2:5])]
                    header += splittedLine
                    row = 0
                    blankLineCount = 0
                elif len(splittedLine) > 1:
                    rowStart = 0
                    if row % 2 == 0:
                        rowStart = 3
                    if len(data) > row:
                        if rowStart == 3:
                            splittedLine[2:4] = [''.join(splittedLine[2:4])]
                        data[row] += splittedLine[rowStart:]
                    else:
                        if rowStart == 0:
                            rowStart = 3
                        else:
                            rowStart = 0
                            splittedLine[2:4] = [''.join(splittedLine[2:4])]
                        data.append(splittedLine)
                        
                        data[row] = ['']*rowStart + data[row]
                    blankLineCount = 0
                    row += 1
                else:
                    blankLineCount += 1
                if blankLineCount == 2: #time to stop
                    count += 1
                    data.append([])
                    header = removeDuplicatesFromList(header) #Fix the header
                    writeToCSV(outputFilename, 'a', allValues, count, shiftRow, [])
                    writeToCSV(outputFilename, 'a', allValues, count, header, data)
                    header = []
                    data = []
                    blankLineCount = 0
                    break
    print('Found %d matrixes' % count) #debug only
    end = timer()
    print('%s: %f' % ('Spin-Orbit Matrixblock', (end-start)))

def findSpinOrbitMatrix(file, allValues, element, outputFilename):
    start = timer()
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Spin-Orbit Matrix \(\S+\)'
    with open(inputFilename) as file:
        while findPattern(file, pattern):
            for line in file:
                splittedLine = line.split()
                if findHeader('Nr', splittedLine):
                    header += splittedLine
                    blankLineCount = 0
                    row = 0
                elif len(splittedLine) > 1:
                    rowStart = 0
                    if row % 2 == 0:
                        rowStart = 4
                    if len(data) > row:
                        data[row] += splittedLine[rowStart:]
                    else:
                        data.append(splittedLine)
                        if rowStart == 0:
                            rowStart = 4
                        else:
                            rowStart = 0
                        data[row] = ['']*rowStart + data[row]
                    
                    blankLineCount = 0
                    row += 1
                else:
                    blankLineCount += 1
                if blankLineCount == 3: #time to stop
                    count += 1
                    data.append([])
                    header = removeDuplicatesFromList(header)    #Fix the header
                    writeToCSV(outputFilename, 'a', allValues, count, header, data)
                    header = []
                    data = []
                    blankLineCount = 0
                    break
    print('Found %d matrixes' % count) #debug only
    end = timer()
    print('%s: %f' % ('Spin-Orbit Matrix', (end-start)))

def createFolders(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

def writeToCSV(filename, mode, allValues, rvec, header, data):
    outputFilePath = outputFoldername + '/' + filename + '.csv'
    if separateFiles:
        outputFilePath = outputFoldername + '/' + filename + '/' + str(rvec) + '.csv'
    if not allValues:
        outputFilePath = outputFoldername + '/' + 'results.csv'

    createFolders(outputFilePath)
    with open(outputFilePath, mode) as outputFile:
        wr = csv.writer(outputFile, 'unix')
        wr.writerow({"sep=,"})# debug hack only
        wr.writerow(header)
        wr.writerows(data)

def cleanBeforeStart(path): # for testing purposes only
    if os.path.isdir(path):
        shutil.rmtree(path)

def loadConfig():
    with open(addAbsolutePath('config.json'), 'r') as file:
        config = json.load(file)
    return config

def addAbsolutePath(filename):
    return os.path.dirname(__file__) + '/' + filename

def startAsThreads(matrixes, allValues, element):
    SpinObritMatrixThread = threading.Thread(target=findSpinOrbitMatrix, args=(inputFilename, allValues, element, matrixes['Spin-Orbit Matrix']))
    SpinObritMatrixThread.start()
    
    SpinOrbitMatrixBlockThread = threading.Thread(target=findSpinOrbitMatrixBlock, args=(inputFilename, allValues, element, matrixes['Spin-Orbit Matrixblock'], 1))
    SpinOrbitMatrixBlockThread.start()
    
    SpinOrbitEigenvectorsThread = threading.Thread(target=findSpinOrbitEigenvectors, args=(inputFilename, allValues, element, matrixes['Composition of spin-orbit eigenvectors']))
    SpinOrbitEigenvectorsThread.start()
    
    ExpectedDMXValuesThread = threading.Thread(target=findExpectedDMValues, args=(inputFilename, allValues, element, matrixes['Expectation values DMX'], 'X'))
    ExpectedDMXValuesThread.start()

    ExpectedDMYValuesThread = threading.Thread(target=findExpectedDMValues, args=(inputFilename, allValues, element, matrixes['Expectation values DMY'], 'Y'))
    ExpectedDMYValuesThread.start()

    ExpectedDMZValuesThread = threading.Thread(target=findExpectedDMValues, args=(inputFilename, allValues, element, matrixes['Expectation values DMZ'], 'Z'))
    ExpectedDMZValuesThread.start()

    SpinObritMatrixThread.join()
    SpinOrbitMatrixBlockThread.join()
    SpinOrbitEigenvectorsThread.join()
    ExpectedDMXValuesThread.join()
    ExpectedDMYValuesThread.join()
    ExpectedDMZValuesThread.join()

def start(matrixes, allValues, element):
    findSpinOrbitMatrix(inputFilename, allValues, element, matrixes['Spin-Orbit Matrix'])
    findSpinOrbitMatrixBlock(inputFilename, allValues, element, matrixes['Spin-Orbit Matrixblock'], 1)
    findSpinOrbitEigenvectors(inputFilename, allValues, element, matrixes['Composition of spin-orbit eigenvectors'])
    findExpectedDMValues(inputFilename, allValues, element, matrixes['Expectation values DMX'], 'X')
    findExpectedDMValues(inputFilename, allValues, element, matrixes['Expectation values DMY'], 'Y')
    findExpectedDMValues(inputFilename, allValues, element, matrixes['Expectation values DMZ'], 'Z')

def main(argv):
    global inputFilename
    global outputFoldername
    global separateFiles
    configType = 'default'
    try:
        opts, args = getopt.getopt(argv,"i:o:c",["ifile=","ofolder=", "configtype="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfolder> -c <configtype>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <inputfile> -o <outputfolder> -c <confgtype>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFilename = addAbsolutePath(arg)
        elif opt in ("-o", "--ofolder"):
            outputFoldername = addAbsolutePath(arg)
        elif opt in ("-c", "--configtype"):
            configType = arg

    config = loadConfig()
    separateFiles = config[configType]['separateFiles']
    matrixes = {}
    for matrix in config[configType]['matrixes']:
        matrixes[matrix] = re.sub("[^a-zA-Z0-9]", "", matrix)

    startTime = timer()
    cleanBeforeStart(addAbsolutePath(config[configType]['outputFolder']))
    endTime = timer()

    print("Clean time: %f" % (endTime-startTime))
   
    if not inputFilename:
        inputFilename = addAbsolutePath(config[configType]['inputFilename'])
    if not outputFoldername:
        outputFoldername = addAbsolutePath(config[configType]['outputFolder'])
    
    

    startTime = timer()
    start(matrixes, config['default']['allValues'], config['default']['element'])
    #startASThreads(matrixes)
    endTime = timer()
    print('%s: %f' % ("Time", (endTime-startTime)))

if __name__ == "__main__":
   main(sys.argv[1:])
  
