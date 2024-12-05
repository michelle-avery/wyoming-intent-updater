# custom_event_client/main.py
import argparse
import asyncio
import logging
from functools import partial
from wyoming_intent_updater.event_handler import IntentEventHandler
from wyoming.server import AsyncServer

_LOGGER = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="stdio://", help="unix:// or tcp://")
    parser.add_argument("--token", help="Access token for Home Assistant")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument("--log-format", default=logging.BASIC_FORMAT, help="Format for log messages")
    parser.add_argument("--intent-sensor", help="The sensor to update with the result of intent handling")
    parser.add_argument("--stt-sensor", help="The sensor to update with the result of speech-to-text")
    parser.add_argument("--home-assistant-url", help="The URL of the Home Assistant instance")
    return parser.parse_args()

def sanitize_args(args):
    sanitized_args = vars(args).copy()
    if 'token' in sanitized_args:
        sanitized_args['token'] = '***'
    return sanitized_args


async def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format)
    _LOGGER.debug(sanitize_args(args))
    _LOGGER.info("Ready")

    server = AsyncServer.from_uri(args.uri)
    try:
        await server.run(partial(IntentEventHandler, args))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
