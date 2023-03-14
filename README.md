# chat-app
Python console chat application. Clients can send data both by TCP and UDP. 

Each client uses 2 threads - one for receiving messages and one for sending. 

Each server uses n+2 threads - n for handling each client, 1 for accepting tcp connections and one for receiving UDP messages.