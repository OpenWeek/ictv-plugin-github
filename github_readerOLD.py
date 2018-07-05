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
    had_organization = channel.get_config_param('had_organization')
    number_organizations = channel.get_config_param('number_organizations')
    orga_url = channel.get_config_param('orga_url')
    print("after orga_url")
    disp_commits = channel.get_config_param('disp_commits')
    number_commits = channel.get_config_param('number_commits')
    disp_contributors = channel.get_config_param('disp_contributors')
    number_contributors = channel.get_config_param('number_contributors')
    disp_issues = channel.get_config_param('disp_issues')
    number_issues = channel.get_config_param('number_issues')
    disp_stat = channel.get_config_param('disp_stat')
    disp_releases = channel.get_config_param('disp_releases')
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
    organization_list = None

    #if disp_stat:
    #    stat = git_obj.get_stat()
    if disp_issues:
        issue_list = git_obj.get_issue(number_issues)
    if disp_commits:
        commit_list = git_obj.get_commit(number_commits)
    if disp_releases:
        release_list = git_obj.get_release()
    #if disp_contributors:
    #    contributor_list = git_obj.get_contributor()
    if had_organization:
        organization_list = git_obj.get_organization(number_organizations)

    print("BeforeReturn")

    return [GithubReaderCapsule(repo_url,stat,issue_list,commit_list,release_list,contributor_list,organization_list,duration)]

class GithubReaderCapsule(PluginCapsule):

    def __init__(self,repo_url,stat,issue_list,commit_list,release_list,contributor_list,organization_list,duration):
        print("GithubReaderCapsule")
        self._slides = []
        print(type(issue_list))
        if stat:
            self._slides.append(GithubReaderSlide(stat,duration,'stat'))
        if issue_list:
            print("GithubReaderCapsule : issue_list")
            self._slides.append(GithubReaderSlide(repo_url,issue_list,duration,'issue'))
        if commit_list:
            self._slides.append(GithubReaderSlide(repo_url,commit_list,duration,'commit'))
        if release_list:
            self._slides.append(GithubReaderSlide(repo_url,release_list,duration,'release'))
        if contributor_list:
            self._slides.append(GithubReaderSlide(repo_url,contributor_list,duration,'contributor'))
        if organization_list:
            self._slides.append(GithubReaderSlide(repo_url,organization_list,duration,'organization'))

    def get_slides(self):
        return self._slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)

class GithubReaderSlide(PluginSlide):
    def __init__(self,repo_url,list, duration,mark = None):
        print("GithubReaderSlide")
        self._content = {}
        #self._content['title-1'] = {'text':repo_url.split('/')[1]}
        self._content['title-1'] = {'text': 'title'}
        self._content['subtitle-1'] = {'text': 'subtitle'}
        self._duration = duration
        i = 1
        if mark == 'organization':
            self._content['title-1'] = {'text': 'Last modified repositories'}
            self._content['subtitle-1'] = {'text': list['name']}
            print(mark)
            dispText = ''
            print('before dispText')
            for repo in list['repos']:
                dispText += repo+'<br>'
                print(dispText)
                i += 1
            self._content['text-'+str(1)] = {'text': dispText}
            self._content['image-'+str(1)] = {'src': list['avatar-url']}
            #for repo in list['repos']:
            #    self._content['text-'+str(i)] = {'text':list['name']+"<br>"+repo}
            #    self._content['image-'+str(i)] = {'src':list['avatar-url']}
            #    i += 1
        else:
            for elem in list:
                #if mark == 'stat': #TODO
                #    self._content['text-'+str(i)] = elem[message]
                #    self._content['image-'+str(i)] = elem[text]
                print('text-'+str(i))
                print(mark)
                if mark == 'issue':
                    if elem['state'] == 'open':
                        self._content['text-'+str(i)] = {'text': elem['title']+"<br>state : "+"<font color = \"green\">"+elem['state']+"</font>"+"<br>"+elem['comments']}
                    elif elem['state'] == 'closed':
                        self._content['text-'+str(i)] = {'text': elem['title']+"<br>state : "+"<font color = \"red\">"+"closed at : "+"</font>"+elem['closed_at']+"<br>"+elem['comments']}
                    #else TODO, undefined ?
                    self._content['image-'+str(i)] = {'src': elem['avatar_url']}
                elif mark == 'commit':
                    print("commit")
                    print("it : "+str(i))
                    print(elem['message'])
                    print(elem['author'])
                    print(elem['created_at'])
                    print(elem['avatar_url'])
                    self._content['text-'+str(i)] = {'text': elem['author']+"<br>created at : "+elem['created_at']+"<br>"+elem['message']}
                    self._content['image-'+str(i)] = {'src': elem['avatar_url']}
                elif mark == 'release':
                    self._content['text-'+str(i)] = {'text':elem['title']+"<br>author :"+elem['author']+ ", created at : "+elem['created_at']+", version :"+elem['version']+"<br>"+elem['body']}
                    self._content['image-'+str(i)] = ""
                #elif mark == 'contributor': #TODO
                #    self._content['text-'+str(i)] = elem[message]
                #    self._content['image-'+str(i)] = elem[text]
                else:
                    break #raise an error unknown mark (or None mark)
                i += 1
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}


    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        return 'template-image-text-table'

    def __repr__(self):
        return str(self.__dict__)

#if __name__ == "__main__":
#
#    git = GitIctv("TOKEN", 'fdardenne/TestRepo', "scala")
#    t = git.get_organization()
#    print(t)
