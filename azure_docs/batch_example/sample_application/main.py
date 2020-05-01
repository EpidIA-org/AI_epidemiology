import sys, getopt, time, datetime
import pandas as pd
from sample_utils import utils


def main(argv):
   inputFile = ""
   outputFile = ""

   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print("test.py -i input_file")
      sys.exit(2)
   for opt, arg in opts:
      if opt == "-h":
         print("test.py -i file")
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputFile = arg
      elif opt in ("-o", "--ofile"):
         outputFile = arg
   
   print("Application version: 1.2")
   print("Started at:", datetime.datetime.now())
 
   # test using pandas (which should be installed through pip in the Job prep task)
   df = pd.read_csv(inputFile, header=None)
   print("\nReceived data:\n")
   print(df)
 
   # introducing delay so the task actually takes some time to run
   print("\nDoing something really important...\n") 
   time.sleep(5)

   # test using a function in another module
   df = df[[4]].head(10)
   df.columns = ['original']
   df["squared"] = df["original"].apply(lambda x: utils.square(x))
   print("\nProcessed data:\n")
   print(df)

   # write output
   df.to_csv(outputFile)
   print("\nWrote result to",outputFile)
   print("\nExited at:", datetime.datetime.now())
   
if __name__ == "__main__":
   main(sys.argv[1:])
  