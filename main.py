import sys, getopt
from lxml import etree
import csv 

inputfile = 'input/krb_so_t.xml' #testing only
outputfile = 'output/out.xml' #testing only
molProNamespace = "{http://www.molpro.net/schema/molpro-output}"
htmlNamespace = "{http://www.w3.org/1999/xhtml}"

def loadXMLFile(filename):
    if not filename:
        raise NameError
    parser = etree.XMLParser(ns_clean=True, remove_comments = True)
    return etree.parse(filename, parser)

def writeXMLFile(filename):
    xmlFile.write(filename)

def writeToCSV(filename, header, data):
    with open(filename+".csv", "a") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(data)

def main(argv):
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
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

def removeComments(xmlFile):
    comments = xmlFile.xpath('//comment()')
    for c in comments:
        p = c.getparent()
        p.remove(c)

if __name__ == "__main__":
   main(sys.argv[1:])
   xmlFile = loadXMLFile(inputfile)
   #removeComments(xmlFile)
   #writeXMLFile(outputfile)
   root = xmlFile.getroot()
   for child in root.getchildren():
       if child.tag == molProNamespace+"job":
           root = child
           print("Found job")
           break
   header = []
   data = []
   for child in root.getchildren():
        if child.tag == htmlNamespace+"table":
            print("Found some tables")
            for children in child.find(htmlNamespace+"thead"):
                header = children.itertext()
            for children in child.find(htmlNamespace+"tbody"):
                data.append(elem.strip() for elem in [item for item in children.itertext() if item is not None])
            writeToCSV("testing", header, data)
            data.clear()
