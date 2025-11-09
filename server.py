import socket
import sys
import threading

HOST = '0.0.0.0'
PORT = 4000
clients = {}
lock = threading.Lock()

def broadcast(message, sender_conn=None):
    with lock:
        # We iterate over a copy of the values (connections)
        for conn in clients.values():
            if conn != sender_conn:
                try:
                    conn.sendall(message.encode())
                except socket.error:
                    # Client is probably disconnected, we'll clean it up in handle_client
                    pass

def handle_client(conn, addr):
    print(f"Handling connection from: {addr[0]}:{addr[1]}")
    username = None
    
    try:
        # 1. Login Flow
        while True:
            try:
                data = conn.recv(1024).strip().decode()
                if not data:
                    print(f"{addr[0]}:{addr[1]} disconnected before login.")
                    return
            except ConnectionResetError:
                 print(f"{addr[0]}:{addr[1]} disconnected before login.")
                 return

            if not data.startswith("LOGIN "):
                conn.sendall(b"ERR Invalid login. Use: LOGIN <username>\n")
                continue
            
            potential_username = data.split(None, 1)[1]
            if not potential_username:
                 conn.sendall(b"ERR Username cannot be empty.\n")
                 continue

            with lock:
                if potential_username in clients:
                    conn.sendall(b"ERR username-taken\n")
                else:
                    username = potential_username
                    clients[username] = conn
                    conn.sendall(b"OK\n")
                    print(f"{username} has logged in from {addr[0]}:{addr[1]}")
                    break
        
        broadcast(f"INFO {username} connected\n", conn)

        # 2. Messaging Loop
        while True:
            try:
                data = conn.recv(1024).strip().decode()
                if not data:
                    break
            except ConnectionResetError:
                break

            if data.startswith("MSG "):
                text = data.split(None, 1)[1]
                broadcast_msg = f"MSG {username} {text}\n"
                
                with lock:
                    for conn_to_send in clients.values():
                        try:
                            conn_to_send.sendall(broadcast_msg.encode())
                        except socket.error:
                            pass
            
            elif data == "WHO":
                with lock:
                    active_users = "\n".join([f"USER {user}" for user in clients])
                    conn.sendall(f"{active_users}\n".encode())
            
            elif data == "PING":
                conn.sendall(b"PONG\n")
            
            elif data.startswith("DM "):
                parts = data.split(None, 2)
                if len(parts) == 3:
                    target_user = parts[1]
                    dm_text = parts[2]
                    
                    with lock:
                        if target_user in clients:
                            target_conn = clients[target_user]
                            try:
                                # Send message to target
                                target_conn.sendall(f"DM from {username}: {dm_text}\n".encode())
                                # Send confirmation to sender
                                conn.sendall(f"DM sent to {target_user}\n".encode())
                            except socket.error:
                                conn.sendall(f"ERR Failed to send DM to {target_user}.\n".encode())
                        else:
                            conn.sendall(f"ERR User '{target_user}' not found.\n".encode())
                else:
                    conn.sendall(b"ERR Usage: DM <username> <text>\n")

            else:
                conn.sendall(b"ERR Unknown command.\n")

    except socket.error as e:
        print(f"Error with client {addr[0]}:{addr[1]}: {e}")
    
    finally:
        # 3. Disconnect Flow
        conn.close()
        if username:
            with lock:
                if username in clients:
                    del clients[username]
            
            broadcast(f"INFO {username} disconnected\n")
            print(f"{username} disconnected.")
        else:
             print(f"{addr[0]}:{addr[1]} disconnected.")

def start_server():
    global PORT
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid port '{sys.argv[1]}'. Using default {PORT}.")
            sys.exit(1)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(f"Error binding to port {PORT}: {e}")
        sys.exit(1)

    server_socket.listen()
    print(f"Server is listening on {HOST}:{PORT}...")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"New connection from: {addr[0]}:{addr[1]}")
            
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    start_server()