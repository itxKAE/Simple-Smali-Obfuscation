# obfuscation_methods.py v0.2
# Description:  Android Obfuscation Methods, Class Renaming and Inserting Junkcode
# Changelog:    v0.1: Base Layout & Junkcode
#               v0.2: Added Class Renaming

import os
import random
import string
import shutil 

# === Utilities Section ===

# smali_finder()
# Description:  Find Smali files
# Args: 	path 		> Folder directory
# Returns: 	fileList	> Contains the directory of each of the smali file
def smali_finder(path):
	fileList = []
	for rootDir, subDir, files in os.walk(path):
		if "\\com" in rootDir or "\\edu" in rootDir or "\\ofp" in rootDir:
			if not "\\google" in rootDir and not "\\kotlin" in rootDir:
				for fileName in files:
					fileList.append(rootDir + "\\" + fileName)
	return fileList

# random_string()
# Description:  Randomise the given input with upper and lower case letters within the range of 10
# Returns: 	N.A.	> Random string
def random_string():
	letter = string.ascii_letters
	return ''.join(random.choice(letter) for i in range(10))

# get_op()
# Description:  Get op code from a pre-defined text file
# Returns: 	opList	> Contains the list of valid op codes
def get_op():
	opList = []
	fileOpen = open("nop_valid_op_code.txt", "r")
	for line in fileOpen:
		stripped = line.strip()
		stripped = stripped.split()
		opList.append(stripped)
	fileOpen.close()
	return opList

# get_junk()
# Description:  Insertion of 'nop' junk instructions
# Returns: 	junk	> Contains the number of junk, line by line
def get_junk():
	junk = ""
	count = random.randint(1, 2)
	for i in range(count):
		junk = junk + "\tnop\n"
	return junk

# ofp_check()
# Description:  Identify the key ofp Smali files to edit. This can cause certain obfuscation identifying application to malfunction due to the inconsistency of obfuscation added
# Args: 	path 		> Folder directory
# Returns: 	returnList	> Contains the list of ofp Smali files to edit
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

# === Obfuscation Methods Section ===

# class_rename()
# Description:  Implemented Obfuscation Method #1. This method is an upgrade of the typical class renaming obfuscation. Instead of editing only the class name within the code, this function will
#				edit the filename of every single Smali file of the main working directory to a random ascii string. In additon, the Manifest file will be edited to ensure that it will not help the
#				user in identify each of the classes' original intention.
# Args: 	path 		> Folder directory
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
			fileStream = fileStream.replace(key, value)
		fileSave = open(fileName, "w")
		fileSave.write(fileStream)
		fileSave.close()
		fileOpen.close()

		currentPath = ''.join(os.path.abspath(fileName).split(className + ".smali"))
		newFileName = newClassnameDict.get(className) + '.smali'
		newPath = currentPath + newFileName
		os.rename(fileName, newPath)

# insert_junk()
# Description:  Implemented Obfuscation Method #2. This method is an upgrade of the typical junkcode obfuscation. Typical obfuscator adds junkcode to every single Smali file found such that it is very easy
#				to be identified as obfuscated. To prevent this from happening, a small amount of commonly used Smali files will be inserted with junkcode instead. A small number means that it can disorient
#				certain obfuscation identifying softwares from working as intended.
# Args: 	path 		> Folder directory
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

# Run
path = input("Enter path to Decompiled Folder: ")
insert_junk(path)
class_rename(path)
print("Completed!")
