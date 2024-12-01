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
    prompt = '''You are the Slave AI. Your role is to ONLY provide direct implementations.
    NEVER give instructions.
    NEVER ask questions.
    NEVER start with "Master:".
    NEVER explain or teach concepts.
    ALWAYS start with "Slave:" followed by ONLY the requested implementation.
    
    If asked for code: provide only the code.
    If asked for output: provide only the output.
    No explanations.
    No tutorials.
    No additional information.'''
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("assistant", "{input}")
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
    global chain
    chat_history = []
    chain = llm_init()
    
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
        
        # Add Master's instruction to chat history as SystemMessage
        if master_instruction:  # Only add if there's a message
            chat_history.append(SystemMessage(content=master_instruction))
        
        # Generate and send Slave's response
        response_stream = chain.astream({"input": master_instruction, "chat_history": chat_history})
        slave_response = "Slave: "  # Start with single prefix
        response_chunks = []
        
        async for r in response_stream:
            if not r.startswith("Master:"):  # Prevent any Master responses
                response_chunks.append(r)
                print(Fore.BLUE + r, end='', flush=True)
        
        # Combine all chunks and send as one message
        complete_response = slave_response + ''.join(response_chunks)
        send_msg(msg=complete_response)
                
        # Add Slave's response to chat history as AssistantMessage
        chat_history.append(SystemMessage(content=complete_response))
        send_msg(end_of_msg)
        print()

if __name__ == "__main__":
    asyncio.run(start_app())


# ngrok tcp 5050
