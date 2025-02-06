from scapy.all import *
import json
from config import Config
from services.mail import Mailer
import threading
from utils import get_time_string

arptable : dict = {}

conf.sniff_promisc = True

config = Config("config.yaml")
mailer = Mailer(config)

arpfile = config.config["log"]["arp_table"]
INTERFACE = config.config["network"]["sniff_iface"]

logging.info("==========PROGRAM RESTART==========")

#load dict from json
try:
    with open("data/arp_table.json", "r") as file:
        arptable = json.load(file)
        logging.info("ARP table loaded from disk")

except FileNotFoundError:
    logging.warning("ARP table file not found. Starting with an empty table.")

except json.JSONDecodeError:
    logging.error("Error decoding JSON from ARP table file. Starting fresh.")


stop_event = threading.Event()
def save_arp_table(interval=30): #Default 30s between saves
    while not stop_event.is_set():
        with open(arpfile, "w") as file:
            json.dump(arptable, file, indent=4)
        if config.config["log"]["options"]["log_saves"]:
            logging.info("ARP table saved.")
        stop_event.wait(interval)

thread = threading.Thread(target=save_arp_table, args=(30,), daemon=True)
thread.start()

def arp_display(pkt : Packet):
    if ARP in pkt and pkt[ARP].op == 2: #ARP response
        if arptable.get(pkt[ARP].hwsrc) is None:
            arptable[pkt[ARP].hwsrc] = pkt[ARP].psrc
            logging.info("ARP table update" + json.dumps(obj=arptable)) #pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")
        
        elif arptable[pkt[ARP].hwsrc] == pkt[ARP].psrc:
            if config.config["log"]["options"]["log_repeated"]:
                logging.info("Repeated response. Ignoring")
        
        else:
            #Different IP for the same MAC
            logging.warning(f"Different IP for same MAC. New ip is {pkt[ARP].psrc}. Old entry was {pkt[ARP].hwsrc} : {arptable[pkt[ARP].hwsrc]}")
            mailer.set_subject("Arpspoof - potential threat")
            mailer.set_text_body(f"You are receiving this email because Arpspoof has detected a potential anomaly on your network at {get_time_string()}. Please check session logs for further information")
            mailer.send_mail()
        return




#Sniff ARP packets
logging.info("Listening for packets")
print("Program is running")
sniff(filter="arp", prn=arp_display, store=0, iface=INTERFACE)
