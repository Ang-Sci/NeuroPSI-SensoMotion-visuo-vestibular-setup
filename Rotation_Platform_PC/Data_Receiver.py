"""
@author: gbouvier
"""

import socket  # Import socket module for network communication
import threading  # Import threading module to handle multi-threading

class DataReceiver: 
    # Class to handle data reception through a TCP server
    
    def __init__(self, host='0.0.0.0', port=12345): 
        """
        Initialize the DataReceiver object with the given host and port.
        By default, it listens on all network interfaces (0.0.0.0) and port 12345.
        """
        self.host = host  # IP address for the server to bind to
        self.port = port  # Port number for the server
        self.direction = False  # Boolean variable to represent motor direction (False: Clockwise, True: Counterclockwise)
        self.speed = 0  # Integer variable to represent motor speed
        self.running = False  # Control flag to keep the server running
        
    def start_server(self):
        """
        Start the TCP server and listen for incoming client connections.
        """
        # Create a TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the server to the specified host and port
        self.server_socket.bind((self.host, self.port))
        # Start listening for incoming connections, with a maximum queue of 5 clients
        self.server_socket.listen(5)
        print(f"Server listening on the port {self.port} ...")
        # print(f"Launch program on Raspberry Pi")

        # Set a timeout of 120 seconds for the server socket
        self.server_socket.settimeout(120)
        # Accept a new client connection
        self.client_socket, self.addr = self.server_socket.accept() 
        print(f"Connection accepted from {self.addr}")
        # Set a 120-second timeout for the client connection
        self.client_socket.settimeout(120)


        
        self.running = True

        # Start a separate thread to handle data reception
        #self.thread = threading.Thread(target=self.listen_for_data_old)
        #self.thread.start() 
        


    def purge_messages(self): 
        """
        Cleans the buffer without waiting for incoming client connections. Does not read the data.
        """

        if self.running == False:
            raise Exception("Server must have been started with start_server method")

        try: 
            self.client_socket.setblocking(False)
            while True:
                data = self.client_socket.recv(1024)  # Receive up to 1024 bytes from the client
                
        except:
            pass
        
        self.client_socket.setblocking(True)
            
            
    def read_messages(self): 
        """
        Wait for incoming client connections and receive data.
        """
        if self.running == False:
            raise Exception("Server must have been started with start_server method")


        try: 
            data = self.client_socket.recv(1024)  # Receive up to 1024 bytes from the client
            
            # The function waits until there is data sent by the Sender on Raspberry Pi, except if the Sender has stopped the connection
            if not data:
                raise Exception("Sender has stopped the connection")

             
            # Decode the received data from bytes to string
            message = data.decode('utf-8') 
            # print(f"Received: {message}")
            
            return message
        

        ##except KeyboardInterrupt:  # Handle Ctrl+C to stop the server
            ##self.stop_server()  # Stop the server when interrupted
    
        except ConnectionResetError: 
            # Handle the case where the connection is lost
            print(f"Lost connection with {self.addr}")
        

    def send_a_message_to_client(self, message):
        """Used to send a message to control the platform"""

        if self.running == False:
            raise Exception("Server must have been started with start_server method")

        try:
            self.client_socket.sendall(message.encode('utf-8'))
            print(f"Message sent to the client: {message}")
        except Exception as e:
            print(f"Error : {e}")

    
    def stop_server(self): 
        """
        Stop the server and clean up resources.
        """
        if self.running == False:
            raise Exception("Server not running")

        # Close the client socket once done
        self.client_socket.close() 
        print(f"Connection closed with {self.addr}")
        
        self.server_socket.close()  # Close the server socket
        self.running = False  # Set the 'running' flag to False to stop the server loop
        print("Server stopped")
        