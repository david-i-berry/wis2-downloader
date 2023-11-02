from flask import Flask, request
import json
import logging
import os
import paho.mqtt.client as mqtt
from pathlib import Path
import queue
import ssl
import threading
import urllib3
from urllib.parse import urlsplit

# Load subs
with open("subscriptions.json") as fh:
    subs = json.load(fh)

# LOGGER
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


# Downloader
urlQ = queue.Queue()
http = urllib3.PoolManager()
def downloadWorker():
    while True:
        LOGGER.debug(f"Messages in queue: {urlQ.qsize()}")
        job = urlQ.get()
        output_dir = subs.get(job['topic'])
        if output_dir == None:
            output_dir = "downloads"
        output_dir = Path(output_dir)
        # get data ID, used to set directory to write to
        dataid = Path(job['payload']['properties']['data_id'])
        # we need to replace colons in output path
        dataid = Path(str(dataid).replace(":",""))
        output_path = Path(output_dir, dataid)
        # create directory
        output_path.parent.mkdir(exist_ok=True, parents=True)
        print(output_path.parent)
        # find canonical in links
        for link in job['payload']['links']:
            if link['rel'] == "canonical":
                path = urlsplit(link['href']).path
                filename = os.path.basename(path)
                LOGGER.debug(f"{filename}")
                # check if already in output directory, if not download
                if not output_path.is_file():
                    LOGGER.debug(f"Downloading {filename}")
                    try:
                        response = http.request("GET", link['href'])
                    except Exception as e:
                        LOGGER.error(f"Error downloading {link['href']}")
                        LOGGER.error(e)
                    try:
                        output_path.write_bytes(response.data)
                    except Exception as e:
                        LOGGER.error(f"Error saving to disk: ./downloads/{filename}")
                        LOGGER.error(e)

        urlQ.task_done()

downloadThread = threading.Thread(target=downloadWorker, daemon=True).start()


# MQTT stuff
def on_connect(client, userdata, flags, rc):  # subs managed by sub-manager
    LOGGER.debug("connected")

def on_message(client, userdata, msg):
    LOGGER.debug("message received")
    # create new job and add to queue
    job = {
        'topic': msg.topic,
        'payload': json.loads(msg.payload)
    }
    urlQ.put(job)


def on_subscribe(client, userdata, mid, granted_qos):
    LOGGER.debug(("on subscribe"))

broker = "globalbroker.meteo.fr"
port = 443
pwd = "everyone"
uid = "everyone"
protocol = "websockets"

LOGGER.debug("Initialising client")
client = mqtt.Client(transport=protocol)
client.tls_set(ca_certs=None, certfile=None, keyfile=None,
               cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS,
               ciphers=None)
client.username_pw_set(uid, pwd)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
LOGGER.debug("Connecting")
result = client.connect(host=broker, port=port)
LOGGER.debug(result)
mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True).start()

for sub in subs:
    client.subscribe(sub)


def create_app(test_config=None):
    LOGGER.debug("Creating app")
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/wis2/subscriptions/list')
    def list_subscriptions():
        return subs

    @app.route('/wis2/subscriptions/add')
    def add_subscription():
        topic = request.args.get('topic', None)
        if topic==None:
            return "No topic passed"
        else:
            if topic in subs:
                LOGGER.debug(f"Topic {topic} already subscribed")
            else:
                client.subscribe(f"{topic}")
                subs[topic] = './downloads'
        return subs

    @app.route('/wis2/subscriptions/delete')
    def delete_subscription():
        topic = request.args.get('topic', None)
        if topic==None:
            return "No topic passed"
        else:
            client.unsubscribe(f"{topic}")
            print(f"{topic}/#")
            if topic in subs:
                del subs[topic]
            else:
                print(f"Topic {topic} not found")
                for sub in subs:
                    print(sub, topic)
        return subs

    return app