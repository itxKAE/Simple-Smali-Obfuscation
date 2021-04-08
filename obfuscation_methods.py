import os
import random
import string

# === Utilities ===
def smali_finder(path):
	fileList = []
	for rootDir, subDir, files in os.walk(path):
		if "\\com" in rootDir or "\\edu" in rootDir or "\\ofp" in rootDir:
			if not "\\google" in rootDir and not "\\kotlin" in rootDir:
				for fileName in files:
					fileList.append(rootDir + "\\" + fileName)
	return fileList

def random_string():
	letter = string.ascii_letters
	return ''.join(random.choice(letter) for i in range(10))

def get_op():
	opList = []
	fileOpen = open("nop_valid_op_code.txt", "r")
	for line in fileOpen:
		stripped = line.strip()
		stripped = stripped.split()
		opList.append(stripped)
	fileOpen.close()
	return opList

def get_junk():
	junk = ""
	count = random.randint(1, 2)
	for i in range(count):
		junk = junk + "\tnop\n"
	return junk

def ofp_check(path):
	fileList = []
	fileList = smali_finder(path)
	
	ofpList = []
	returnList = []
	for fileName in fileList:
		if not "ofp" in fileName:
			with open(fileName, "r") as fileOpen:
				buf = fileOpen.readlines()
				for line in buf:
					if "Lofp/" in line:
						line = line.split("Lofp/")[1]
						line = line.split(";")[0]
						ofpList.append(line + ".smali")
	for i in ofpList:
		if i not in returnList:
			returnList.append(i)
	return returnList

# === Obfuscation Methods ===
def class_rename(path):
	manifestPath = path + "\\AndroidManifest.xml"
	path = path + "\\smali"

	fileList = []
	fileList = smali_finder(path)

	newClassnameDict = {}
	manifestOpen = open(manifestPath, "r")
	manifestStream = manifestOpen.read()
	for fileName in fileList:
		className = fileName.split('\\')[-1]
		className = className.split(".smali")[0]
		if "MainActivity" in className or "ofp" in fileName:
			newClassnameDict[className] = className
		else:
			newClassString = random_string()
			newClassnameDict[className] = newClassString
			manifestStream = manifestStream.replace(className, newClassString)
	manifestSave = open(manifestPath, "w")
	manifestSave.write(manifestStream)
	manifestSave.close()
	manifestOpen.close()

	for fileName in fileList:
		className = fileName.split('\\')[-1]
		className = className.split(".smali")[0]
		fileOpen = open(fileName, "r")
		fileStream = fileOpen.read()
		for key, value in newClassnameDict.items():
			#print(key, value)
			fileStream = fileStream.replace(key, value)
		#print("========================")
		fileSave = open(fileName, "w")
		fileSave.write(fileStream)
		fileSave.close()
		fileOpen.close()

		currentPath = ''.join(os.path.abspath(fileName).split(className + ".smali"))
		newFileName = newClassnameDict.get(className) + '.smali'
		newPath = currentPath + newFileName
		os.rename(fileName, newPath)

def insert_junk(path):
	path = path + "\\smali"

	fileList = []
	fileList = smali_finder(path)

	opCode = []
	opCode = get_op()

	ofpCheck = []
	ofpCheck = ofp_check(path)

	for fileName in fileList:
		if not "ofp" in fileName:
			with open(fileName, "r") as fileOpen:
				buf = fileOpen.readlines()
			with open(fileName, "w") as fileSave:
				for line in buf:
					for i in range(len(opCode)):
						if opCode[i][0] in line and not ".super" in line and not ":" in line:
							line = line + get_junk()
					fileSave.write(line)
			fileSave.close()
			fileOpen.close()
		elif "ofp" in fileName:
			for num in range(len(ofpCheck)):
				if ofpCheck[num] in fileName:
					with open(fileName, "r") as fileOpen:
						buf = fileOpen.readlines()
					with open(fileName, "w") as fileSave:
						for line in buf:
							for i in range(len(opCode)):
								if opCode[i][0] in line and not ".super" in line and not ":" in line:
									line = line + get_junk()
							fileSave.write(line)
					fileSave.close()
					fileOpen.close()

# === Testing ===
class_rename("D:\\School\\2207 - Mobile Security\\Project\\Assignment 2\\Working Folder\\app-release")
insert_junk("D:\\School\\2207 - Mobile Security\\Project\\Assignment 2\\Working Folder\\app-release")