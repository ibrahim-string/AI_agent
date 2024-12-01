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
    Reference previous responses when giving new instructions.
    Build upon the Slave's previous answers.
    
    For example:
    Master: Explain the basic structure of a linked list node.
    Slave: [Previous response about node structure]
    Master: Based on the node structure you described, explain how to connect two nodes together.'''
    
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
    start_time = time.time()
    
    question = input("Enter your question: ")
    count = 0
    chain = llm_init()
    
    while True:
        if question.lower() == "/bye":
            return

        # Master generates initial instruction
        response_stream = chain.astream({"input": question, "chat_history": chat_history})
        chat_history.append(HumanMessage(content=question))
        response_text = ""
        
        # Send Master's instruction
        async for response in response_stream:
            print(Fore.RED + response, end='', flush=True)
            send_msg(msg=response)
            response_text += response
        send_msg(end_of_msg)
        print()
        
        chat_history.append(SystemMessage(content=response_text))
        
        # Receive Slave's response
        print(f"Waiting for Slave response: ")
        slave_response = ""
        while True:
            chunk = c.recv(1024).decode()
            slave_response += chunk
            print(Fore.BLUE + chunk, end='', flush=True)
            if end_of_msg in slave_response:
                slave_response = slave_response.replace(end_of_msg, '')
                break
        
        # Add Slave's response to chat history
        chat_history.append(HumanMessage(content=slave_response))
        
        count += 1
        if count >= 3:
            # Send concluding instruction
            conclusion_prompt = "Master: Provide a final conclusion about our discussion on this topic. This will end our current conversation."
            response_stream = chain.astream({"input": conclusion_prompt, "chat_history": chat_history})
            response_text = ""
            async for response in response_stream:
                print(Fore.RED + response, end='', flush=True)
                send_msg(msg=response)
                response_text += response
            send_msg(end_of_msg)
            send_msg(msg=terminate)
            
            print(Fore.YELLOW + "\nConversation concluded. Moving to next topic...")
            chain = llm_init()
            chat_history = []
            break
        
        # Check time limit
        if time.time() - start_time > 180:
            send_msg(msg=terminate)
            print(Fore.YELLOW + "Time exceeded 180 seconds, reinitializing llm...")
            chain = llm_init()
            chat_history = []
            start_time = time.time()
            break

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
