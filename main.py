import sys, os, getopt
import shutil
import csv 
import re
import json
from timeit import default_timer as timer

inputFilename = ''
outputFoldername = ''

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

def skipLines(file, lines):
    for i in range(lines):
        next(file)

def removeDuplicatesFromList(arg):
    return list(dict.fromkeys(arg))

def findExpectedDMValues(file, outputFilename, axis):
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Property matrix of the DM' + axis + ' operator'
    skilLinesCount = 3
    while findPattern(file, pattern, 3):
        for line in file:
            splittedLine = line.split()
            if findHeader('Nr', splittedLine): # found header
                splittedLine[1:4] = [''.join(splittedLine[1:4])]
                header += splittedLine
                row = 0
                blankLineCount = 0
            elif len(splittedLine) > 1:
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
            if blankLineCount == 2: #time to stop
                data.append([])
                header = removeDuplicatesFromList(header) #Fix the header
                writeToCSV(outputFilename, 'a', header, data)                    
                count += 1
                header = []
                data = []
                blankLineCount = 0
                break
    return count #debug only

def findSpinOrbitEigenvectors(file, outputFilename):
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Composition of spin-orbit eigenvectors'
    skipLinesCount = 2
    while findPattern(file, pattern, skipLinesCount):
        for line in file:
            splittedLine = line.split()
            if findHeader('Nr', splittedLine): # found header
                splittedLine[4:7] = [''.join(splittedLine[4:7])]
                header += splittedLine
                row = 0
                blankLineCount = 0
            elif len(splittedLine) > 1: #parse non empty line
                rowStart = 5
                splittedLine[4:6] = [''.join(splittedLine[4:6])]
                if len(data) > row:
                    data[row] += splittedLine[rowStart:]
                else:
                    data.append(splittedLine)
                    blankLineCount = 0
                    row += 1
            else:
                blankLineCount += 1
            if blankLineCount == 2: #time to stop
                data.append([])
                header = removeDuplicatesFromList(header) #Fix the header
                header.insert(3, 'Sym') # special hack
                writeToCSV(outputFilename, 'a', header, data)                    
                count += 1
                header = []
                data = []
                blankLineCount = 0
                break
    return count

def findSpinOrbitMatrixBlock(file, outputFilename, symmetry):
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    symmetryPattern = '  Results for symmetry ' + str(symmetry)
    matrixPattern = ' => Spin-Orbit Matrixblock \(\S+\)'
    skipLinesCount = 3
    while findPattern(file, symmetryPattern) and findPattern(file, matrixPattern, skipLinesCount):
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
                data.append([])
                header = removeDuplicatesFromList(header) #Fix the header
                writeToCSV(outputFilename, 'a', header, data)                    
                count += 1
                header = []
                data = []
                blankLineCount = 0
                break
    return count #debug only

def findSpinOrbitMatrix(file, outputFilename):
    data = []
    header = []
    blankLineCount = 0
    row = 0
    count = 0
    pattern = ' Spin-Orbit Matrix \(\S+\)'

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
                data.append([])
                header = removeDuplicatesFromList(header)    #Fix the header
                writeToCSV(outputFilename, 'a', header, data)                    
                count += 1
                header = []
                data = []
                blankLineCount = 0
                break
    return count

def writeToCSV(filename, mode, header, data):
    outputFilePath = outputFoldername + '/' + filename + '.csv'
    with open(outputFilePath, mode) as outputFile:
        wr = csv.writer(outputFile, 'unix')
        wr.writerow({"sep=,"})# debug hack only
        wr.writerow(header)
        wr.writerows(data)

def cleanBeforeStart(path): # for testing purposes only
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)

def loadConfig():
    with open(addAbsolutePath('config.json'), 'r') as file:
        config = json.load(file)
    return config

def addAbsolutePath(filename):
    return os.path.dirname(__file__) + '/' + filename

def main(argv):
    config = loadConfig()
    global inputFilename
    global outputFoldername
    matrixes = {}
    for matrix in config['default']['matrixes']:
        matrixes[matrix] = re.sub("[^a-zA-Z0-9]", "", matrix)

    start = timer()
    cleanBeforeStart(addAbsolutePath(config['default']['outputFolder']))
    end = timer()

    print("Clean time: %f" % (end-start))
   
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofolder="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfolder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <inputfile> -o <outputfolder>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFilename = addAbsolutePath(arg)
        elif opt in ("-o", "--ofolder"):
            outputFoldername = addAbsolutePath(arg)
    if not inputFilename:
        inputFilename = addAbsolutePath(config['default']['inputFilename'])
    if not outputFoldername:
        outputFoldername = addAbsolutePath(config['default']['outputFolder'])

    start = timer()
    with open(inputFilename) as inputFile:
        count = findSpinOrbitMatrix(inputFile, matrixes['Spin-Orbit Matrix'])
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Spin-Orbit Matrix', (end-start)))
        start = end
    with open(inputFilename) as inputFile:
        count = findSpinOrbitMatrixBlock(inputFile, matrixes['Spin-Orbit Matrixblock'], 1)
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Spin-Orbit Matrixblock', (end-start)))
        start = end
    with open(inputFilename) as inputFile:
        count = findSpinOrbitEigenvectors(inputFile, matrixes['Composition of spin-orbit eigenvectors'])
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Composition of spin-orbit eigenvectors', (end-start)))
        start = end
    with open(inputFilename) as inputFile:
        count = findExpectedDMValues(inputFile, matrixes['Expectation values DMX'], 'X')
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Expectation values DMX', (end-start)))
        start = end
    with open(inputFilename) as inputFile:
        count = findExpectedDMValues(inputFile, matrixes['Expectation values DMY'], 'Y')
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Expectation values DMY', (end-start)))
        start = end
    with open(inputFilename) as inputFile:
        count = findExpectedDMValues(inputFile, matrixes['Expectation values DMZ'], 'Z')
        print('Found %d matrixes' % count) #debug only
        end = timer()
        print('%s: %f' % ('Expectation values DMZ', (end-start)))
        start = end
if __name__ == "__main__":
   main(sys.argv[1:])
  
