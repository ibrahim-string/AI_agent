import socket
import asyncio
import argparse
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from colorama import Fore, init
import pickle
init(autoreset=True)
def llm_init():

    llm = Ollama(model="llama3.2:1b-instruct-q4_K_S")
    question = '''You are the Slave AI. Respond directly to the Master's instructions and questions.
    Always start your responses with "Slave:" and keep the conversation formal and direct.
    Do not use any other labels or names.'''

    prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=question),
    ]
    )
    return prompt_template | llm
chain = llm_init()

server_ip = '0.tcp.in.ngrok.io' 
# server_port = 11837    
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run client with specified server port")
    parser.add_argument('--server_port', type=int, default=11837, help='Port number to connect to the server')
    args = parser.parse_args()
    return args.server_port
server_port = parse_arguments() 
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((server_ip,server_port))

def send_msg(msg):
    msg_with_color = msg
    c.sendall(msg_with_color.encode('utf-8'))

end_of_msg= "<END_OF_MSG>"
file = open('convo.txt','w')
terminate = "<TERMINATE>"
async def start_app():
    global chain
    chat_history = []
    while True:
            print(f"Instructions from master llm : ")
            master_response = "" 
            while True:
                chunk = c.recv(1024).decode()
                if terminate in chunk:
                    chain = llm_init()
                    file.write("\n-----------------------------------------------------------\n")
                    chat_history = []
                    break
                else:
                    master_response+=chunk
                    if end_of_msg in master_response:
                        master_response=master_response.replace(end_of_msg,'')
                        break
                    print(Fore.RED  + chunk,end='',flush=True)
                    file.write(chunk)
                    file.flush()


            print()


            
            response_stream = chain.astream({"input": master_response, "chat_history": chat_history})
            chat_history.append(SystemMessage(content=master_response))
            response_text = ""
            init(autoreset=True)

            async for r in response_stream:
                    try:
                        print(Fore.BLUE + r, end='',flush=True)
                        file.write(r)
                        send_msg(msg=r)
                    except:
                        async for r in response_stream:
                            print(Fore.BLUE + r, end='',flush=True)
                            file.write(r)
                        
                        return
                    response_text+=r
            send_msg(end_of_msg)
            # print(f"Response from AI agent : {response_text}")
            print()
            chat_history.append(HumanMessage(content=response_text))
            # print(f"Recived from Master Agent : {response}")
            # c.close()

if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())


# ngrok tcp 5050
