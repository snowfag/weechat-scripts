# -*- coding: utf-8 -*-
import weechat as wc
import requests
import re
from BeautifulSoup import BeautifulSoup

name = "mpc-hc_np"

wc.register(name, 'snowfag', '1.1', 'BSD-2c', 'mpc-hc now playing', '', '')

def config(*args, **kwargs):
    if not wc.config_is_set_plugin('mpc_host'):
        wc.config_set_plugin('mpc_host', 'localhost')
    if not wc.config_is_set_plugin('mpc_port'):
	wc.config_set_plugin('mpc_port', '13579')
    if not wc.config_is_set_plugin('color1'):
        wc.config_set_plugin('color1', '06')
    if not wc.config_is_set_plugin('color2'):
        wc.config_set_plugin('color2', '13')
    c1 = wc.config_get_plugin('color1')
    c2 = wc.config_get_plugin('color2')
    colorre = re.compile(r'^[0][1-9]|[1][0-5]$')
    if not colorre.match(c1):
        wc.prnt("", "invalid color (valid colors are 01-15)")
        wc.config_set_plugin('color1', '06')
    if not colorre.match(c2):
        wc.prnt("", "invalid color (valid colors are 01-15)")
        wc.config_set_plugin('color2', '13')
    return wc.WEECHAT_RC_OK

def mpc_np(*args, **kwargs):
    mpc_host = wc.config_get_plugin('mpc_host')
    mpc_port = wc.config_get_plugin('mpc_port')
    c1 = wc.config_get_plugin('color1')
    c2 = wc.config_get_plugin('color2')
    try:
        r = requests.get('http://%s:%s/variables.html' % (mpc_host, mpc_port), timeout=0.5)
        output = r.content
    except:
        wc.prnt(wc.current_buffer(), 'Server did not respond, maybe mpc-hc isn\'t running')
        return wc.WEECHAT_RC_ERROR

    def args(output, attr):
        return BeautifulSoup(output).body.find('p', attrs={'id':'%s' % (attr)}).text.encode('utf-8')

    size = args(output, "size")
    title = args(output, "file")
    rawposition = int(args(output, "position"))/1000
    rawlength = int(args(output, "duration"))/1000
    if rawposition < 3600:
        m, s = divmod(rawposition, 60)
        position = "%s:%02d" % (m, s)
    else:
        m, s = divmod(rawposition, 60)
        h, m = divmod(m, 60)
        position = "%s:%02d:%02d" % (h, m, s)
    if rawlength < 3600:
        m, s = divmod(rawlength, 60)
        length = "%s:%02d" % (m, s)
    else:
        m, s = divmod(rawlength, 60)
        h, m = divmod(m, 60)
        length = "%s:%02d:%02d" % (h, m, s)

    wc.command(wc.current_buffer(), r"/me {5}»» {4}MPC-HC {5}«»{4} {0} {5}«»{4} {1}{5}/{4}{2} {5}«»{4} {3}".format(title, position, length, size, c1, c2))
    return wc.WEECHAT_RC_OK
wc.hook_command('vid', 'mpc-hc now playing', '', '', '', 'mpc_np', '')
wc.hook_config("plugins.var.python." + name + ".color1", "config", "")
wc.hook_config("plugins.var.python." + name + ".color2", "config", "")
config()
