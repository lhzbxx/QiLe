import uuid

def main():
	f = open('uuid.txt', 'a+')
	f.write(str(uuid.uuid4()) + '\n')

if __name__ == '__main__':
	main()