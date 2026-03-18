# from ipaddress import IPv4Address
# from dns.inet import AF_INET

import socket
message='/connect'
request_data='A103000F000F'
bytes_req_data=bytes.fromhex(request_data)
#crc=[2D, 6D]
try:
    #create socket
    client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #connect to server
    client_socket.connect(('127.0.0.1',12345))
    print("Client is connected")
    message = input("Want to send request?(y/n) or '/exit': ")
    if message == '/exit':
        # close socket
        print("Client Disconnected")
        client_socket.close()
    elif message=='y' or message=='yes':
        client_socket.send(bytes_req_data)  # sending
    client_socket.send(message.encode())  # sending
    # receive response
    response = client_socket.recv(1024).decode()  # receiving
    print(f"Server response: {response}")
    while True:
        # send message
        message = input("Another request?(y/n) or '/exit': ")
        if message =='/exit':
            #close socket
            print("Client Disconnected")
            client_socket.close()
            break
        elif message == 'y' or message == 'yes':
            client_socket.send(bytes_req_data)  # sending
        client_socket.send(message.encode())  # sending
        # receive response
        response = client_socket.recv(1024).decode()  # receiving
        print(f"Server response: {response}")

except Exception as er:
    print(f"Error: {er}")
