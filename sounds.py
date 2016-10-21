#!/usr/bin/env python
import time
from slackclient import SlackClient
import os, re

base_dir = os.path.dirname(os.path.realpath(__file__))

player = 'afplay'
text2voice = 'espeak'
sounds_dir = 'sounds'
filetype = 'mp3'
debug = True
bots_channel = 'build'

play_fixed = re.compile("FIXED")
play_cancelled = re.compile("CANCELLED")
play_failed = re.compile("FAILED")
play_broken = re.compile("BROKEN")
play_building = re.compile("BUILDING")

add_sound_regex = re.compile("^add-sound\s([a-z0-9]+)\s<?(https?:\/\/[a-z./]*\?v=[a-zA-Z0-9_-]*)>?(\s([0-9.]*)\s([0-9.]*)$)?")

def action(command, message):
    global debug
    global sc
    global bots_channel

    sc.rtm_send_message(bots_channel, message)
    if debug: print ('Running command: ' + command)
    os.system(command)

whitelist = {}
with open(os.path.join(base_dir, 'whitelist.txt')) as f:
    for line in f:
        (name, identifier) = line.split()
        whitelist[identifier] = name

f = open(os.path.join(base_dir, 'token.txt'))
token = f.readline().rstrip()
f.close()

print ("Connecting using token " + token)
sc = SlackClient(token)

if sc.rtm_connect():
    while True:
        for event in sc .rtm_read():
            if 'type' in event and event['type'] == 'message' and 'text' in event:
                if ('user' in event and event['user'] in whitelist.keys()):
                    user = whitelist[event['user']]
                elif ('subtype' in event and event['subtype'] == 'bot_message' and 'bot_id' in event and event['bot_id'] in whitelist.keys()):
                    user = whitelist[event['bot_id']]
                else:
                    user = False
                if user:
                    if debug: print ("Parsing message from " + user + ": '" + event['attachments'][0]['fallback'] + "'")
                    add_sound_match = add_sound_regex.match(event['attachments'][0]['fallback'])
                    fixed = play_fixed.search(event['attachments'][0]['fallback'])
                    cancelled = play_cancelled.search(event['attachments'][0]['fallback'])
                    failed = play_failed.search(event['attachments'][0]['fallback'])
                    broken = play_broken.search(event['attachments'][0]['fallback'])
                    building = play_building.search(event['attachments'][0]['fallback'])

                    if fixed:
                        message = user + ' FIXED '
                        sound_file = os.path.join(base_dir, sounds_dir, 'dai' + '.' + filetype)
                        command = player + ' ' + sound_file
                        action(command, message)
                    elif cancelled:
                        message = user + ' CANCELLED '
                        sound_file = os.path.join(base_dir, sounds_dir, 'noooo' + '.' + filetype)
                        command = player + ' ' + sound_file
                        action(command, message)
                    elif failed:
                        message = user + ' FAILED '
                        sound_file = os.path.join(base_dir, sounds_dir, 'heygirl' + '.' + filetype)
                        command = player + ' ' + sound_file
                        action(command, message)
                    elif broken:
                        message = user + ' BROKEN '
                        sound_file = os.path.join(base_dir, sounds_dir, 'horror' + '.' + filetype)
                        command = player + ' ' + sound_file
                        action(command, message)
                    elif building:
                        message = user + ' BUILDING '
                        sound_file = os.path.join(base_dir, sounds_dir, 'dangerzone' + '.' + filetype)
                        command = player + ' ' + sound_file
                        action(command, message)
                    elif add_sound_match:
                        message = user + ' adds sound ' + add_sound_match.group(1) + ' from youtube video ' + add_sound_match.group(2)
                        command = os.path.join(base_dir, 'yt-add-sound.sh') + ' ' + add_sound_match.group(1) + ' ' + add_sound_match.group(2)
                        if add_sound_match.group(3): command += add_sound_match.group(3)
                        action(command, message)
        time.sleep(1);
else:
    print ('Connection failed, invalid token?')