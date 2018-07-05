# -*- coding: utf-8 -*-
#
#    Written by Dardenne Florent, Fiset Alexandre, Gobeaux Alexandre
#
#    ICTV github-reader is free plugin software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ICTV github-reader is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with ICTV github-reader.  If not, see <http://www.gnu.org/licenses/>.

from pyquery import PyQuery
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
import urllib.request
from github import Github
from datetime import datetime, timedelta

def get_content(channel_id):
    channel = PluginChannel.get(channel_id)
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('github_reader', channel)
    token = channel.get_config_param('token')
    duration = channel.get_config_param('duration')*1000
    repo_url = channel.get_config_param('repo_url')
    had_organization = channel.get_config_param('had_organization')
    number_organizations = channel.get_config_param('number_organizations')
    orga_url = channel.get_config_param('orga_url')
    disp_commits = channel.get_config_param('disp_commits')
    number_commits = channel.get_config_param('number_commits')
    max_days_commit = channel.get_config_param('max_days_commit')
    disp_contributors = channel.get_config_param('disp_contributors')
    number_contributors = channel.get_config_param('number_contributors')
    disp_issues = channel.get_config_param('disp_issues')
    number_issues = channel.get_config_param('number_issues')
    disp_stat = channel.get_config_param('disp_stat')
    disp_releases = channel.get_config_param('disp_releases')
    number_releases = channel.get_config_param('number_releases')
    if not token or not repo_url:
        logger.warning('Some of the required parameters are empty', extra=logger_extra)
        return []

    git_obj = Github(token)
    capsule = GithubReaderCapsule()


    #if disp_stat:
    #    stat = git_obj.get_stat()
    if disp_issues:
        capsule._slides.append(GithubReaderSlideIssue(repo_url, number_issues, duration, git_obj,logger,logger_extra))
    if disp_commits:
        capsule._slides.append(GithubReaderSlideCommit(repo_url, number_commits, duration, git_obj,max_days_commit,logger,logger_extra))
    if disp_releases:
        capsule._slides.append(GithubReaderSlideRelease(repo_url, number_releases, duration, git_obj,logger,logger_extra))
    if disp_contributors:
        capsule._slides.append(GithubReaderSlideContributor(repo_url, number_contributors, duration, git_obj,logger,logger_extra))
    if had_organization:
        capsule._slides.append(GithubReaderSlideOrganization(orga_url, number_organizations, duration, git_obj,logger,logger_extra))


    return [capsule]

def is_uptodate(date_object, day):
    day = 3
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
    def __init__(self, repo_url, nb_elem,duration,git_obj,logger,logger_extra):

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

class GithubReaderSlideCommit(GithubReaderSlide):
    def __init__(self, repo_url, number_of_commits, duration, git_obj,max_days,logger,logger_extra):
        repo = git_obj.get_repo(repo_url)
        commits = repo.get_commits()
        commit_list = []
        for commit in commits[:number_of_commits]:
            message = commit.commit.message
            message = message.split("\n")[0]
            name = commit.author.name
            if(not name):
                name = "Undefined"
            commit_list.append({'author': name, 'message': message, "created_at": commit.commit.author.date.strftime("%d %B %Y %H:%M"), 'avatar_url':commit.author.avatar_url})
        self._content = {}
        self._content['title-1'] = {'text':repo_url.split('/')[1]}
        self._content['subtitle-1'] = {'text': "Commits"}
        self._duration = duration
        i = 1
        for elem in commit_list:
            self._content['text-'+str(i)] = {'text': elem['author']+"<br>created at : "+elem['created_at']+"<br>"+elem['message']}
            self._content['image-'+str(i)] = {'src': elem['avatar_url']}
            i += 1
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}

