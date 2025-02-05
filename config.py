import logging
import yaml
import os

class Config:
    def __init__(self, config_file="config.yaml"):
        self.config = self.load_config(config_file)
        self.config_logger()

    def load_config(self, filename):
        with open(filename, "r") as file:
            config = yaml.safe_load(file)
        return config
    
    def config_logger(self):
        log_path = os.path.dirname(self.config["log"]["log_file"])
        if log_path and not os.path.exists(log_path):
            os.makedirs(log_path)

        logging.basicConfig(
            filename=self.config["log"]["log_file"],
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )