######################################################
###          Home Assistant BLE Adventure          ###
###                 Arty-Chan T-T                  ###
######################################################          
import asyncio
import bleak
import aiohttp as ah
import aiohttp.web as ahweb
import aioconsole
import argparse

class DeviceBLEOne:
    def __init__(self):
        pass

    async def handle_greet_device(self, request):
        return await ahweb.Response(text="Hello, this is device one")
    
    async def handle_respond(self):
        pass
    

if __name__ == "__main__":
    # Runs the application for the socketweb
    app = ahweb.Application()

    # Calling the handler class
    handler_device = DeviceBLEOne()

    # Creating directories for the websocket
    app.add_routes([ahweb.get('/', handler_device.handle_greet_device),
                    ahweb.get('/device', handler_device.handle_respond)])

    # Running the entire application
    ahweb.run_app(app)