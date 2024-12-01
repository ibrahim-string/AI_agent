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
    # llm = Ollama(model="llama3", endpoint="https://6cac-2406-7400-51-1e22-88f4-684f-cfab-676e.ngrok-free.app")

    prompt = '''You are Jack master AI agent, your job is only to give instructions to your slave AI agent John.'''
    # prompt_template = ChatPromptTemplate.from_messages(
    #     [
    #         (
    #             "system",
    #             prompt,
    #         ),
    #         MessagesPlaceholder(variable_name="chat_history"),
    #         # ("human", "{input}"),
    #     ]
    # )
    prompt_template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=prompt),
        ]
    )
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
    for category, topics_list in loaded_topics.items():
        start_time = time.time()
        for topic in topics_list:

            question = f'''
                        You are a Master LLM collaborating with a Slave LLM. Your task is to engage in a structured conversation on the topic: **{topic}**. 

                            Guidelines:
                            1. Begin by briefly introducing the topic.
                            2. Share perspectives, insights, or questions to explore the topic in depth.
                            3. Challenge each other's ideas with logical or creative extensions.
                            4. Collaborate to provide actionable insights, recommendations, or conclusions.
                            5. Avoid hallucinations or incorrect information.

                            Begin the dialogue now.
                        '''
            count=0
            chain = llm_init()
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
                    send_msg(end_of_msg)
                    print()  
                    chat_history.append(SystemMessage(content=response_text))
                else: 
                    # data = c.recv(1024).decode()
                    print(f"AI agent llm: ")
                    agent_response = "" 
                    while True: 
                        # print("*",end='')
                        chunk = c.recv(1024).decode()
                        agent_response+=chunk
                        if end_of_msg in agent_response:
                            agent_response=agent_response.replace(end_of_msg,'')
                            break
                        print(Fore.BLUE + chunk,end='',flush=True)

                    print()
                    print('-------------------------------------------------')
                    
                    response_stream = chain.astream({"input": agent_response, "chat_history": chat_history})
                    chat_history.append(HumanMessage(content=question))

                    response_text = ""

                    async for response in response_stream:
                        print(Fore.RED + response, end='',flush=True)
                        send_msg(msg=response)
                        response_text += response
                    send_msg(end_of_msg)
                    print()  
                    chat_history.append(HumanMessage(content=response_text))
                count= count+ 1
                if time.time() - start_time > 180:
                    # c.close()
                    send_msg(msg=terminate)
                    print(Fore.YELLOW + "Time exceeded 60 seconds reinitializing llm...")
                    chain = llm_init()
                    chat_history = []
                    start_time = time.time()
                    
                    break

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
