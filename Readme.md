
---

# AI Agent Communication System

This project demonstrates a simple system where two AI agents, running on separate devices, communicate with each other over a network. The agents are designed to perform specific tasks: one acts as a code generator, and the other as an akinator, asking questions.

## Overview

- **Client Agent (`client.py`)**: Acts as a code generator named Ram Kishan. It connects to a server, receives instructions, and generates code as a response.
- **Server Agent (`server.py`)**: Acts as an akinator, asking a series of questions. It listens for connections, interacts with the client agent, and handles the communication loop.

Both agents utilize the `LangChain` library to manage conversation and generate responses.

## Project Structure

- `client.py`: The client-side script, which connects to the server and handles incoming instructions.
- `server.py`: The server-side script, which initiates a conversation and manages the interaction with the client agent.

## Requirements

- Python 3.8 or higher
- `langchain-community` and `langchain-core` libraries
- `socket` library (standard in Python)

To install the necessary Python packages, run:

```bash
pip install langchain-community langchain-core
```

## Setup and Usage

### 1. Setting Up the Server

1. Ensure the server has a public IP or accessible network address.
2. Run the server script:

    ```bash
    python server.py
    ```

    The server will start and listen on port `5050` for incoming connections.

### 2. Setting Up the Client

1. In the `client.py` file, set the `server_ip` variable to the IP address of the server.
2. Run the client script:

    ```bash
    python client.py --server_port 5050
    ```

    The client will connect to the server and start the interaction.

### Notes

- The communication between the client and server agents is text-based, with messages ending with a specific marker `<END_OF_MSG>` to signify the end of a message.
- Both scripts use asynchronous programming to handle communication smoothly.

### Future Improvements

- Enhance the conversation capabilities of the agents.
- Add more robust error handling and logging.
- Implement a secure connection mechanism.

## Contributing

Feel free to fork this project, suggest improvements, or report issues.






---
