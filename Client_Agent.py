import socket
import asyncio
import argparse
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from colorama import Fore, init
init(autoreset=True)

llm = Ollama(model="codellama")

chat_history = []

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Your are John slave AI coder, Your job is to listen to your master jack and generate the best code with good comments.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        # ("human", "{input}"),
    ]
)

chain = prompt_template | llm

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
    msg_with_color = Fore.BLUE + msg
    c.sendall(msg_with_color.encode('utf-8'))

end_of_msg= "<END_OF_MSG>"

async def start_app():
    while True:
        print(f"Instructions from master llm : ")
        master_response = "" 
        while True: 
            chunk = c.recv(1024).decode()
            master_response+=chunk
            if end_of_msg in master_response:
                master_response=master_response.replace(end_of_msg,'')
                break
            print(chunk,end='',flush=True)

        print()
        if master_response == "/bye":
            return

        
        response_stream = chain.astream({"input": master_response, "chat_history": chat_history})
        chat_history.append(HumanMessage(content=master_response))
        response_text = ""
        init(autoreset=True)

        async for r in response_stream:
                print(Fore.BLUE + r, end='',flush=True)
                send_msg(msg=r)
                response_text+=r
        send_msg(end_of_msg)
        print(f"Response from AI agent : {response_text}")
        print()
        chat_history.append(AIMessage(content=response_text))
        # print(f"Recived from Master Agent : {response}")
        # c.close()
if __name__ == "__main__":
    # while True:
        asyncio.run(start_app())


# ngrok tcp 5050
