from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import glob
import pystray
from PIL import Image

from popup_manager import PopupManager

class Main():
    def __init__(self):
        self.popup_manager = PopupManager()
        self.menu_check = True

        path = "certificates/*.crt"
        certificatePath = glob.glob(path)[0]

        path = "certificates/*private.pem.key"
        privateKeyPath = glob.glob(path)[0]

        with open("config.json", "r", encoding="UTF8") as st_json:
            json_data = json.load(st_json)

        store_id = json_data['store_id']
        host = json_data['host']

        self.subscribe_topic = 'transaction_successful/' + store_id

        rootCAPath = "certificates/root.pem"

        port = 8883

        self.myAWSIoTMQTTClient = AWSIoTMQTTClient(store_id)
        self.myAWSIoTMQTTClient.configureEndpoint(host, port)
        self.myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

        # AWSIoTMQTTClient connection configuration
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(2)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        # Connect and subscribe to AWS IoT
        self.myAWSIoTMQTTClient.connect()
        self.myAWSIoTMQTTClient.subscribe(self.subscribe_topic, 0, self.customCallback)

        def on_quit(icon, item):
            self.popup_manager.stop_thread()
            icon.stop()
            self.myAWSIoTMQTTClient.disconnect()

        def tts_toggle(menu_item):
            self.menu_check = not self.menu_check
            menu_item.checked = self.menu_check
            self.popup_manager.tts_toggle()

        image = Image.open('tray_icon.png')
        menu = pystray.Menu(
            pystray.MenuItem('종료', on_quit),
            pystray.MenuItem('음성', tts_toggle, checked=lambda i: bool(self.menu_check))
        )

        tray = pystray.Icon('줍줍포인트 팝업관리자', image, '줍줍포인트 팝업관리자', menu)

        tray.run()



    def customCallback(self, client, userdata, message):
        try:
            message_string = message.payload

            if message_string[0] == 'b':

                message_string = message_string[1:]
            if message_string[0] == "'":
                message_string = message_string[1:len(message_string)-1]

            message_to_json = json.loads(message_string)

            self.popup_manager.put_data(message_to_json['price'], message_to_json['transaction_time'], message_to_json['duration'])

        except Exception as e:
            print(e)

    def publish_message(self, topic, message):
        try:
            messageJson = json.dumps(message)
            self.myAWSIoTMQTTClient.publish(topic, messageJson, 0)
        except Exception as e:
            print(e)

    def disconnect(self):
        try:
            self.myAWSIoTMQTTClient.disconnect()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main = Main()

