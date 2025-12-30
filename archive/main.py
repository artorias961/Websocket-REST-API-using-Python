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


class Handler:
    def __init__(self):
        # Creating the wanted local MAC Address (BLE Device Address) (The default will be the Nordic Device)
        self.ADDRESS = None                                                             #"F8:D7:73:1D:43:08"

        # Creating the wanted local characteristic UUID (The default will be the Nordic Device)
        self.CHARACTERISTIC_UUID = None                                                 # "19b10000e8f2537e4f6cd104768a12ff"
        
        # Storing the client local clients data 
        self.devices_scanner_info = dict()
        self.scanner_api = dict()
        self.devices = list()
        self.mac_address = list()

        # User wanted list for BLE devices
        self.add_device_list = list()

        # Creating the Bluetooth Client 
        self.client = None                                                              # bleak.BleakClient(self.ADDRESS, timeout=5.0)


    async def find_local_ble_devices(self, request):
        """
        Scan local Bluetooth Devices

        :param request: When the user ask for the request
        :return: the status of local Devices MAC Address
        """
        # Letting the user know the server is finding nearby devices
        print("Scanning for 5 seconds, please wait . . .")

        # Discovering local devices in a dictionary format
        self.devices_scanner_info = await bleak.BleakScanner.discover(timeout=5.0, return_adv=True)

        # Creating a counter variable
        counter = 0

        # Letting the USER know that they need to wait for a local scan
        # ahweb.Response(text="Scanning for 5 seconds, please wait . . .")

        # Listing all the data from the scan (Device, MAC Address)
        for dev, addr in self.devices_scanner_info.values():
            # Printing the general information (terminal side)
            print("============================================")
            print(f"\nThe device is: {dev}")
            print("-" * len(str(dev)))
            print(f"\nThe MAC Address is: {addr}")
            print("============================================")

            # Adding the MAC Address to the API
            self.scanner_api[f"Device {counter}"] = dev

            # Increment counter
            counter += 1

        # Dividing the dictionary to its own elements
        self.devices = list(self.devices_scanner_info.keys()) 
        self.mac_address = list(self.devices_scanner_info.items())
        
        # Testing if the command works on the terminal
        print("************************************************************")
        print(self.scanner_api)
        
        return ahweb.Response(text=str(self.scanner_api))

    async def find_wanted_ble_device(self, request):
        """
        The user will be able to implement wanted Device MAC Address

        :param request: When the user ask for the request
        :return: Let the user know the device been added
        """
        # To let the user know what format the MAC Address be
        ble_text_one ="The format for the MAC Address is (Any Numerical Value and/or any character between A-F): \n"
        ble_text_two = "XX:XX:XX:XX:XX:XX \n"
        ble_text_three = "or \n"
        ble_text_four = "XXXXXXXXXXXX \n"
        ble_text_five = "==========================================\n"
        ble_text_all = ble_text_one + ble_text_two + ble_text_three + ble_text_four + ble_text_five

        # Printing the information
        print(ble_text_all)

        # Creating a counter variable
        counter = 0

        # Creating a for loop for to show the user the current existing MAC Address
        for index in self.devices:
            # Incrementing counter
            counter += 1

            # Current device being displayed 
            temp_text = f"Device {counter} : {index}\n"

            # Printing each element 
            print(temp_text)

            # Storing the information 
            ble_text_all += temp_text 

        # Add more to the text for the terminal and API 
        ble_text_all += "==========================================\n"

        # Creating a format for the user
        addr_id = request.match_info.get('addr_id', 'Anonymous')

        # Creating the text for the user
        text = ble_text_all + "{}".format(addr_id)

        # Storing the MAC Address to the self function
        self.ADDRESS = addr_id

        # Adding the MAC Address to the list
        await self.append_info(self.ADDRESS)

        return ahweb.Response(text=text)
        # With the user input, added to the bleak 
        # self.client = await bleak.BleakScanner.find_device_by_address(self.ADDRESS)
    
    async def find_unwanted_ble_device(self, request):
        """
        If the user want to remove a unwanted device

        :param request: When the user ask for the request
        :return: Notify the user a device been removed
        """
        # Creating a empty variable
        all_text = str
        counter = 0

        # Letting the user they have enter the remove a device

        # If the list is empty
        if len(self.add_device_list) == 0:
            # Let the user know that there is nothing to remove
            return ahweb.Response(text="There are no device's been added to the program")
        
        # Else if the current list is only one device
        elif len(self.add_device_list) == 1:
            # Let the user know the there is only one device
            ble_text_one = "You only have one device listed \n"
            ble_text_two = f"Your current device is: {self.add_device_list} \n"
            ble_text_three = "The device will be removed from the program \n"
            ble_text_four = "Your device has been removed \n"
            all_text = ble_text_one + ble_text_two + ble_text_three + ble_text_four
            
            # Removing the element from the list
            self.add_device_list.pop(0)

            # Printing the information on the terminal
            print(all_text)

            return ahweb.Response(text=all_text)
        
        # If the user has mutliple device's in the application
        elif len(self.add_device_list) > 1:
            # Letting the user know that all devices will be disconnected
            all_text = "We are going to disconnect all devices from the application!!!"

            # Printing the information to the terminal
            print(all_text)

            # Clearing the list 
            self.add_device_list.clear()

            return ahweb.Response(text=all_text)

    async def connect_ble_device(self, request):
        """
        If the user add the device already, the user will have the option to connect to the device

        :param request: When the user ask for the request
        :return: a boolean statement if the device connected
        """
        # Attempting to connect the device (specifically GATT Service)
        await self.client.connect()
        
        # To check if the device is connected or not 
        if self.client.is_connected:
            # Letting the user know that the device is connected
            ble_text = "A BLE Device is connected"
            await print(ble_text)
        else:
            # Letting the user know that the device is NOT connected
            ble_text = "Your device is not connected"
            await print(ble_text)

        return ahweb.Response(text=ble_text)
    
    async def disconnect_ble_device(self, request):
        """
        If the user add the device already, the user will have the option to disconnect to a device

        :param request: When the user ask for the request
        :return: a boolean statement if the device disconnected
        """
        # Attempting to disconnect the device
        await self.client.disconnect()

        # To check if the device is connected or not 
        if self.client.is_connected:
            # Letting the user know they are still connected 
            ble_text = "Your Device is still connected"
            await print(ble_text)
        else:
            # Letting the user that the device is disconnected
            ble_text = "Your device disconnected"
            await print(ble_text)
        
        return ahweb.Response(text=ble_text)

    async def list_current_devices(self, request):
        """
        List all current devices that has been added to the application

        :param request: When the user ask for the request
        :return: A list of connected devices
        """
        # If the user ask for device list when empty
        if len(self.add_device_list) == 0:
                # Return a notifications to the user that there is no element/devices in the application
                return ahweb.Response(text="There are no devices to display!!!! Add a device first!!!")
        # Printing all the information of the list of devices
        elif len(self.add_device_list) == 1:
            # Return the current device that is listed
            return ahweb.Response(text=self.ADDRESS)
        elif len(self.add_device_list) > 1:
            # Creating a empty variable
            counter = 0
            all_text = str

            # Printing information to the user
            all_text = "\t \t YOUR CURRENT LIST OF DEVICE'S\n"

            # A for loop to iterate the entire list
            for index in self.add_device_list:
                # Incrementing counter
                counter += 1

                # Current device being displayed 
                temp_text = f"Device {counter} : {index}\n"

                # Printing each element 
                print(temp_text)

                # Storing the information
                all_text += temp_text
            
            return ahweb.Response(text=all_text)


    async def async_user_input(self, prompt: str):
        """
        An option for the application to consider unique request from user

        :param prompt: When the user ask for a specific prompt
        :return: N/A
        """
        return await aioconsole.ainput(prompt)
    
    async def append_info(self, item):
        """
        When called, it will append to a list of secure devices that has or is in the program

        :param item: When the user ask for the request
        :return: a list
        """
        return self.add_device_list.append(item)

    async def handle_general(self, request):
        """
        Lets the user know the base directories for all path's

        :param request: When the user ask for the request
        :return: a long string text
        """
        # Creating a text about all the directories path for the websocket
        general_text_one = "The following directories we have are: \n" 
        general_text_two = "/ \n"
        general_text_three = "/intro \n"
        general_text_four = "/greet \n"
        general_text_five = "/bluetooth \n"
        general_text_six = "/bluetooth/scan_local \n"
        general_text_seven = "/bluetooth/add_device \n"
        general_text_eight = "/bluetooth/remove_device \n"
        general_text_nine = "/bluetooth/list_devices \n"
        general_text_ten = "/bluetooth/connect_device \n"
        general_text_eleven = "/bluetooth/disconnect_device \n"
        general_text_twelve = "/bluetooth/test_device_connection \n"

        # Adding all the text together (had an error where it did not work in one line)
        general_text = (general_text_one + general_text_two + general_text_three + general_text_four + general_text_five 
                        + general_text_six + general_text_seven + general_text_eight + general_text_nine 
                        + general_text_ten + general_text_eleven + general_text_twelve)


        return ahweb.Response(text=general_text)

    async def handle_intro(self, request):
        """
        Informing the user the overall idea of the application

        :param request: When the user ask for the request
        :return: a long string text
        """
        # A small introduction to the user opening the program
        intro_text = "Hello User, welcome to Arty-Chan Application!!! " \
                     "This application is to connect your local device " \
                     "able to control everything through your phone"
        
        return ahweb.Response(text=intro_text)

    async def handle_greeting(self, request):
        """
        Letting the user experiment with custom extensions on to the directory

        :param request: When the user ask for the request
        :return: a custom user text
        """
        # A greeting to the unknown user
        name = request.match_info.get('name', "Anonymous")

        # Combining two text's
        text = "Hello, {}".format(name)

        return ahweb.Response(text=text)
    
    async def handle_bluetooth_general(self, request):
        """
        To notify the user, that they have enable bluetooth mode options

        :param request: When the user ask for the request
        :return: a long string text
        """
        # Letting the user know they have joined the bluetooth section
        ble_intro_text = "Hello user, you have enter the bluetooth section, where you can " \
                         "scan/add/remove/test/list devices a bluetooth device. Where you " \
                         "can do the following: \n" \
                         "/bluetooth \n" \
                         "/bluetooth/scan_local  \n" \
                         "/bluetooth/add_device \n " \
                         "/bluetooth/remove_device \n " \
                         "/bluetooth/connect_device \n " \
                         "/bluetooth/disconnect_device \n " \
                         "/bluetooth/list_devices \n " \
                         "/bluetooth/test_connection \n"

        return ahweb.Response(text=ble_intro_text)
    
    async def handle_bluetooth_scan(self, request):
        """
        Calls the Bleak function to scan local devices

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.find_local_ble_devices(request)
    
    async def handle_bluetooth_add(self, request):
        """
        Calls the Bleak function to add a device

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.find_wanted_ble_device(request)
    
    async def handle_bluetooth_remove(self, request):
        """
        Calls the Bleak function to remove a device

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.find_unwanted_ble_device(request)
    
    async def handle_bluetooth_connect(self, request):
        """
        Calls the Bleak function to connect the device

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.connect_ble_device(request)
    
    async def handle_bluetooth_disconnect(self, request):
        """
        Calls the Bleak function to disconnect the device

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.disconnect_ble_device(request)
    
    async def handle_list_bluetooth_connection(self, request):
        """
        Calls the Bleak function to list all devices on the program

        :param request: When the user ask for the request
        :return: a request
        """
        return await self.list_current_devices(request)
    
    async def handle_test_bluetooth_connection(self, request):
        """
        Calls the Bleak function to send a ping and wait for a response of the device

        :param request: When the user ask for the request
        :return: a request
        """
        return ahweb.Response(text="This feature will be added in future date!!!")

if __name__ == "__main__":
    # Runs the application for the socketweb
    app = ahweb.Application()

    # Calling the handler class
    handler = Handler()

    # Creating directories for the websocket
    app.add_routes([ahweb.get('/', handler.handle_general),
                    ahweb.get('/intro', handler.handle_intro),
                    ahweb.get('/greet/{name}', handler.handle_greeting),
                    ahweb.get('/bluetooth', handler.handle_bluetooth_general),
                    ahweb.get('/bluetooth/scan_local', handler.handle_bluetooth_scan),
                    ahweb.get('/bluetooth/add_device_{addr_id}', handler.handle_bluetooth_add),
                    ahweb.get('/bluetooth/remove_device', handler.handle_bluetooth_remove),
                    ahweb.get('/bluetooth/connect_device', handler.handle_bluetooth_connect),
                    ahweb.get('/bluetooth/disconnect_device', handler.handle_bluetooth_disconnect),
                    ahweb.get('/bluetooth/list_devices', handler.handle_list_bluetooth_connection),
                    ahweb.get('/bluetooth/test_connection', handler.handle_test_bluetooth_connection)])
    
    # A dummy test to see if bluetooth is working or not 
    # asyncio.run(handler.connect_ble_device())

    # Running the entire application
    ahweb.run_app(app)

