import asyncio
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from colorama import Fore, init
import socket
import time
import pickle
init(autoreset=True)

s = socket.socket()
s.bind(('0.0.0.0', 5050))  
print("Socket created")
s.listen(3)
print("Waiting for connections...")

c, addr = s.accept()
print(f"Connected with {addr}")
# --------------------------------------------------------------
def llm_init():
    llm = Ollama(model="llama3.2:1b-instruct-q4_K_S")
    prompt = '''You are the Master AI. Your role is to give clear, direct instructions to the Slave AI about the given topics. 
    Always start with "Master:" followed by a specific instruction or task.
    Stay focused on the current topic only.
    Give step-by-step instructions related to the topic.
    Do not respond as the Slave.
    Do not ask questions - only give instructions.
    
    For example:
    Master: Explain the basic structure of a linked list node.
    [Wait for Slave response]
    Master: Now implement the node structure in C code.
    [Wait for Slave response]
    Master: Add a function to create a new node.'''
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    return prompt_template | llm
file = open('convo.txt','w')

with open("topics.pkl", "rb") as file:
    loaded_topics = pickle.load(file)
def send_msg(msg):
    msg_with_color = msg
    c.sendall(msg_with_color.encode('utf-8'))
end_of_msg= "<END_OF_MSG>"
terminate = "<TERMINATE>"
async def start_app():
    global chain
    chat_history = []
    
    while True:
        # Generate and send Master's instruction
        response_stream = chain.astream({"input": question, "chat_history": chat_history})
        master_instruction = ""
        
        async for response in response_stream:
            print(Fore.RED + response, end='', flush=True)
            send_msg(msg=response)
            master_instruction += response
        send_msg(end_of_msg)
        print()
        
        # Add Master's instruction to chat history
        chat_history.append(SystemMessage(content=master_instruction))
        
        # Wait for Slave's response
        print(f"Waiting for Slave response: ")
        slave_response = ""
        while True:
            chunk = c.recv(1024).decode()
            if end_of_msg in chunk:
                slave_response = slave_response.replace(end_of_msg, '')
                break
            slave_response += chunk
            print(Fore.BLUE + chunk, end='', flush=True)
        
        # Add Slave's response to chat history
        chat_history.append(HumanMessage(content=slave_response))
        print()

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
