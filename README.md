# python-tcp-chat

This is a TCP chat server built in Python using the standard `socket` and `threading` libraries.

## Getting Started

1.  **Clone the Repository:**
    Open your terminal and run this command to download the code:
    ```sh
    git clone [https://github.com/Aaryanyd06/python-tcp-chat.git](https://github.com/Aaryanyd06/python-tcp-chat.git)
    ```

2.  **Navigate to the Directory:**
    ```sh
    cd python-tcp-chat
    ```

## How to Run the Server

1.  **Run the Server:**
    Once you are in the `python-tcp-chat` folder, run the server:
    ```sh
    python server.py
    ```
2.  The server will start and listen on port **4000**.

## How to Connect

You will need at least two other terminals to test the chat.

* **Connect a Client:**
    In a new terminal, use `ncat` to connect:
    ```sh
    ncat localhost 4000
    ```

## Example Chat Interaction

Here is an example of the input/output for two users chatting.

### Terminal 1: User "user_one"

```sh
$ ncat localhost 4000
LOGIN user_one
OK
INFO user_two connected
MSG hello there
MSG user_one hello there
MSG user_two hi!
WHO
USER user_one
USER user_two
INFO user_two disconnected

Terminal 2: User "user_two"
Bash

$ ncat localhost 4000
LOGIN user_one
ERR username-taken
LOGIN user_two
OK
INFO user_one connected
MSG user_one hello there
MSG hi!
MSG user_two hi!