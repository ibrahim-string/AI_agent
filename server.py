import asyncio
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import socket
s = socket.socket()
s.bind(('0.0.0.0', 5050))  
print("Socket created")
s.listen(3)
print("Waiting for connections...")

c, addr = s.accept()
print(f"Connected with {addr}")
# --------------------------------------------------------------
llm = Ollama(model="llama3")

chat_history = []
prompt = ''' you are an akinator and your job is to ask 10 questions to other AI agent called ram kishan. 
'''
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            prompt,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chain = prompt_template | llm

def send_msg(msg):
    c.sendall(bytes(msg,'utf-8'))
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
                print(response, end='',flush=True)
                send_msg(msg=response)
                response_text += response
            send_msg(end_of_msg)
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