class GithubReaderSlideRelease(GithubReaderSlide):
    def __init__(self, repo_url, number_releases, duration, git_obj,logger,logger_extra):
        print('GithubReaderSlideRelease')
        self._content = {}
        self._content['title-1'] = {'text': repo_url.split('/')[1]}
        self._content['subtitle-1'] = {'text': 'Recent releases'}
        self._duration = duration
        repo = git_obj.get_repo(repo_url)
        releases = repo.get_releases()
        print(releases)
        if(not releases):
            logger.warning('no release', extra=logger_extra)
        #print(releases.totalCount)
        for i,release in enumerate(releases[:number_releases]):
            print("i'm in !")
            name = release.author.name
            if(not name):
                name = "Undefined"
            self._content['text-'+str(i+1)] = {'text': release.title+" released on "+release.created_at.strftime("%d %B %Y %H:%M")+" by "+name+" version "+release.tag_name}
            self._content['image-'+str(i+1)] = {'src': ''}
        print('after for')
        if('text-1' not in self._content):
            self._content['text-'+str(1)] = {'text': 'There is no release'}
            self._content['image-'+str(1)] = {'src': 'plugins/github_reader/mfcry.png'}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}


class GithubReaderSlideContributor(GithubReaderSlide):
    def __init__(self,repo_url,number_contributors,duration,git_obj,logger,logger_extra):
        self._content = {}
        self._content['title-1'] = {'text':repo_url.split('/')[1]}
        self._content['subtitle-1'] = {'text': 'Week\'s '+str(number_contributors)+' most contributors'}
        self._duration = duration

        contributors = git_obj.get_repo(repo_url).get_stats_contributors()
        sorted_contributors = sorted(contributors, reverse=True, key=lambda k: k.weeks[-1].c)
        for i,contributor in enumerate(sorted_contributors[:number_contributors]):
            print(contributor.weeks[-1].w.strftime("%d %B %Y %H:%M"))
            print('it :'+str(i))
            try:
                name = contributor.author.name
                if(not name):
                    name = 'Undefined'
                self._content['text-'+str(i+1)] = {'text': name+"<br>"+"# commits : "+str(contributor.weeks[-1].c)}
            except Exception as e:
                print('except')
                #logger.warning('Missing contributor attibuts', extra=logger_extra)
            self._content['image-'+str(i+1)] = {'src': contributor.author.avatar_url}
        self._content['subtitle-1'] = {'text': 'Best contributors since '+sorted_contributors[0].weeks[-1].w.strftime("%d %B %Y %H:%M")}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}
class GithubReaderSlideOrganization(GithubReaderSlide):
    def __init__(self, orga_url, number_organizations, duration, git_obj,logger,logger_extra):
        if not orga_url:
            logger.warning('No oraganisation provide', extra=logger_extra)
        organization = git_obj.get_organization(orga_url)
        if not oraganisation:
            logger.warning('No oraganisation found', extra=logger_extra)

        repos_organization = []

        repos = [e for e in organization.get_repos()] #easier to print repos, makes a list from a Paginated list(which has not a suitable print function)

        sorted_repos = sorted(repos, reverse=True, key=lambda k: k.updated_at)
        for repo in sorted_repos[:number_organizations]:
            repos_organization.append('<p font-weigth = "900">'+repo.full_name.split('/')[1]+'</p>'+' updated at : ' + repo.updated_at.strftime("%d %B %Y %H:%M")) #TODO if datetime = vide ??

        dico = {"avatar-url": organization.avatar_url, "name": organization.name, "repos":repos_organization}

        self._content = {}
        self._content['title-1'] = {'text': 'Last modified repos'}
        self._content['subtitle-1'] = {'text': organization.name}
        self._duration = duration
        dispText = ''
        i = 1
        for repo in repos_organization:
            dispText += repo+'<br>'
            i += 1
        self._content['text-'+str(1)] = {'text': dispText}
        self._content['image-'+str(1)] = {'src': organization.avatar_url}
        self._content['background-1']={'src': 'plugins/github_reader/github-background.png', 'color': 'black', 'size': 'content'}

class GithubReaderSlideStat():
  pass
