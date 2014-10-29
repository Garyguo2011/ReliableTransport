import sys

f = sys.stdin
print(f.read())



def test(filename):
	try:
		_filePtr = open(filename, 'r')
		tmp = _filePtr.read(1440)
		if tmp == "":
			_filePtr.close()
			_filePtr = open(filename, 'w')
			userInput = raw_input(">")
			_filePtr.write(userInput)
			_filePtr.close()
			_filePtr = open(filename, 'r')
			print(_filePtr.read())
			_filePtr.close()
			_filePtr = open(filename, 'w')
			_filePtr.write("")
			_filePtr.close()
	except IOError:
		print("'" + filename + "' doesn't exist")
	

