from message import (MainCommandMessage, SubCommandMessage)
import asyncio
import json
import websockets
import requests

default_substring_url_to_reload = 'console.aws'

def main(message: MainCommandMessage):
    '''
Reload browser tabs where url contains the switch string
By default it reload aws pages if there is no switch string
'''
    env = message.env
    if message.switch_1:
        url_sub_string = message.switch_1
    else:
        url_sub_string = default_substring_url_to_reload
    asyncio.get_event_loop().run_until_complete(_reloading(env, url_sub_string))


async def _get_open_tabs(env):
    # Get the list of open tabs
    if env == 'dev':
        response = requests.get('http://localhost:9222/json')
    elif env == 'staging':
        response = requests.get('http://localhost:9223/json')
    elif env == 'prod':
        response = requests.get('http://localhost:9224/json')
    else:
        print('Invalid environment')
    return response.json()

async def _reload_tab(tab):
    async with websockets.connect(tab['webSocketDebuggerUrl']) as websocket:
        # Send reload command to the tab
        await websocket.send(json.dumps({
            "id": 1,
            "method": "Page.reload"
        }))
        print(f"Reloaded tab: {tab['url']}")


async def _reloading(env, url_sub_string):
    '''
Reload all aws browser tabs
This should be happening after updating the credentials
'''
    print(f'Reloading AWS browser tabs for {env}')
    tabs = await _get_open_tabs(env)

    for tab in tabs:
        if url_sub_string in tab['url']:
            await _reload_tab(tab)