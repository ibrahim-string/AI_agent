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
    Do not ask open-ended questions about what the Slave wants to do.
    Do not ask for the Slave's opinion or preferences.
    Focus on giving clear directives related to the topic at hand.'''
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt),
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
                if count >= 3:  # You can adjust this number
                    # Send concluding instruction
                    conclusion_prompt = '''Master: Provide a final conclusion about our discussion on this topic. This will end our current conversation.'''
                    
                    response_stream = chain.astream({"input": conclusion_prompt, "chat_history": chat_history})
                    response_text = ""
                    async for response in response_stream:
                        print(Fore.RED + response, end='', flush=True)
                        send_msg(msg=response)
                        response_text += response
                    send_msg(end_of_msg)
                    
                    # Send termination signal
                    send_msg(msg=terminate)
                    print(Fore.YELLOW + "\nConversation concluded. Moving to next topic...")
                    chain = llm_init()
                    chat_history = []
                    break
                
                # Your existing time-based termination
                if time.time() - start_time > 60:
                    send_msg(msg=terminate)
                    print(Fore.YELLOW + "Time exceeded 180 seconds, reinitializing llm...")
                    chain = llm_init()
                    chat_history = []
                    start_time = time.time()
                    break

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())
