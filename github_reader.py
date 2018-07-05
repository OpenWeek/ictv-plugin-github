from pyquery import PyQuery
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
import urllib.request
from ictv.plugins.github_reader.githubApp import GitIctv
from github import Github
from datetime import datetime, timedelta

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
    max_days_commit = channel.get_config.param('max_days_commit')
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

    git_obj = Github(token)
    capsule = GithubReaderCapsule()

    print("After init gitIctv")

    #if disp_stat:
    #    stat = git_obj.get_stat()
    if disp_issues:
        capsule._slides.append(GithubReaderSlideIssue(repo_url, number_issues, duration, git_obj))
    if disp_commits:
        capsule._slides.append(GithubReaderSlideCommit(repo_url, number_commits, duration,max_days_commit, git_obj))
    if disp_releases:
        release_list = git_obj.get_release()
    if disp_contributors:
        contributor_list = git_obj.get_contributor(repo_url,number_contributors,duration,git_obj)
    if had_organization:
        capsule._slides.append(GithubReaderSlideOrganization(orga_url, number_organizations, duration, git_obj))

    print("BeforeReturn")

    return [capsule]

def is_uptodate(date_object, day):
    now = datetime.now()
    duration_of_days = timedelta(days=day)

    date_limit = now - duration_of_days
    return date_object < date_limit


class GithubReaderCapsule(PluginCapsule):

    def __init__(self):
    		self._slides = []

    def get_slides(self):
        return self._slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)

class GithubReaderSlide(PluginSlide):
    def __init__(self):
        pass
    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        return 'template-image-text-table'

    def __repr__(self):
        return str(self.__dict__)

class GithubReaderSlideIssue(GithubReaderSlide):
    def __init__(self, repo_url, nb_elem,duration,git_obj):

        self._content = {}
        self._content['title-1'] = {'text':repo_url.split('/')[1]}
        self._content['subtitle-1'] = {'text': 'Last modified issues'}
        self._duration = duration

        issues = git_obj.get_repo(repo_url).get_issues(state="all")
        for i,issue in enumerate(issues[:nb_elem]):
            if issue.state == 'open':
                self._content['text-'+str(i+1)] = {'text': issue.title+"<br>"+"<font color = \"#7FFF00\">"+"opened"+"</font>"+" on "+issue.created_at.strftime("%d %B %Y %H:%M")+"<br>"+"# comments : "+str(issue.comments)}
            elif issue.state == 'closed':
              	self._content['text-'+str(i+1)] = {'text': issue.title+"<br>"+"<font color = \"red\">"+"closed"+"</font>"+" on "+issue.closed_at.strftime("%d %B %Y %H:%M")+"<br>"+"# comments : "+str(issue.comments)}
            else:
              	try:
                    logger.warning('None state issue'+issue.title, extra=logger_extra)
              	except Exception as e:
                    logger.warning('None state issue', extra=logger_extra)
            self._content['image-'+str(i+1)] = {'src': issue.user.avatar_url}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}

#=====================================FLO
class GithubReaderSlideCommit(GithubReaderSlide):
    def __init__(self, repo_url, number_of_commits, duration, max_days, git_obj):
        repo = git_obj.get_repo(repo_url)
        commits = repo.get_commits()
        commit_list = []
        for commit in commits[:number_of_commits]:
            message = commit.commit.message
            message = message.split("\n")[0]
            name = commit.author.name
            created_at = commit.commit.author.datetime

            if(not name):
                name = "Undefined"

            if(is_uptodate(created_at, max_days)):
                commit_list.append({'author': name, 'message': message, "created_at": commit.commit.author.date.strftime("%d %B %Y %H:%M"), 'avatar_url':commit.author.avatar_url})
        	#TODO SEE IF MORE THAN 0 COMMITS
            if(len(commit_list) > 0):
                self._content = {}
                self._content['title-1'] = {'text':repo_url.split('/')[1]}
                self._content['subtitle-1'] = {'text': "Commits"}
                self._duration = duration
                i = 1
                for elem in commit_list:
                    print("commit")
                    print("it : "+str(i))
                    print(elem['message'])
                    print(elem['author'])
                    print(elem['created_at'])
                    print(elem['avatar_url'])
                    self._content['text-'+str(i)] = {'text': elem['author']+"<br>created at : "+elem['created_at']+"<br>"+elem['message']}
                    self._content['image-'+str(i)] = {'src': elem['avatar_url']}
                    i += 1
                self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}
            else:
                self._content = {}
                self._duration = duration
                self._content['text-1'] = {'text': "There is no new commit"}
                self._content['image-1'] = {'src': "plugins/github_reader/mfcry.png"}

#=====================================END FLO




class GithubReaderSlideRelease():
  pass
class GithubReaderSlideContributor(GithubReaderSlide):
    def __init__(self,repo_url,number_contributors,duration,git_obj)
        self._content = {}
        self._content['title-1'] = {'text':repo_url.split('/')[1]}
        self._content['subtitle-1'] = {'text': 'Week\'s '+str(number_contributors)+' most contributors'}
        self._duration = duration

        contributors = git_obj.get_repo(repo_url).get_stats_contributors()
        for i,contributor in enumerate(contributors[:nb_elem]):
            try:
                self._content['text-'+str(i+1)] = {'text': contributors.author+"<br>"+"# commits lines : "+str(contributor.total)}
          	except Exception as e:
                logger.warning('Missing contributor attibuts', extra=logger_extra)
            self._content['image-'+str(i+1)] = {'src': contributor.author.avatar_url}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}

class GithubReaderSlideOrganization(GithubReaderSlide):
    def __init__(self, orga_url, number_organizations, duration, git_obj):
        #git_obj = Github(token)
        organization = git_obj.get_organization(orga_url)
        # et si organization n'existe pas ???? TODO

        repos_organization = []

        repos = [e for e in organization.get_repos()] #easier to print repos, makes a list from a Paginated list(which has not a suitable print function)

        print(repos)
        sorted_repos = sorted(repos, reverse=True, key=lambda k: k.updated_at)
        print(sorted_repos)
        for repo in sorted_repos[:number_organizations]:
        #for count in range(number_organizations):
        #    repo = sorted_repos[count]
            print(repo,repo.updated_at)
            print(repo.full_name.split('/')[1])
            # FORMAT TODO
            repos_organization.append('<B>'+repo.full_name.split('/')[1]+'</B>'+' updated at : ' + repo.updated_at.strftime("%d %B %Y %H:%M")) #TODO if datetime = vide ??

        dico = {"avatar-url": organization.avatar_url, "name": organization.name, "repos":repos_organization}

        self._content = {}
        self._content['title-1'] = {'text': 'Last modified repos'}
        self._content['subtitle-1'] = {'text': organization.name}
        self._duration = duration
        print('organization')
        dispText = ''
        print('before dispText')
        i = 1
        for repo in repos_organization:
            dispText += repo+'<br>'
            print(dispText)
            i += 1
        self._content['text-'+str(1)] = {'text': dispText}
        self._content['image-'+str(1)] = {'src': organization.avatar_url}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}

class GithubReaderSlideStat():
  pass
