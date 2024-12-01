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
    client_addr = writer.get_extra_info('peername')
    print(f"\n[+] New client connected from {client_addr}")
    master = MasterAI()
    
    print("\n[*] Enter the topic to discuss (or press Ctrl+C to exit):")
    current_topic = input("> ")
    print(f"\n[*] Starting conversation about: {current_topic}")
    
    try:
        while True:
            print("\n[*] Generating Master's instruction...")
            # Generate and send Master's instruction
            async for response in master.generate(current_topic):
                if 'response' in response:
                    text = response['response']
                    if not text.startswith("Slave:"):
                        print(Fore.RED + text, end='', flush=True)
                        writer.write(text.encode('utf-8'))
                        await writer.drain()
            
            print("\n[*] Sending end of message marker...")
            writer.write(end_of_msg.encode('utf-8'))
            await writer.drain()
            
            # Wait for Slave's response
            print("\n[*] Waiting for Slave response...")
            slave_response = ""
            while True:
                chunk = await reader.read(1024)
                if not chunk:
                    print(f"\n[-] Client {client_addr} disconnected")
                    return
                
                chunk = chunk.decode()
                if end_of_msg in chunk:
                    slave_response = slave_response.replace(end_of_msg, '')
                    break
                slave_response += chunk
                print(Fore.BLUE + chunk, end='', flush=True)
            
            print("\n[+] Received complete response from Slave")
            master.chat_history.append({"role": "assistant", "content": slave_response})
    
    except Exception as e:
        print(f"\n[-] Error handling client {client_addr}: {e}")
    finally:
        print(f"\n[-] Closing connection with {client_addr}")
        writer.close()
        await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', args.server_port
    )
    
    addr = server.sockets[0].getsockname()
    print(f'\n[+] Server started successfully')
    print(f'[+] Listening on {addr}')
    print(f'[*] To make server public, run: ngrok tcp {args.server_port}')
    print('\n[*] Waiting for client connections... Press Ctrl+C to exit\n')
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nShutting down server...")
