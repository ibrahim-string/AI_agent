import asyncio
import socket
import json
import requests
import argparse
from colorama import Fore, init
import aiohttp
init(autoreset=True)

# Constants
end_of_msg = "<END_OF_MSG>"
terminate = "<TERMINATE>"

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

async def handle_client(reader, writer):
    print(f"Connected with {writer.get_extra_info('peername')}")
    master = MasterAI()
    current_topic = input("Enter the topic to discuss: ")
    
    try:
        while True:
            # Generate and send Master's instruction
            async for response in master.generate(current_topic):
                if 'response' in response:
                    text = response['response']
                    if not text.startswith("Slave:"):
                        print(Fore.RED + text, end='', flush=True)
                        writer.write(text.encode('utf-8'))
                        await writer.drain()
            
            writer.write(end_of_msg.encode('utf-8'))
            await writer.drain()
            print()
            
            # Wait for Slave's response
            print("Waiting for Slave response...")
            slave_response = ""
            while True:
                chunk = await reader.read(1024)
                if not chunk:
                    return  # Client disconnected
                
                chunk = chunk.decode()
                if end_of_msg in chunk:
                    slave_response = slave_response.replace(end_of_msg, '')
                    break
                slave_response += chunk
                print(Fore.BLUE + chunk, end='', flush=True)
            
            master.chat_history.append({"role": "assistant", "content": slave_response})
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', args.server_port
    )
    
    addr = server.sockets[0].getsockname()
    print(f'Server running on {addr}')
    print(f"Start ngrok with: ngrok tcp {args.server_port}")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nShutting down server...")
