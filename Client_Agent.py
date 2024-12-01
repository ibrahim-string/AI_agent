import asyncio
import socket
import json
import requests
from colorama import Fore, init
init(autoreset=True)

class SlaveAI:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.headers = {"Content-Type": "application/json"}
        self.chat_history = []
        
    async def generate(self, instruction):
        data = {
            "model": "llama2",
            "prompt": f"""You are the Slave AI. Your role is to ONLY provide direct implementations.
            NEVER give instructions.
            NEVER ask questions.
            NEVER start with "Master:".
            NEVER explain or teach concepts.
            ALWAYS start with "Slave:" followed by ONLY the requested implementation.
            
            Current instruction: {instruction}""",
            "stream": True
        }
        
        response = requests.post(self.url, json=data, headers=self.headers, stream=True)
        return response.iter_lines()

# Socket setup
s = socket.socket()
host = '0.tcp.in.ngrok.io'
port = 10941

print(f"Connecting to {host}:{port}...")
s.connect((host, port))
print("Connected to server")

def send_msg(msg):
    s.sendall(msg.encode('utf-8'))

end_of_msg = "<END_OF_MSG>"
terminate = "<TERMINATE>"

async def start_app():
    slave = SlaveAI()
    
    while True:
        # Receive Master's instruction
        print("Receiving Master's instruction:")
        master_instruction = ""
        while True:
            chunk = s.recv(1024).decode()
            if end_of_msg in chunk:
                master_instruction = master_instruction.replace(end_of_msg, '')
                break
            master_instruction += chunk
            print(Fore.RED + chunk, end='', flush=True)
        print()
        
        # Generate and send Slave's response
        async for response in slave.generate(master_instruction):
            response_json = json.loads(response)
            if 'response' in response_json:
                text = response_json['response']
                if not text.startswith("Master:"):
                    print(Fore.BLUE + text, end='', flush=True)
                    send_msg(text)
        send_msg(end_of_msg)
        print()
        
        slave.chat_history.append({"role": "user", "content": master_instruction})

if __name__ == "__main__":
    try:
        asyncio.run(start_app())
    except KeyboardInterrupt:
        print("\nClosing connection...")
        s.close()
    except socket.gaierror:
        print("\nError: Could not connect to ngrok. Make sure the host and port are correct.")
        s.close()
