from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink
import asyncio
import threading
import time

class CustomHandler(Sink):
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

def run_smtp_server():
    handler = CustomHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    print(f'SMTP Server running on {controller.hostname}:{controller.port}')
    return controller

# Start server in a separate thread
def start_smtp_server():
    controller = run_smtp_server()
    time.sleep(1)  # Give server time to start
    return controller

if __name__ == '__main__':
    controller = start_smtp_server()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
