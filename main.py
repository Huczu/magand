import sys, os, getopt
import csv 
import re
from timeit import default_timer as timer

def findSpinOrbitMatrix(file):
    data = []
    match = None
    header = []
    blankLineCount = 0
    row = 0
    i = 0
    for line in file:
        if not match:
            match = re.match(" Spin-Orbit Matrix \(\S+\)", line)
        else:
            splittedLine = line.split()
            if splittedLine and splittedLine[0] == 'Nr':
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
                    data[row] = ['']*rowStart + data[row]
                    
                blankLineCount = 0
                row += 1
            else:
                blankLineCount += 1
            if blankLineCount == 3: #time to stop
                data.append([])
                header = list(dict.fromkeys(header))    #Fix the header
                with open('output/spinOrbitMatrixes.csv', 'a') as outputFile:
                    writeToCSV(outputFile, header, data)                    
                    i += 1
                    header = []
                    data = []
                    match = None
                    blankLineCount = 0

    return header, data #not needed now

def writeToCSV(file, header, data):
        wr = csv.writer(file, 'unix')
        wr.writerow(header)
        wr.writerows(data)

def cleanBeforeStart(): # for testing purposes only
    testingFiles = ['output/spinOrbitMatrixes.csv']
    for filename in testingFiles:
       if os.path.isfile(filename):
            os.remove(filename)

def main(argv):
   inputFilename = 'input/krb_so_t.out' #testing only
   outputFilename = 'output/out.csv' #testing only
   start = timer()
   cleanBeforeStart()
   end = timer()
   print("Clean time: %f" % (end-start))
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('main.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('main.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputFilename = arg
      elif opt in ("-o", "--ofile"):
         outputFilename = arg
   start = timer()
   with open(inputFilename) as inputFile:
      header, data = findSpinOrbitMatrix(inputFile)
   end = timer()
   print('Spin Orbit Matrix: %f' % (end-start))

if __name__ == "__main__":
   main(sys.argv[1:])
  
