#!/usr/bin/env python

import logging
import time
import json
import importlib

from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from cp_push import Checkpoint

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
CONFIG_FILE = "/path/to/config/file"
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Check Point push module import
cppush = importlib.import_module('cp_push')

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    # Create and add event listener
    class MyEventCallback(EventCallback):
        def on_event(self, event):
            try:
                query = event.payload.decode()
                
                query = query[:query.rfind('}')+1]
                query = json.loads(query)
                try:
                    for ips in query['Summary']['Ips']:
                        ipv4 = ips['Ipv4']
                        if not ipv4: pass
                        else: Checkpoint(ipv4)
                except: pass
 
            except Exception as error:
                print(error)

        @staticmethod
        def worker_thread(req):
            client.sync_request(req)

    # Register the callback with the client
    client.add_event_callback('#', MyEventCallback(), subscribe_to_topic=False)
    client.subscribe("/mcafee/event/atd/file/report")

    # Wait forever
    while True:
        time.sleep(60)

