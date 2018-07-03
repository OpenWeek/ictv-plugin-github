from pyquery import PyQuery
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
import urllib.request




def get_content(channel_id):
    channel = PluginChannel.get(channel_id)
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('fb-reader', channel)
    token = channel.get_config_param('token')
    page_id = channel.get_config_param('page_id')
    number_post = channel.get_config_param('number_post')
    duration = channel.get_config_param('duration')

    if not token or not page_id:
        logger.warning('Some of the required parameters are empty', extra=logger_extra)
        return []

    return [FbReaderCapsule(token, page_id, number_post, duration)]

def get_page_feed(token, page_id):
    with urllib.request.urlopen("https://graph.facebook.com/v3.0/"+page_id+"?fields=feed&access_token="+token) as url:
        raw = url.read()
        json_feed = json.loads(raw)
        feed = json_obj['feed']["data"]

        return dict
    return {}

class FbReaderCapsule(PluginCapsule):

    def __init__(self, token, page_id, number_post, duration):
        self._slides = [FbReaderSlide(token, page_id, number_post, duration)]

    def get_slides(self):
        return self._slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)

class FbReaderSlide(PluginSlide):
    def __init__(self, token, page_id, number_post, duration):
        self._duration = duration
        self._content = {'background-1': {'src': 'https://bonsaieejit.files.wordpress.com/2011/12/background.jpg', 'size': 'contain'}, 'text-1': {'text': token}}


    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        return 'template-background-text-qr'

    def __repr__(self):
        return str(self.__dict__)
