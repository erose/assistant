from typing import *
import requests
import urllib
import wrapped_redis
import os

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

SERP_API_KEY = os.environ.get('SERP_API_KEY')
app = Flask(__name__)

YOUTUBE_COMMAND_PREFIX = "youtube:"
COMMAND_PREFIXES = [YOUTUBE_COMMAND_PREFIX]

INITIAL_STATE = 'initial'
WAITING_ON_YOUTUBE_CONFIRMATION_STATE = 'waiting_on_youtube_confirmation_state'
STATES = [
    INITIAL_STATE,
    WAITING_ON_YOUTUBE_CONFIRMATION_STATE,
]

@app.route("/sms_reply", methods=["POST"])
def sms_reply():
    body = request.values.get('Body', None)
    normalized_body = body.lower()

    # Initialize the response content to an error message.
    response_content = f"No command recognized. Commands start with any string in this list [{prefixes_formatted()}]"

    current_state = get_state()
    if normalized_body.startswith(YOUTUBE_COMMAND_PREFIX):
        if current_state == INITIAL_STATE:
            search_string = normalized_body.removeprefix(YOUTUBE_COMMAND_PREFIX)
            url = get_first_video_url(search_string)
            if url is None:
                response_content = "No results found."
            else:
                response_content = f"{url} ?"
                set_youtube_video_url(url)
        else:
            # TODO
            raise ValueError

    elif current_state == WAITING_ON_YOUTUBE_CONFIRMATION_STATE:
        video_url = get_youtube_video_url()
        os.system(f"./download_single_or_multiple_videos.sh {video_url}")
    else:
        raise ValueError
   
    response = MessagingResponse()
    response.message(response_content)
    return str(response)

def get_state() -> str:
	return wrapped_redis.get('current_state') or INITIAL_STATE # So it works the first time.

def get_youtube_video_url() -> str:
    return wrapped_redis.get('youtube_video_url')

def set_state(string) -> None:
    wrapped_redis.set('current_state', string)

def set_youtube_video_url(string) -> None:
    wrapped_redis.set('youtube_video_url', string)

def prefixes_formatted() -> str:
    return ', '.join(f'"{prefix}"' for prefix in COMMAND_PREFIXES)

def get_first_video_url(search_string) -> Optional[str]:
    response = requests.get(f"https://serpapi.com/search.json?engine=youtube&search_query={urllib.parse.quote_plus(search_string)}&api_key={SERP_API_KEY}")
    results = response.json()
    try:
        video_results = results["video_results"]
        if not video_results:
            return None

        first_movie_result = video_results[0]
        return first_movie_result["link"]
    except KeyError:
        return None

if __name__ == "__main__":
    app.run(debug=True)