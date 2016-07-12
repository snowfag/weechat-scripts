import requests
import weechat as wc
import re

wc.register('youtube.py', 'snowfag', '1.1', 'BSD-2c', 'Youtube video title announcer', '', '')

def config(*args, **kwargs):
    if not wc.config_is_set_plugin('channels'):
        wc.config_set_plugin('channels', '.*')
    if not wc.config_is_set_plugin('api_key'):
        wc.config_set_plugin('api_key', 'not_set')
    if not wc.config_is_set_plugin('other_bots'):
        wc.config_set_plugin('other_bots', 'not_set')
    return wc.WEECHAT_RC_OK

def privmsg(data, signal, signal_data):
    (server, signal) = signal.split(",")
    channels = wc.config_get_plugin('channels').replace(',', '|')
    api_key = wc.config_get_plugin('api_key')
    if re.match('^\${sec\.data\.(.*)}$', api_key):
        api_key = wc.string_eval_expression(api_key, {}, {}, {})
    bots_list = wc.config_get_plugin('other_bots').split(",")
    details = wc.info_get_hashtable("irc_message_parse", {"message": signal_data, "server": server})
    youtube_regex_match = re.compile(r'(.*https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})(.*)').match(details['text'])
    buffer_name = details['channel']
    buffer_pointer = wc.info_get("irc_buffer", "%s,%s" % (server, buffer_name))
    channels_regex = re.compile(r'(%s)' % (channels), re.I)
    bots_exist = False
    if channels_regex.match(buffer_name) and youtube_regex_match:
        if not bots_list == "not_set":
            for other_bots in bots_list:
                bots_test = wc.nicklist_search_nick(buffer_pointer, "", other_bots)
                if bots_test:
                    bots_exist = True
        if not bots_exist:
            if not api_key == "not_set":
                vid_id = youtube_regex_match.group(6)
                rvt = requests.get('https://www.googleapis.com/youtube/v3/videos/?id={0}&part=snippet&key={1}'.format(vid_id, api_key))
                rvc = requests.get('https://www.googleapis.com/youtube/v3/videos/?id={0}&part=statistics&key={1}'.format(vid_id, api_key))
                try:
                    vid_title = rvt.json()['items'][0]['snippet']['title'].encode('utf-8')
                    vid_channel = rvt.json()['items'][0]['snippet']['channelTitle'].encode('utf-8')
                    vid_views = rvc.json()['items'][0]['statistics']['viewCount']
                    wc.command("", r"/msg {0} [Youtube] {1} | Channel: {2} | Views: {3}".format(buffer_name, vid_title, vid_channel, vid_views))
                except:
                    wc.command("", r"/msg {0} [Youtube] Error getting video info.".format(buffer_name))
            else:
                wc.command("", r"/msg {0} Youtube api key not set.".format(buffer_name))
    return wc.WEECHAT_RC_OK
wc.hook_signal("*,irc_in_privmsg", "privmsg", "")
config()
