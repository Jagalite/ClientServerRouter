import socket, pickle, sys, subprocess, time
from threading import Thread
 
def serialize(data):
    return pickle.dumps(data)
    
def deserialize(data):
    return pickle.loads(data)
    
def sendPullMessage(socket):
    message = {}
    message["version"] = 1
    message["type"] = "pull"
    message["id"] = 17
    message["body"] = getRoutingTable()
    message["myName"] = myName
    serialized = serialize(message)
    socket.send(serialized)
    
    #serverResponse = socket.recv(4096)
    #response = deserialize(serverResponse)
    #if(response["type"] == "push"):
    #    global routingTable
    #    routingTable[response["myName"]] = response["body"]
    #    print("RECIEVED FROM: ", response["myName"], " - TABLE: ", routingTable[response["myName"]] )
    #return
    
def sendPushMessage(socket):
    message = {}
    message["version"] = 1
    message["type"] = "push"
    message["id"] = 17
    message["body"] = getRoutingTable()
    message["myName"] = myName
    serialized = serialize(message)
    socket.send(serialized)
    
    #serverResponse = socket.recv(4096)
    #response = deserialize(serverResponse)
    #if(response["type"] == "end"):
    #    socket.close()
    
def sendEndMessage(connection):
    message = {}
    message["version"] = 1
    message["type"] = "end"
    message["id"] = 17
    message["body"] = getRoutingTable()
    message["myNameName"] = myName
    serialized = serialize(message)
    connection.send(serialized)
    
def processPullRequest(connection):
    message = {}
    message["version"] = 1
    message["type"] = "push"
    message["id"] = 17
    message["body"] = getRoutingTable()
    message["myName"] = myName
    serialized = serialize(message)
    connection.send(serialized)
    
    
def processPushRequest(request):
    global routingTable
    routingTable = updateRoutingTable(myName, request["myName"],routingTable, request["body"]) # routingTable[request["myName"]] = request["body"]
    print("RECIEVED FROM: ", request["myName"], " - TABLE: ", request["body"])
    print("UPDATE: ", routingTable)
    
def getRoutingTable():
    return routingTable
    
def printRoutingTable():
    print(routingTable)
    
def getTimeStamp():
	return str(time.time())
	
def updateRoutingTable(currentRouter, toAddRouter, currentTable, toAddTable):
	distance = currentTable[toAddRouter]
	for router in toAddTable:
		if(router != currentRouter and router != toAddRouter):
			currentRoute = currentTable[toAddRouter] + toAddTable[router]
			if(currentTable[router] == None or currentTable[router] > currentRoute):
				currentTable[router] = currentRoute
	return currentTable


#===================================================================================
def waitForConnection(socket):
    while(True):
        connection, address = socket.accept()
        print("CONNECTED~")
        Thread(target=connected, args=(connection,)).start()
        
def connected(connection):
    try:
    	while(True):
        	request = connection.recv(4096)
        	requestMessage = deserialize(request)
        	if(requestMessage["type"] == "pull"):
            		print("PULL REQUEST RECIEVED FROM: " + requestMessage["myName"] + " - " + getTimeStamp())
            		processPullRequest(connection)
            		print(myName + ": PULL REQUEST FULLFILLED: " + requestMessage["myName"]  + " - " + getTimeStamp())
        	else:
            		print(myName + ": PUSH REQUEST RECIEVED FROM: " + requestMessage["myName"] + " - " + getTimeStamp())
            		processPushRequest(requestMessage)
            		print(myName + ": PUSH REQUEST FULLFILLED: " + requestMessage["myName"]  +" - " + getTimeStamp())
    except:
    	print("Closing Connection")
    	
    
def sendData(socket):
    for i in range(10):
        print(myName + ": SENDING PULL MESSAGE - " + getTimeStamp())
        sendPullMessage(socket)
        print(myName + ": PULL MESSAGE FULLFILLED - " + getTimeStamp())
        time.sleep(3)
    
        print(myName + ": SENDING PUSH MESSAGE - " + getTimeStamp())
        sendPushMessage(socket)
        print(myName + ": PUSH MESSAGE FULLFILLED - " + getTimeStamp())
        time.sleep(3)

def connectToServer(connection, port):
    socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketConnection.connect((connection, port))
    Thread(target=sendData, args=(socketConnection,)).start()

routingTable0 = {"router0" : 0, "router1" : 1, "router2" : 3, "router3" : 7}
routingTable1 = {"router0" : 1, "router1" : 0, "router2" : 1, "router3" : None}
routingTable2 = {"router0" : 3, "router1" : 1, "router2" : 0, "router3" : 2}
routingTable3 = {"router0" : 7, "router1" : None, "router2" : 2, "router3" : 0}

myHost = ''
myPort = 0
myName = ''
connection1 = ''
connection2 = ''
connection3 = ''
routingTable = None

arguments = sys.argv;
myHost = arguments[1]
port = int(arguments[2])
myName = arguments[3]
connection1 = socket.gethostbyname(arguments[4])
connection2 = socket.gethostbyname(arguments[5])
if(len(arguments) > 6):
	connection3 = socket.gethostbyname(arguments[6])

print("Host: ", myHost)
print("Port: ", port)
print("Name: ", myName)
print("Connection: ", connection1)
print("Connection: ", connection2)
if(connection3 != ''):
	print("Connection: ", connection3)

if(myName == "router0"):
	routingTable = routingTable0
if(myName == "router1"):
	routingTable = routingTable1
if(myName == "router2"):
	routingTable = routingTable2
if(myName == "router3"):
	routingTable = routingTable3

print(routingTable)

#Start listening
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((myHost, port))
serverSocket.listen()
Thread(target=waitForConnection, args=(serverSocket,)).start()

time.sleep(6)

connectToServer(connection1, port);
connectToServer(connection2, port);
if(connection3 != ''):
	connectToServer(connection3, port);

