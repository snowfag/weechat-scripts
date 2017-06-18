import weechat as wc

name = "mass_hl_ban.py"
wc.register(name, 'snowfag', '2.5', 'BSD-2c', 'Bans user if they highlight X number of users in channel in a single line', '', '')

def config(*args, **kwargs):
    global channels, whitelist, max_nick_count, mod_timer
    if not wc.config_is_set_plugin('channels'):
        wc.config_set_plugin('channels', '.*')
    if not wc.config_is_set_plugin('whitelist'):
        wc.config_set_plugin('whitelist', 'not_set')
    if not wc.config_is_set_plugin('max_nick_count'):
        wc.config_set_plugin('max_nick_count', '5')
    if not wc.config_is_set_plugin('mod_timer'):
        wc.config_set_plugin('mod_timer', '300')
    channels = wc.config_get_plugin('channels').lower().split(',')
    whitelist = wc.config_get_plugin('whitelist').lower().split(',')
    max_nick_count = wc.config_get_plugin('max_nick_count')
    mod_timer = wc.config_get_plugin('mod_timer')
    return wc.WEECHAT_RC_OK

def unmod(channel_name, remaining_calls):
    wc.command('', r'/mode {} -M'.format(channel_name))
    return wc.WEECHAT_RC_OK

def privmsg(data, signal, signal_data):
    (server, signal) = signal.split(',')
    details = wc.info_get_hashtable('irc_message_parse', {'message': signal_data, 'server': server})
    buffer_name = details['channel'].lower()
    if buffer_name in channels:
        if not details['nick'].lower() in whitelist:
            buffer_pointer = wc.info_get('irc_buffer', '{},{}'.format(server, buffer_name))
            msg_list = details['text'].split()
            nick_count = 0
            for msg_word in msg_list:
                test_word = wc.nicklist_search_nick(buffer_pointer, '', msg_word)
                if test_word:
                    nick_count = nick_count + 1
            if nick_count >= int(max_nick_count):
                wc.command('', r'/msg chanserv ban {0} {1} FUCK OFF.'.format(buffer_name, details['nick']))
                wc.command('', r'/mode {} +M'.format(buffer_name))
                wc.hook_timer(int(mod_timer) * 1000, 0, 1, 'unmod', buffer_name)
    return wc.WEECHAT_RC_OK

wc.hook_config('plugins.var.python.' + name + '.*', 'config', '')
wc.hook_signal('*,irc_in_privmsg', 'privmsg', '')
config()
