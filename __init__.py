# Copyright 2023 aofc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import paho.mqtt.client as mqtt

from neon_utils.skills.neon_skill import NeonSkill
from ovos_bus_client.message import Message

class MQTTBridgeSkill(NeonSkill):

    def __init__(self):
        super(MQTTBridgeSkill, self).__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_close = self.on_close
        self.client.on_message = self.on_mqtt_message
        self.client.username_pw_set(username=self.settings.get('username'),
                                    password=self.settings.get('passsword'))

    def on_connect(self, client, userdata, flags, rc):
        self.log.info("Connecté au broker MQTT avec le code de retour " + str(rc))

    def on_close(self):
        self.initialize()

    def initialize(self):
        self.client.connect(self.settings.get('ip'), self.settings.get('port'), 60)
        self.client.loop_start()
        self.client.subscribe(self.settings.get('topic')."/send")
        message_types = [
            'speak',
            'mycroft.internet.connected',
            'mycroft.ready',
            'mycroft.stop',
            'mycroft.not.paired',
            'mycroft.paired',
            'mycroft.awoken',
            'mycroft.debug.log',
            'complete_intent_failure',
            'configuration.updated',
            'recognizer_loop:wakeword',
            'recognizer_loop:record_begin',
            'recognizer_loop:record_end',
            'recognizer_loop:utterance',
            'recognizer_loop:audio_output_start',
            'recognizer_loop:audio_output_end',
            'recognizer_loop:sleep',
            'recognizer_loop:wake_up',
            'enclosure.notify.no_internet',
            'enclosure.mouth.viseme_list',
            'mycroft.mic.listen',
            'mycroft.mic.mute',
            'mycroft.mic.unmute',
            'mycroft.audio.service.play',
            'mycroft.audio.service.stop',
            'mycroft.audio.service.pause',
            'mycroft.audio.service.resume',
            'mycroft.audio.service.next',
            'mycroft.audio.service.prev',
            'mycroft.audio.service.track_info',
            'mycroft.audio.service.track_info_reply',
            'mycroft.audio.service.list_backends',
            'mycroft.volume.increase',
            'mycroft.volume.decrease',
            'mycroft.volume.mute',
            'mycroft.volume.unmute',
            'mycroft.volume.set',
            'mycroft.volume.get',
            'mycroft.volume.get.response',
            'mycroft.volume.duck',
            'mycroft.volume.unduck',
            'mycroft.skill.handler.start',
            'mycroft.skill.handler.complete',
            'mycroft.skill.enable_intent',
            'mycroft.skill.disable_intent',
            'mycroft.skills.loaded',
            'mycroft.skills.loading_failure',
            'mycroft.skills.shutdown',
            'mycroft.skills.initialized',
            'mycroft.skills.list',
            'mycroft.skills.settings.update',
            'mycroft.gui_service.is_alive.response',
            'mycroft.gui_service.is_alive',
            'mycroft.skills.is_alive.response',
            'mycroft.skills.is_alive',
            'msm.updating',
            'msm.installing',
            'msm.install.succeeded',
            'msm.install.failed',
            'msm.installed',
            'msm.updated',
            'msm.removing',
            'msm.remove.succeeded',
            'msm.remove.failed',
            'msm.removed',
            'skillmanager.deactivate',
            'skillmanager.list',
            'skillmanager.update',
            'open',
            'close',
            'reconnecting',
            'system.wifi.setup',
            'system.wifi.reset',
            'system.ntp.sync',
            'system.ssh.enable',
            'system.ssh.disable',
            'system.reboot',
            'system.shutdown',
            'system.update',
            'play:query',
            'play:query.response',
            'play:start',
            'question:query',
            'question:query.response',
            'question:action',
            'private.mycroftai.has_alarm',
            'phal.brightness.control.auto.dim.update',
            'ovos.PHAL.internet_check',
            'ovos.PHAL.internet_check.response'
        ]

        for message_type in message_types:
            self.add_event(message_type, self.on_message)

    def on_message(self, message):
        payload = {
            "type": message.msg_type,
            "data": message.data
        }
        self.send_to_mqtt(self.settings.get('topic'), payload)

    def on_mqtt_message(self, client, userdata, message):
        payload = json.loads(message.payload)
        self.log.info("Message MQTT reçu: " + str(payload))
        
        # Créez un objet Message à partir des données reçues
        msg = Message(payload["type"], payload["data"])

        # Envoyez le message au messagebus de Mycroft
        self.bus.emit(msg)

    def send_to_mqtt(self, topic, payload):
        self.client.publish(topic, json.dumps(payload))

    def shutdown(self):
        self.client.loop_stop()

def create_skill():
    return MQTTBridgeSkill()
