import asyncio
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from colorama import Fore, init
import socket
init(autoreset=True)

s = socket.socket()
s.bind(('0.0.0.0', 5050))  
print("Socket created")
s.listen(3)
print("Waiting for connections...")

c, addr = s.accept()
print(f"Connected with {addr}")
# --------------------------------------------------------------
llm = Ollama(model="llama3")
# llm = Ollama(model="llama3", endpoint="https://6cac-2406-7400-51-1e22-88f4-684f-cfab-676e.ngrok-free.app")

chat_history = []
prompt = '''You are Jack master AI agent, your job is only give instructions to your slave AI agent John.'''
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            prompt,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        # ("human", "{input}"),
    ]
)

chain = prompt_template | llm

def send_msg(msg):
    msg_with_color = Fore.RED + msg
    c.sendall(msg_with_color.encode('utf-8'))
end_of_msg= "<END_OF_MSG>"
async def start_app():
    question = input("You: ")
    count=0
    while True:
        if count==0:
            if question.lower() == "/bye":
                return

            response_stream = chain.astream({"input": question, "chat_history": chat_history})
            chat_history.append(HumanMessage(content=question))

            response_text = ""
            async for response in response_stream:
                print(Fore.RED + response, end='',flush=True)
                send_msg(msg=response)
                response_text += response
            send_msg(Fore.RED + end_of_msg)
            print()  
            chat_history.append(AIMessage(content=response_text))
        else: 
            # data = c.recv(1024).decode()
            print(f"AI agent llm : ")
            agent_response = "" 
            while True: 
                # print("*",end='')
                chunk = c.recv(1024).decode()
                agent_response+=chunk
                if end_of_msg in agent_response:
                    agent_response=agent_response.replace(end_of_msg,'')
                    break
                print(chunk,end='',flush=True)

            print()
            print('-------------------------------------------------')
            
            response_stream = chain.astream({"input": agent_response, "chat_history": chat_history})
            chat_history.append(HumanMessage(content=question))

            response_text = ""

            async for response in response_stream:
                print(response, end='',flush=True)
                send_msg(msg=response)
                response_text += response
            send_msg(end_of_msg)
            print()  
            chat_history.append(AIMessage(content=response_text))
        count= count+ 1

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
