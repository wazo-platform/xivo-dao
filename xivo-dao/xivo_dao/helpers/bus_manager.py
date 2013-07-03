from xivo_dao.helpers.notifiers.amqp import publisher

BusPublisher = None


def _init_bus():
    global BusPublisher
    bus_publisher = publisher.AMQPPublisher()
    bus_publisher.connect('localhost', 5672)
    BusPublisher = bus_publisher


def get_publisher():
    global BusPublisher
    if not BusPublisher:
        _init_bus()
    return BusPublisher


def send_bus_command(command):
    publisher = get_publisher()
    publisher.execute_command(command)
