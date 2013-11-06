# -*- coding: utf-8 -*-

from xivo_bus.ctl.client import BusCtlClient

bus_client = None


def _init_bus():
    global bus_client
    bus_client = BusCtlClient()
    bus_client.connect()
    bus_client.declare_xivo_exchange()


def send_bus_command(command):
    # TODO rename to send_bus_event
    if bus_client is None:
        _init_bus()
    bus_client.publish_xivo_event(command)
