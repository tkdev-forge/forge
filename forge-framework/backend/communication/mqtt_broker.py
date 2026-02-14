import json
import os
from collections.abc import Callable

import paho.mqtt.client as mqtt


class MQTTBrokerClient:
    def __init__(self):
        self.host = os.getenv("MQTT_HOST", "mosquitto")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(self.host, self.port, 60)

    @staticmethod
    def topic(project_id: str, tier: int, agent_id: str, action: str) -> str:
        return f"forge/{project_id}/tier{tier}/{agent_id}/{action}"

    def publish(
        self,
        project_id: str,
        agent_id: str,
        tier: int,
        topic_suffix: str,
        payload: dict,
    ):
        topic = self.topic(project_id, tier, agent_id, topic_suffix)
        self.client.publish(topic, json.dumps(payload), qos=1)

    def subscribe(
        self,
        project_id: str,
        agent_id: str,
        tier: int,
        topic_suffix: str,
        callback: Callable,
    ):
        topic = self.topic(project_id, tier, agent_id, topic_suffix)

        def _on_message(client, userdata, msg):
            callback(msg.topic, msg.payload.decode("utf-8"))

        self.client.on_message = _on_message
        self.client.subscribe(topic)
        self.client.loop_start()
