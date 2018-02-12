import os
import sys

class record(object):
	"""docstring for record"""
	inputMessage = ""
	CMTE_ID = ""
	NAME = ""
	ZIP_CODE = ""
	TRANSACTION_DT = ""
	YEAR = ""
	TRANSACTION_AMT = ""
	OTHER_Id = ""

	total_amount = 0
	def __init__(self, inputMessage):
		
		self.OTHER_Id = inputMessage['OTHER_Id']
		self.TRANSACTION_DT = inputMessage['TRANSACTION_DT']
		self.ZIP_CODE = inputMessage['ZIP_CODE']
		self.NAME = inputMessage['NAME']
		self.CMTE_ID = inputMessage['CMTE_ID']
		self.TRANSACTION_AMT = inputMessage['TRANSACTION_AMT']

	def isValid(self):
		
		if len(self.OTHER_Id) > 0:
			# ignore if OTHER_Id contains any other value
			return False

		tdt = self.TRANSACTION_DT
		if len(tdt) == 8:
			# ignore if TRANSACTION_DT is empty or malformed
			try:
				num = int(tdt)
			except ValueError:
				return False
			YEAR = int(tdt[4])*1000 + int(tdt[5]) * 100 + int(tdt[6]) *10 + int(tdt[7])
			MONTH_FEB = 28
			if YEAR > 2018:
				return False
			if YEAR % 4 == 0:
				MONTH_FEB = 29
			MONTH = int(tdt[0]) * 10 + int(tdt[1])
			if MONTH > 12 or MONTH == 0:
				return False
			DAY = int(tdt[2]) * 10 + int(tdt[3])
			if MONTH == 1 or MONTH ==3 or MONTH ==5 or MONTH == 7 or MONTH ==8 or MONTH == 10 or MONTH ==12:
				if DAY == 0 or DAY > 31:
					return False
			if MONTH == 4 or MONTH == 6 or MONTH == 9 or MONTH == 11:
				if DAY == 0 or DAY > 30:
					return False
			if MONTH == 2 and (DAY == 0 or DAY > MONTH_FEB):
				return False
			self.YEAR = str(YEAR)
		else:
			return False

		zip_code = self.ZIP_CODE
		if len(zip_code) < 5:
			# ignore if ZIP_CODE is an valid zip code
			return False
		self.ZIP_CODE = zip_code[:5]

		n = self.NAME
		if len(n) <=0:
			# skip if NAME is an invalid 
			return False 
		if len(self.CMTE_ID) == 0 or len(self.TRANSACTION_AMT) == 0:
			# CMTE_ID or TRANSACTION_AMT contains empty
			return False
		try:
			self.TRANSACTION_AMT = int(self.TRANSACTION_AMT)
		except ValueError:
			return False

		#print ("CMTE_ID {0} 	NAME {1}	ZIP_CODE {2} 	TRANSACTION_DT {3}	TRANSACTION_AMT {4} 	OTHER_Id {5}".format(self.CMTE_ID,self.NAME,self.ZIP_CODE,self.TRANSACTION_DT,self.TRANSACTION_AMT,self.OTHER_Id))
		return True

	def isDuplicate(self,n_id):
		if n_id == "":
			return True
		n_NAME,n_ZIP_CODE = n_id.split('|')
		if self.NAME == n_NAME and self.ZIP_CODE == n_ZIP_CODE:
			return True
		return False
	def getInfo(self):
		return self.NAME+'|'+self.ZIP_CODE

# main function
def processLine(inputString):
	# suppose something like "C00629618|N|TER|P|201701230300133512|15C|IND|PEREZ, JOHN A|LOS ANGELES|CA|90017|PRINCIPAL|DOUBLE NICKEL ADVISORS|01032017|40|H6CA34245|SA01251735122|1141239|||2012520171368850783"
	requiredField = {"CMTE_ID":0,"NAME":7,"ZIP_CODE":10,"TRANSACTION_DT":13,"TRANSACTION_AMT":14,"OTHER_Id":15}
	# split
	inputStrs = inputString.split('|')
	if len(inputStrs) < 15:
		return None
	inputMessage = {}
	for key in requiredField.keys():
		inputMessage[key] = inputStrs[requiredField[key]]
	rTmp = record(inputMessage)
	return rTmp
		
if __name__ == '__main__':

	# get args
	if len(sys.argv) > 2:
		print("[FAIL]: Do not receive proper arguments")
		exit()
	runtype = ""
	if len(sys.argv) == 1:
		# run evaluation rather than test file
		percentage_file = "./input/percentile.txt"
		input_file = "./input/itcont.txt"
		output_file = "./output/repeat_donors.txt"
		runtype = "evaluation"
	else:
		# run test situation
		percentage_file = sys.argv[1]+"input/percentile.txt"
		input_file = sys.argv[1]+"input/itcont.txt"
		output_file = sys.argv[1]+"output/repeat_donors.txt"
		runtype = sys.argv[1]
	# print(percentage_file,input_file)
	# read percent file
	percent = 0
	try:
		percentage = open(percentage_file,"r")
		try:
			percent = int(percentage.read())
		except ValueError:
			print("[FAIL]: "+runtype+": invalid percentage number!")
			percentage.close()
			exit()
	except IOError:
		print("[FAIL]: "+runtype+": Unable to find perentage file.")
		exit()
	percentage.close()
	# print("percentage {}".format(percent))
	

	try:
		inputfile = open(input_file,"r")
	except IOError:
		print("[FAIL]: "+runtype+": Unable to find itcont file.")
		exit()

	recordlist = []
	recordMap = {}
	duplicateRecord = {}
	total_number_repeat = 0
	total_amount = 0
	inputfile = open(input_file,"r")
	outputfile = open(output_file,"w+")
	for line in inputfile:
		if line != "":
			rTmp = processLine(line)
			if rTmp is not None and rTmp.isValid():
				recordlist.append(rTmp)
				info = rTmp.getInfo()
				YEAR = rTmp.YEAR
				# print (info+rTmp.YEAR)
				if info not in recordMap:
					recordMap[info] = []
					recordMap[info].append(rTmp)
				else:
					# duplicate # recipient zip year
					if rTmp.CMTE_ID not in duplicateRecord:
						duplicateRecord[rTmp.CMTE_ID] = {}
					if rTmp.ZIP_CODE not in duplicateRecord[rTmp.CMTE_ID]:
						duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE] = {}
					if YEAR not in duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE]:
						duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR] = []
					if len(duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR]) == 0:
						rTmp.total_amount = rTmp.TRANSACTION_AMT
					else:
						rTmp.total_amount = duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR][-1].total_amount + rTmp.TRANSACTION_AMT
					duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR].append(rTmp)
					total_number_repeat = len(duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR])
					total_amount = rTmp.total_amount
					# percentage
					num_ = (percent / 100) * total_number_repeat + 0.5
					if num_ < 1:
						num_ = 1
					else:
						num_ = int(num_)
					percentile_contribution = duplicateRecord[rTmp.CMTE_ID][rTmp.ZIP_CODE][YEAR][num_-1].TRANSACTION_AMT
					outputStr = rTmp.CMTE_ID+'|'+rTmp.ZIP_CODE+'|'+str(YEAR)+'|'+str(percentile_contribution)+'|'+str(total_amount)+'|'+str(total_number_repeat)
					outputfile.write(outputStr+'\n')
	# find duplicate
	inputfile.close()
	outputfile.close()




