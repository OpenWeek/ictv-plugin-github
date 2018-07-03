from pyquery import PyQuery
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
import urllib.request
from github import Github




def get_content(channel_id):

    channel = PluginChannel.get(channel_id)
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('github-reader', channel)
    token = channel.get_config_param('token')
    duration = channel.get_config_param('duration')
    repo_url = channel.get_config_param('repo_url')
    had_organisation = channel.get_config_param('had_organisation')
    orga_url = channel.get_config_param('orga_url')
    disp_commits = channel.get_config_param('disp_commits')
    number_commits = channel.get_config_param('number_commits')
    disp_contributors = channel.get_config_param('disp_contributors')
    number_contributors = channel.get_config_param('number_contributors')
    disp_issues = channel.get_config_param('disp_issues')
    number_issues = channel.get_config_param('number_issues')
    disp_stat = channel.get_config_param('disp_stat')

    if not token or not page_url:
        logger.warning('Some of the required parameters are empty', extra=logger_extra)
        return []

    git_obj = GitIctv(token,page_url)

    if disp_stat:
        stat = git_obj.get_stat()
    if disp_issues:
        issue_list = git_obj.get_issue()
    if disp_commits:
        commit_list = git_obj.get_commit()
    if disp_releases:
        release_list = git_obj.get_realease()
    if disp_contributors:
        contributo_list = git_obj.get_contributor()
    if had_organisation:
        repo_list = git_obj.get_repo()

    return [GithubReaderCapsule(duration)]

class GithubReaderCapsule(PluginCapsule):

    def __init__(self,duration):
        self._slides = [GithubReaderSlide(duration)]

    def get_slides(self):
        return self._slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)

class GithubReaderSlide(PluginSlide):
    def __init__(self,duration):
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
