import weechat as wc
import re

name = 'guest.py'
wc.register(name, 'snowfag', '1.5', 'BSD-2c', 'guest remover', '', '')

def config(*args, **kwargs):
    global channels
    if not wc.config_is_set_plugin('channels'):
        wc.config_set_plugin('channels', '*')
    channels = wc.config_get_plugin('channels').lower().split(',')
    return wc.WEECHAT_RC_OK

def guestkicker(data, buffer, date, tags, displayed, is_hilight, prefix, msg):
    buffer_name = wc.buffer_get_string(buffer, "name").split('.')[-1].lower()
    cnick = re.compile(r'^irc_nick')
    if buffer_name in channels or '*' in channels:
        if cnick.match(tags):
            tagdata = tags.split(',')
            nickcheck = re.compile(r'^(irc_nick2_)(Guest[0-9]{2,8})$')
            if nickcheck.match(tagdata[3]):
                wc.command(buffer, r'/msg chanserv akick {} enforce'.format(buffer_name))
    return wc.WEECHAT_RC_OK

wc.hook_config('plugins.var.python.' + name + '.*', 'config', '')
wc.hook_print('', '', '', 1, 'guestkicker', '')
config()
