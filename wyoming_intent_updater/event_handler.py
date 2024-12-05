# custom_event_client/event_handler.py
import logging
import requests
import time
from wyoming.event import Event
from wyoming.asr import Transcript, Transcribe
from wyoming.satellite import StreamingStarted, StreamingStopped
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize
from wyoming.vad import VoiceStarted, VoiceStopped
from wyoming.wake import Detection

_LOGGER = logging.getLogger()

class IntentEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(self, cli_args, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli_args = cli_args
        self.client_id = str(time.monotonic_ns())
        _LOGGER.debug("Client connected: %s", self.client_id)

    def get_state(self, sensor):
        headers = {
            'Authorization': f'Bearer {self.cli_args.token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.cli_args.home_assistant_url}/api/states/{sensor}', headers=headers)
        return response.json()

    def update_state(self, sensor, state, attributes=None):
        headers = {
            'Authorization': f'Bearer {self.cli_args.token}',
            'Content-Type': 'application/json'
        }
        data = self.get_state(sensor)
        data['state'] = state
        if attributes:
            data['attributes'].update(attributes)
        response = requests.post(f'{self.cli_args.home_assistant_url}/api/states/{sensor}', headers=headers, json=data)
        _LOGGER.info(f'code: {response.status_code} response: {response.text}')

    async def handle_event(self, event: Event) -> bool:
        intent_sensor = self.cli_args.intent_sensor
        stt_sensor = self.cli_args.stt_sensor

        if Transcribe.is_type(event.type):
            self.update_state(intent_sensor, 'start')

        elif Detection.is_type(event.type):
            self.update_state(stt_sensor, 'start')

        elif VoiceStarted.is_type(event.type):
            self.update_state(stt_sensor, 'vad-start')

        elif VoiceStopped.is_type(event.type):
            self.update_state(stt_sensor, 'vad-end')

        elif Transcript.is_type(event.type) or StreamingStopped.is_type(event.type):
            self.update_state(stt_sensor, 'end')

        elif Synthesize.is_type(event.type):
            _LOGGER.info(f"Synthesizing {event.data['text']}")
            attributes = {
                'intent_output': {
                    'response': {
                        'speech': {
                            'plain': {
                                'speech': event.data['text'],
                                'extra_data': 'null'
                            }
                        },
                        'card': {},
                        'language': 'en',
                        'response_type': 'action_done',
                        'data': {
                            'targets': [],
                            'success': [],
                            'failed': []
                        }
                    },
                    'conversation_id': 'None',
                }
            }
            self.update_state(intent_sensor, 'end', attributes)

        return True
