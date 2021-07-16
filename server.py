from typing import *
import requests
import urllib
import wrapped_redis

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

    response_content = f"No command recognized. Commands start with any of {','.join(COMMAND_PREFIXES)}"
    if normalized_body.startswith(YOUTUBE_COMMAND_PREFIX):
        search_string = normalized_body.removeprefix(YOUTUBE_COMMAND_PREFIX)
        url = get_first_video_url(search_string)
        if url is None:
            response_content = ""
        else:
            response_content = f"{url} ?"
       
    response = MessagingResponse()
    response.message(response_content)
    return str(response)

def get_state() -> str:
	return wrapped_redis.get('current_state') or INITIAL_STATE # So it works the first time.

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