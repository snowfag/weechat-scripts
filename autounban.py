import weechat as wc
from time import sleep

wc.register('autounban.py', 'snowfag', '1.0', 'BSD-2c', 'auto unban and rejoin channel', '', '')

def config(*args, **kwargs):
    global delay
    if not wc.config_is_set_plugin('delay'):
        wc.config_set_plugin('delay', '4')
    else:
        delay = wc.config_get_plugin('delay')
        try:
            int(delay)
        except:
            wc.prnt("", "%s is not a valid delay." % (delay))
            wc.config_set_plugin('delay', '4')
    delay = wc.config_get_plugin('delay')
    return wc.WEECHAT_RC_OK

def unban_timer(data, signal, signal_data):
    details = wc.info_get_hashtable("irc_message_parse", {"message": signal_data})
    global channel
    channel = details['channel']
    wc.hook_timer(int(delay) * 1000, 0, 1, "unban", "")
    return wc.WEECHAT_RC_OK

def kick_timer(data, signal, signal_data):
    (server, signal) = signal.split(",")
    details = wc.info_get_hashtable("irc_message_parse", {"message": signal_data, "server": server})
    global channel
    channel = details['channel']
    knick = details['text'].split()[0]
    cnick = wc.info_get("irc_nick", server)
    if knick == cnick:
        wc.hook_timer(int(delay) * 1000, 0, 1, "kick", "signal, signal_data")
    return wc.WEECHAT_RC_OK

def unban(*args, **kwargs):
    wc.command("", r"/msg chanserv unban %s" % (channel))
    sleep(0.1)
    wc.command("", r"/join %s" % (channel))
    return wc.WEECHAT_RC_OK

def kick(*args, **kwargs):
    wc.command("", r"/join %s" % (channel))
    return wc.WEECHAT_RC_OK

wc.hook_signal("*,irc_raw_in_474", "unban_timer", "")
wc.hook_signal("*,irc_raw_in_kick", "kick_timer", "")
wc.hook_config("plugins.var.python." + "autounban.py" + ".delay", "config", "")
config()
