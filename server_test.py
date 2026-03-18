# from transformers.pipelines import values

import socket

message='/connect'
data_values= 'a1031e000000000000000000000036000002100002ffff00000000f00103c500005469'
bytes_data_val=bytes.fromhex(data_values)
try:
    #create a socket (AF_INET=IPv4, SOCK_STREAM=TCP)
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #or
    #with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_socket:

    #Bind IP and port with server_socket
    server_socket.bind(('127.0.0.1',12345))   #(ip=127.0.0.1, port=12345)

    #Wait for connection
    server_socket.listen(1)
    print("Server is waiting for connection...")

    #Accepting client connection
    client_socket,address=server_socket.accept()
    print(f"Connected to: {address}")

    while True:
        #Receiving Data & Sending reply
        data=client_socket.recv(1024).decode()   #receiving
        print(f"client says: {data}")
        message=input("Enter your reply  or '/exit': ")
        if message =='/exit':
            #close connection
            print("Server Stopped")
            client_socket.close()
            server_socket.close()
            break
        client_socket.send(message.encode())   #sending

except Exception as e:
    print(f"Error: {e}")
