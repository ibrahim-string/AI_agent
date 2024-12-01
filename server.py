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
    prompt = '''You are the Master AI. Your role is to ONLY give instructions and questions.
    NEVER provide implementations or code.
    NEVER explain concepts.
    NEVER start with "Slave:".
    ALWAYS start with "Master:" followed by a clear instruction or question.
    
    Keep instructions simple and direct.
    One task at a time.
    No explanations or tutorials.'''
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("assistant", "{input}")
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
    
    current_topic = input("Enter the topic to discuss: ")
    chain = llm_init()
    
    while True:
        # Generate Master's instruction
        master_prompt = f"Give a clear instruction about: {current_topic}"
        response_stream = chain.astream({
            "input": master_prompt,
            "chat_history": chat_history
        })
        
        # Send Master's instruction
        master_instruction = ""
        async for response in response_stream:
            if not response.startswith("Slave:"):  # Prevent any Slave responses
                print(Fore.RED + response, end='', flush=True)
                send_msg(msg=response)
                master_instruction += response
        send_msg(end_of_msg)
        print()
        
        # Add Master's instruction to chat history
        chat_history.append(SystemMessage(content=master_instruction))
        
        # Wait for Slave's response
        print("Waiting for Slave response...")
        slave_response = ""
        while True:
            chunk = c.recv(1024).decode()
            if end_of_msg in chunk:
                slave_response = slave_response.replace(end_of_msg, '')
                break
            slave_response += chunk
            print(Fore.BLUE + chunk, end='', flush=True)
        
        # Add Slave's response to chat history
        chat_history.append(SystemMessage(content=slave_response))

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
