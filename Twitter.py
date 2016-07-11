from TwitterAPI import TwitterAPI
from HTMLParser import HTMLParser
import weechat as wc
import re

wc.register('Twitter.py', 'snowfag', '1.0', 'BSD-2c', 'Twitter status announcer', '', '')

def config(*args, **kwargs):
    if not wc.config_is_set_plugin('channels'):
        wc.config_set_plugin('channels', '.*')
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
    return wc.WEECHAT_RC_OK

def privmsg(data, signal, signal_data):
    (server, signal) = signal.split(',')
    channels = wc.config_get_plugin('channels').replace(',', '|')
    consumer_key = wc.config_get_plugin('consumer_key')
    consumer_secret = wc.config_get_plugin('consumer_secret')
    access_token_key = wc.config_get_plugin('access_token_key')
    access_token_secret = wc.config_get_plugin('access_token_secret')
    bots_list = wc.config_get_plugin('other_bots').split(',')
    details = wc.info_get_hashtable('irc_message_parse', {'message': signal_data, 'server': server})
    twitter_regex_match = re.compile(r'(.*https?://)?twitter\.com/.*/status/([0-9]{18})(.*)').match(details['text'])
    buffer_name = details['channel']
    buffer_pointer = wc.info_get('irc_buffer', '%s,%s' % (server, buffer_name))
    channels_regex = re.compile(r'(%s)' % (channels), re.I)
    bots_exist = False
    if channels_regex.match(buffer_name) and twitter_regex_match:
        if not bots_list == 'not_set':
            for other_bots in bots_list:
                bots_test = wc.nicklist_search_nick(buffer_pointer, '', other_bots)
                if bots_test:
                    bots_exist = True
        if not bots_exist:
            if consumer_key == 'not_set':
                wc.command('', r'/msg {0} Twitter consumer_key not set.'.format(buffer_name))
            elif consumer_secret == 'not_set':
                wc.command('', r'/msg {0} Twitter consumer_secret not set.'.format(buffer_name))
            elif access_token_key == 'not_set':
                wc.command('', r'/msg {0} Twitter access_token_key not set.'.format(buffer_name))
            elif access_token_secret == 'not_set':
                wc.command('', r'/msg {0} Twitter access_token_secret not set.'.format(buffer_name))
            else:
                tweet_id = twitter_regex_match.group(2)
                tweet = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret).request('statuses/show/:{0}'.format(tweet_id))
                try:
                    tweet_message = tweet.json()['text'].replace('\n', ' ').encode('utf-8')
                    tweet_message = HTMLParser().unescape(tweet_message)
                    tweet_user = tweet.json()['user']['screen_name'].encode('utf-8')
                    wc.command('', r'/msg {0} [Twitter] "{1}" by @{2}'.format(buffer_name, tweet_message, tweet_user))
                except:
                    wc.command('', r'/msg {0} [Twitter] Error getting tweet info.'.format(buffer_name))
    return wc.WEECHAT_RC_OK
wc.hook_signal('*,irc_in_privmsg', 'privmsg', '')
config()
