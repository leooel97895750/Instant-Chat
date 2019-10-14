# Instant-Chat
python socket programming

### When a server starts, it sends its binding address (IP address + port number) to the registrar.
* The binding port can be specified by the "-p" option.
* If 0 is specified, the OS will allocate a free port between 1024 and 65535.
### When a server terminates, it sends an "un-register" command to the registrar.
* A server may terminates for a few causes. One scenario is that it finishes chatting with a clienT. Another scenario is the user pressing Ctrl+C to stop it.
* You may handle Ctrl+C with an exception handler on KeyboardInterrupt.
### When a client starts, it sends a request to the registrar to inquery all online users. The registrar responds with a list of usernames and addresses.
* To encode a dictionary to bytes so that it can be sent by sockets, you may encode the dictionary to a JSON string, and then encode the string to bytes.
### The client shows the list of online users as below:
* Alice ('163.22.17.162', 2001)
* Bob ('163.22.20.109', 2002)
* Carol ('163.22.20.103', 2003)
### Then the user can input a number to choose a user to chat.
### For convenience, you may define a constant REGISTRAR_PORT in your registrar function.
