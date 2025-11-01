import configparser
import os


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser(interpolation=None)
        config_file = "config/config.ini"

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found")

        self.config.read(config_file)

    def get_mqtt_config(self):
        return {
            "broker": self.config["MQTT"]["broker"],
            "username": self.config["MQTT"]["username"],
            "password": self.config["MQTT"]["password"],
            "topic_command": self.config["MQTT"]["topic_command"],
            "topic_state": self.config["MQTT"]["topic_state"]
        }

    def get_mqtt_broker(self) -> str:
        return self.config["MQTT"]["broker"]

    def get_mqtt_username(self) -> str:
        return self.config["MQTT"]["username"]

    def get_mqtt_password(self) -> str:
        return self.config["MQTT"]["password"]

    def get_mqtt_topic_command(self) -> str:
        return self.config["MQTT"]["topic_command"]

    def get_mqtt_topic_state(self) -> str:
        return self.config["MQTT"]["topic_state"]

    def get_coop_light_dim_config(self) -> dict[str, int]:
        return {
            "dim_pin": self.get_coop_light_dim_pin(),
            "dusk_endurance": self.get_coop_light_dusk_endurance(),
            "dusk_steps": self.get_coop_light_dusk_steps(),
            "dawn_endurance": self.get_coop_light_dawn_endurance(),
            "dawn_steps": self.get_coop_light_dawn_steps()
        }

    def get_coop_light_dim_pin(self) -> int:
        return int(self.config["COOP_LIGHT"]["dim_pin"])

    def get_coop_light_dusk_endurance(self) -> int:
        return int(self.config["COOP_LIGHT"]["dusk_endurance"])

    def get_coop_light_dusk_steps(self) -> int:
        return int(self.config["COOP_LIGHT"]["dusk_steps"])

    def get_coop_light_dawn_endurance(self) -> int:
        return int(self.config["COOP_LIGHT"]["dawn_endurance"])

    def get_coop_light_dawn_steps(self) -> int:
        return int(self.config["COOP_LIGHT"]["dawn_steps"])

    def get_coop_light_logging(self) -> dict:
        return {
            "logfile": self.config["COOP_LIGHT_LOGGING"]["logfile"],
            "level": self.config["COOP_LIGHT_LOGGING"]["level"]
        }

    def get_coop_light_logging_logfile(self) -> str:
        return self.config["COOP_LIGHT_LOGGING"]["logfile"]

    def get_coop_light_logging_level(self) -> str:
        return self.config["COOP_LIGHT_LOGGING"]["level"]

    def get_coop_light_logging_message_format(self) -> str:
        return self.config["COOP_LIGHT_LOGGING"]["message_format"]

    def get_coop_light_logging_date_time_format(self) -> str:
        return self.config["COOP_LIGHT_LOGGING"]["date_time_format"]
