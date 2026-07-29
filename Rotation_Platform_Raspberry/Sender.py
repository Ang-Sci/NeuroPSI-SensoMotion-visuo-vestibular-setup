import socket
import threading


class DataSender:
    def __init__(self, host='192.168.3.1', port=12345):
        """
        Initializes the DataSender with the server host and port.
        """
        self.host = host
        self.port = port
        self.running = False

    def start_client(self):
        """
        Creates a socket connection to the server and starts a thread to send messages.
        """
        # Create a socket object using IPv4 and TCP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the server
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
        self.running = True

    def send_a_message_to_server(self, message):
        
        if self.running == False:
            raise Exception("Connection must have been established with start_client method")
        # Va falloir envoyer speed et direction
        # Prompt the user for direction input
        # direction (clockwise/counterclockwise): ").strip().lower()
        # Prompt the user for speed input
        #speed_input = input("Enter speed (integer): ").strip()

        # Send the message to the server
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")

        except ConnectionAbortedError:
            self.stop_client()



    def receive_a_message(self):
        if self.running == False:
                raise Exception("connection must have been established with start_client method")
        # Va falloir envoyer speed et direction
        # Prompt the user for direction input
        # direction (clockwise/counterclockwise): ").strip().lower()
        # Prompt the user for speed input
        #speed_input = input("Enter speed (integer): ").strip()

        # Receive the server's response
        response = self.client_socket.recv(1024)
        message = response.decode('utf-8')
        if message:
                print(f"server response: {message}")
                return message
        else:
                return ""
        
    def stop_client(self):
        """
        Closes the socket connection and stops the client.
        """
        self.client_socket.close()
        self.running = False
        print("Connection closed")



