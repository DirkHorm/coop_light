import time
import paho.mqtt.client as mqtt
from gpiozero import PWMLED
import logging
import logging.handlers

from misc.config_loader import Config
from misc.coop_light_command import CoopLightCommand

dim_pwm_pin: int
dim_cancel: bool

CANCEL_SLEEP_TIME = 0.1

DUSK_START_VALUE = 0.1
LIGHT_ON_VALUE = 0.7
LIGHT_OFF_VALUE = 0.0
DAWN_START_VALUE = 0.6

cfg = Config()
MQTT_COMMAND_TOPIC = cfg.get_mqtt_topic_command()
MQTT_COOP_LIGHT_STATE_TOPIC = cfg.get_mqtt_topic_state()

DIM_PIN = cfg.get_coop_light_dim_pin()

DAWN_ENDURANCE = cfg.get_coop_light_dawn_endurance()
DAWN_STEPS = cfg.get_coop_light_dawn_steps()

DUSK_ENDURANCE = cfg.get_coop_light_dusk_endurance()
DUSK_STEPS = cfg.get_coop_light_dusk_steps()

def dim(start: float, end: float, steps: int, endurance: int) -> None:
    """
    Dims the light from start to end with the number of given steps length of endurance
    :param start: the start value 0|1
    :param end: the end value 0|1
    :param steps: The number of steps to dim / simulate dusk|dawn
    :param endurance: the endurance each step takes
    """
    global dim_cancel
    dim_cancel = False
    step_time = endurance / steps
    log(f'Starting to generate and set dim steps / values')
    for i in range(steps + 1):
        if dim_cancel:
            log(f'Dimming cancelled')
            break
        if start < end:
            current_dim_value = round(start + (end - start) * (i / steps), 2)
        else:
            current_dim_value = round(start - (start - end) * (i / steps), 2)
        set_light_value(current_dim_value)
        log(f'Keeping dim step for {step_time} seconds')
        time.sleep(step_time)

def set_light_value(value: float) -> None:
    log(f'Setting light value {value}')
    dim_pwm_pin.value = value


def start_dimming(direction: str) -> None:
    f"""
    Starts a new dimming in the given direction
    :param direction: dusk|dawn
    """
    global dim_cancel

    # Cancel a currently running dimming, in case there's one
    dim_cancel = True
    # Wait for a short time in case it's currently dimming
    time.sleep(CANCEL_SLEEP_TIME)

    if CoopLightCommand.DAWN.name == direction:
        log(f'Starting dawn dimming')
        dim(DAWN_START_VALUE, LIGHT_OFF_VALUE, DAWN_STEPS, DAWN_ENDURANCE)
        log(f'Successfully dawn dimmed')
    elif CoopLightCommand.DUSK.name == direction:
        log(f'Starting dusk dimming')
        dim(DUSK_START_VALUE, LIGHT_ON_VALUE, DUSK_STEPS, DUSK_ENDURANCE)
        log(f'Successfully dusk dimmed')
    elif CoopLightCommand.ON.name == direction:
        log(f'Switching light ON')
        set_light_value(1.0)
    elif CoopLightCommand.OFF.name == direction:
        log(f'Switching light OFF')
        set_light_value(0.0)

def on_connect(client, userdata, flags, result_code, properties) -> None:
    client.subscribe(MQTT_COMMAND_TOPIC)
    client.subscribe(MQTT_COOP_LIGHT_STATE_TOPIC)
    log(f'Connected to mqtt broker and topic {MQTT_COMMAND_TOPIC}')

def on_message(client, userdata, msg) -> None:
    payload = msg.payload.decode().upper()
    log(f'Message received with payload {payload}')
    if CoopLightCommand.has_command(payload):
        log(f'Starting to dim')
        start_dimming(payload)
    else:
        log(f'Unknown payload {payload}')


def setup_logging() -> None:
    log_handler = logging.handlers.WatchedFileHandler(cfg.get_coop_light_logging_logfile())
    formatter = logging.Formatter(
        cfg.get_coop_light_logging_message_format(),
        cfg.get_coop_light_logging_date_time_format()
    )
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(cfg.get_coop_light_logging_level())


def log(message: str, *args, level: int = logging.INFO, exc=None) -> None:
    if exc:
        logging.log(level, message, *args, exc_info=exc)
    else:
        logging.log(level, message, *args)

def init_pins() -> None:
    global dim_pwm_pin
    dim_pwm_pin = PWMLED(DIM_PIN)

def main() -> None:
    setup_logging()
    client = None
    global dim_cancel

    try:
        init_pins()

        log('Connecting to mqtt')
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        log('Mqtt client created')
        client.username_pw_set(cfg.get_mqtt_username(), cfg.get_mqtt_password())
        log('Mqtt username and password set')
        client.on_connect = on_connect
        client.on_message = on_message
        log('Trying to connect to Mqtt server')
        client.connect(cfg.get_mqtt_broker())
        log('Connected to Mqtt server')
        client.loop_forever(retry_first_connection=False)
    except KeyboardInterrupt:
        dim_cancel = True
        log('coop_light.py stopped by keyboard interrupt')
        pass
    except Exception as err:
        dim_cancel = True
        log('coop_light.py broke with exception', level=logging.ERROR, exc=err)
    finally:
        if client:
            client.unsubscribe(MQTT_COMMAND_TOPIC)
            client.unsubscribe(MQTT_COOP_LIGHT_STATE_TOPIC)
            client.disconnect()
        dim_pwm_pin.off()
        log('Finishing coop light script')

if __name__ == '__main__':
    main()
