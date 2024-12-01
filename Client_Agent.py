import socket
import asyncio
import argparse
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from colorama import Fore, init
init(autoreset=True)

def llm_init():
    llm = Ollama(model="llama3.2:1b-instruct-q4_K_S")
    prompt = '''You are the Slave AI. Your role is to execute the Master's instructions precisely.
    Always start with "Slave:" followed by the execution of the given instruction.
    Never give instructions.
    Never act as the Master.
    Simply execute what is commanded.'''
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    return prompt_template | llm

# Parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run client with specified server port")
    parser.add_argument('--server_port', type=int, default=5050, help='Port number to connect to the server')
    args = parser.parse_args()
    return args.server_port

# Initialize connection
server_ip = '0.tcp.in.ngrok.io' 
server_port = parse_arguments() 
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((server_ip, server_port))

# Initialize chain
chain = llm_init()

# Other variables
end_of_msg = "<END_OF_MSG>"
terminate = "<TERMINATE>"

def send_msg(msg):
    msg_with_color = msg
    c.sendall(msg_with_color.encode('utf-8'))

async def start_app():
    chat_history = []
    
    while True:
        # Receive Master's instruction
        print(f"Receiving Master's instruction: ")
        master_instruction = "" 
        while True:
            chunk = c.recv(1024).decode()
            if terminate in chunk:
                chain = llm_init()
                chat_history = []
                break
            master_instruction += chunk
            if end_of_msg in master_instruction:
                master_instruction = master_instruction.replace(end_of_msg, '')
                break
            print(Fore.RED + chunk, end='', flush=True)
        print()
        
        # Add Master's instruction to chat history
        chat_history.append(SystemMessage(content=master_instruction))
        
        # Generate and send Slave's response
        response_stream = chain.astream({"input": master_instruction, "chat_history": chat_history})
        slave_response = ""
        
        async for r in response_stream:
            print(Fore.BLUE + r, end='', flush=True)
            send_msg(msg=r)
            slave_response += r
                
        # Add Slave's response to chat history
        chat_history.append(HumanMessage(content=slave_response))
        send_msg(end_of_msg)
        print()

if __name__ == "__main__":
    asyncio.run(start_app())


# ngrok tcp 5050
