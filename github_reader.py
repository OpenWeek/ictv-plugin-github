from pyquery import PyQuery
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
import urllib.request
from ictv.plugins.github_reader.githubApp import GitIctv

def parse_stat(stat):
    return None

def parse_issues(issues):
    return None

def pasre_commits(commits):
    return None

def parse_releases(releases):
    return None

def parse_contributors(contributors):
    return None

def get_content(channel_id):
    print("get_content")
    channel = PluginChannel.get(channel_id)
    print("after channel")
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('github_reader', channel)
    print("after get_logger")
    token = channel.get_config_param('token')
    print("before duration")
    duration = channel.get_config_param('duration')*1000
    repo_url = channel.get_config_param('repo_url')
    had_organisation = channel.get_config_param('had_organisation')
    orga_url = channel.get_config_param('orga_url')
    print("after orga_url")
    disp_commits = channel.get_config_param('disp_commits')
    number_commits = channel.get_config_param('number_commits')
    disp_contributors = channel.get_config_param('disp_contributors')
    number_contributors = channel.get_config_param('number_contributors')
    disp_issues = channel.get_config_param('disp_issues')
    number_issues = channel.get_config_param('number_issues')
    disp_stat = channel.get_config_param('disp_stat')
    print("After variable")
    if not token or not repo_url:
        logger.warning('Some of the required parameters are empty', extra=logger_extra)
        return []
    print("After token")

    git_obj = GitIctv(token,repo_url,orga_url)

    print("After init gitIctv")

    #Test
    stat = None
    issue_list = None
    commit_list = None
    release_list = None
    contributor_list = None
    organisation_list = None

    #if disp_stat:
    #    stat = git_obj.get_stat()
    if disp_issues:
        issue_list = git_obj.get_issue(number_issues)
    if disp_commits:
        commit_list = git_obj.get_commit(number_commits)
    if disp_releases:
        release_list = git_obj.get_realease()
    #if disp_contributors:
    #    contributor_list = git_obj.get_contributor()
    if had_organisation:
        organization_list = git_obj.get_organisation()

    print("BeforeReturn")

    return [GithubReaderCapsule(stat,issue_list,commit_list,release_list,contributor_list,organisation_list,duration)]

class GithubReaderCapsule(PluginCapsule):

    def __init__(self,stat,issue_list,commit_list,release_list,contributor_list,organisation_list,duration):
        print("GithubReaderCapsule")
        self._slides = []
        if stat :
            self._slides.append(GithubReaderSlide(stat,duration,'stat'))
        if issue_list:
            self._slides.append(GithubReaderSlide(issue_list,duration,'issue'))
        if commit_list:
            self._slides.append(GithubReaderSlide(commit_list,duration,'commit'))
        if release_list:
            self._slides.append(GithubReaderSlide(release_list,duration,'release'))
        if contributor_list:
            self._slides.append(GithubReaderSlide(contributor_list,duration,'contributor'))
        if organization_list:
            self._slides.append(GithubReaderSlide(organization_list,duration,'organization'))

    def get_slides(self):
        return self._slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)

class GithubReaderSlide(PluginSlide):
    def __init__(self, list, duration,mark = None):
        print("GithubReaderSlide")
        self._content = {}
        self._content['title'] = 'test'
        self._content['subtitle'] = 'Insert subtitle here'
        self._duration = duration
        i = 1
        for elem in list:
            #if mark == 'stat': #TODO
            #    self._content['text-'+str(i)] = elem[message]
            #    self._content['image-'+str(i)] = elem[text]
            if mark == 'issue':
                if elem['state'] == 'open':
                    self._content['text-'+str(i)] = elem['title']+"<br>state : "+elem['state']+"<br>"+elem['comments']
                elif elem['state'] == 'closed':
                    self._content['text-'+str(i)] = elem['title']+"<br>state : "+elem['state']+"closed at : "+elem['closed_at']+"<br>"+elem['comments']
                #else TODO, undefined ?
                self._content['image-'+str(i)] = elem['avatar']
            elif mark == 'commit':
                self._content['text-'+str(i)] = elem['author']+"<br>created at : "+elem['created_at']+"<br>"+elem['message']
                self._content['image-'+str(i)] = ""
            elif mark == 'release':
                self._content['text-'+str(i)] = elem['title']+"<br>author :"+elem['author']+ ", created at : "+elem['created_at']+", version :"+elem['version']+"<br>"+elem['body']
                self._content['image-'+str(i)] = ""
            #elif mark == 'contributor': #TODO
            #    self._content['text-'+str(i)] = elem[message]
            #    self._content['image-'+str(i)] = elem[text]
            elif mark == 'organization':
                self._content['text-'+str(i)] = elem['name']+"<br>"+elem['repos']
                self._content['image-'+str(i)] = elem['avatar-url']
            else:
                break #raise an error unknown mark (or None mark)
            i += 1
        self._content = {'background-1': {'src': 'https://bonsaieejit.files.wordpress.com/2011/12/background.jpg', 'size': 'contain'}, 'text-1': {'text': token}}


    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        return 'template-image-text-table.html'

    def __repr__(self):
        return str(self.__dict__)

if __name__ == "__main__":

    git = GitIctv("TOKEN", 'fdardenne/TestRepo', "scala")
    t = git.get_organization()
    print(t)
