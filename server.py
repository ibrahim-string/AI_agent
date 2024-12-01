import asyncio
import socket
import json
import requests
import argparse
from colorama import Fore, init
import aiohttp
init(autoreset=True)

# Add argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--server_port', type=int, default=10941)
args = parser.parse_args()

class MasterAI:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.headers = {"Content-Type": "application/json"}
        self.chat_history = []
        
    async def generate(self, topic):
        data = {
            "model": "llama2",
            "prompt": f"""You are the Master AI. Your role is to ONLY give instructions and questions.
            NEVER provide implementations or code.
            NEVER explain concepts.
            NEVER start with "Slave:".
            ALWAYS start with "Master:" followed by a clear instruction or question.
            
            Current topic: {topic}""",
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=data, headers=self.headers) as response:
                async for line in response.content:
                    if line:
                        yield json.loads(line)

# Socket setup
s = socket.socket()
s.bind(('0.0.0.0', args.server_port))
print(f"Socket created on port {args.server_port}")
print("Start ngrok with: ngrok tcp {args.server_port}")
s.listen(3)
print("Waiting for connections...")

c, addr = s.accept()
print(f"Connected with {addr}")

def send_msg(msg):
    c.sendall(msg.encode('utf-8'))

end_of_msg = "<END_OF_MSG>"
terminate = "<TERMINATE>"

async def start_app():
    master = MasterAI()
    current_topic = input("Enter the topic to discuss: ")
    
    while True:
        # Generate and send Master's instruction
        async for response in master.generate(current_topic):
            response_json = json.loads(response)
            if 'response' in response_json:
                text = response_json['response']
                if not text.startswith("Slave:"):
                    print(Fore.RED + text, end='', flush=True)
                    send_msg(text)
        send_msg(end_of_msg)
        print()
        
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
        
        master.chat_history.append({"role": "assistant", "content": slave_response})

if __name__ == "__main__":
    asyncio.run(start_app())
