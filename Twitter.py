from TwitterAPI import TwitterAPI
from HTMLParser import HTMLParser
import weechat as wc
import re

name = 'Twitter.py'
wc.register(name, 'snowfag', '2.2', 'BSD-2c', 'Twitter status announcer', '', '')

def config(*args, **kwargs):
    global channels, consumer_key, consumer_secret, access_token_key, access_token_secret, bots_list
    if not wc.config_is_set_plugin('channels'):
        wc.config_set_plugin('channels', '*')
    if not wc.config_is_set_plugin('consumer_key'):
        wc.config_set_plugin('consumer_key', 'not_set')
    if not wc.config_is_set_plugin('consumer_secret'):
        wc.config_set_plugin('consumer_secret', 'not_set')
    if not wc.config_is_set_plugin('access_token_key'):
        wc.config_set_plugin('access_token_key', 'not_set')
    if not wc.config_is_set_plugin('access_token_secret'):
        wc.config_set_plugin('access_token_secret', 'not_set')
    if not wc.config_is_set_plugin('other_bots'):
        wc.config_set_plugin('other_bots', 'not_set')
    channels = wc.config_get_plugin('channels').lower().split(',')
    consumer_key = wc.config_get_plugin('consumer_key')
    consumer_secret = wc.config_get_plugin('consumer_secret')
    access_token_key = wc.config_get_plugin('access_token_key')
    access_token_secret = wc.config_get_plugin('access_token_secret')
    sec = re.compile('^\${sec\.data\.(.*)}$')
    if sec.match(consumer_key):
        consumer_key = wc.string_eval_expression(consumer_key, {}, {}, {})
    if sec.match(consumer_secret):
        consumer_secret = wc.string_eval_expression(consumer_secret, {}, {}, {})
    if sec.match(access_token_key):
        access_token_key = wc.string_eval_expression(access_token_key, {}, {}, {})
    if sec.match(access_token_secret):
        access_token_secret = wc.string_eval_expression(access_token_secret, {}, {}, {})
    bots_list = wc.config_get_plugin('other_bots').split(',')
    return wc.WEECHAT_RC_OK

def privmsg(data, signal, signal_data):
    (server, signal) = signal.split(',')
    details = wc.info_get_hashtable('irc_message_parse', {'message': signal_data, 'server': server})
    buffer_name = details['channel'].lower()
    bots_exist = False
    if buffer_name in channels or '*' in channels:
        if not bots_list == 'not_set':
            buffer_pointer = wc.info_get('irc_buffer', '{},{}'.format(server, buffer_name))
            for other_bots in bots_list:
                bots_test = wc.nicklist_search_nick(buffer_pointer, '', other_bots)
                if bots_test:
                    bots_exist = True
        if not bots_exist:
            twitter_regex_match = re.compile(r'(.*https?://)?twitter\.com/.*/status/([0-9]{18})(.*)').match(details['text'])
            if twitter_regex_match:
                if consumer_key == 'not_set':
                    wc.command(buffer_pointer, r'/msg {} Twitter consumer_key not set.'.format(buffer_name))
                elif consumer_secret == 'not_set':
                    wc.command(buffer_pointer, r'/msg {} Twitter consumer_secret not set.'.format(buffer_name))
                elif access_token_key == 'not_set':
                    wc.command(buffer_pointer, r'/msg {} Twitter access_token_key not set.'.format(buffer_name))
                elif access_token_secret == 'not_set':
                    wc.command(buffer_pointer, r'/msg {} Twitter access_token_secret not set.'.format(buffer_name))
                else:
                    tweet_id = twitter_regex_match.group(2)
                    tweet = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret).request('statuses/show/:{}'.format(tweet_id))
                    try:
                        tweet_message = tweet.json()['text'].replace('\n', ' ').encode('utf-8')
                        tweet_message = HTMLParser().unescape(tweet_message)
                        tweet_user = tweet.json()['user']['screen_name'].encode('utf-8')
                        wc.command(buffer_pointer, r'/msg {} [Twitter] "{}" by @{}'.format(buffer_name, tweet_message, tweet_user))
                    except:
                        wc.command(buffer_pointer, r'/msg {} [Twitter] Error getting tweet info.'.format(buffer_name))
    return wc.WEECHAT_RC_OK

wc.hook_config('plugins.var.python.' + name + '.*', 'config', '')
wc.hook_signal('*,irc_in_privmsg', 'privmsg', '')
config()
