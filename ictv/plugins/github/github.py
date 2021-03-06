# -*- coding: utf-8 -*-
#
#    Written by Dardenne Florent, Fiset Alexandre, Gobeaux Alexandre
#
#    ICTV-plugin-github is free plugin software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ICTV-plugin-github is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with ICTV-plugin-github.  If not, see <http://www.gnu.org/licenses/>.
import datetime

from github import Github as GithubAPI
from ictv.models.channel import PluginChannel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide


class NoContentError(ValueError):
    pass


def get_date_str(d, date_format="%d %B %Y %H:%M"):
    return d.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime(date_format)


def get_content(channel_id):
    channel = PluginChannel.get(channel_id)
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('github', channel)
    token = channel.get_config_param('token')
    duration = channel.get_config_param('duration') * 1000
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

    git_obj = GithubAPI(token)
    capsule = GithubReaderCapsule()

    if disp_issues:
        try:
            capsule.slides.append(GithubReaderSlideIssue(repo_url, number_issues, duration, git_obj, logger, logger_extra))
        except NoContentError:
            pass
        except:
            logger.info('An exception occurred when generating the issues slide', exc_info=True, extra=logger_extra)
    if disp_commits:
        try:
            capsule.slides.append(GithubReaderSlideCommit(repo_url, number_commits, duration, git_obj, max_days_commit, logger, logger_extra))
        except NoContentError:
            pass
        except:
            logger.info('An exception occurred when generating the commits slide', exc_info=True, extra=logger_extra)
    if disp_releases:
        try:
            capsule.slides.append(GithubReaderSlideRelease(repo_url, number_releases, duration, git_obj, logger, logger_extra))
        except NoContentError:
            pass
        except:
            logger.info('An exception occurred when generating the releases slide', exc_info=True, extra=logger_extra)
    if disp_contributors:
        try:
            capsule.slides.append(GithubReaderSlideContributor(repo_url, number_contributors, duration, git_obj, logger, logger_extra))
        except NoContentError:
            pass
        except:
            logger.info('An exception occurred when generating the contributors slide', exc_info=True, extra=logger_extra)
    if had_organization:
        try:
            capsule.slides.append(GithubReaderSlideOrganization(orga_url, number_organizations, duration, git_obj, logger, logger_extra))
        except NoContentError:
            pass
        except:
            logger.info('An exception occurred when generating the organisation slide', exc_info=True, extra=logger_extra)

    return [capsule]


class GithubReaderCapsule(PluginCapsule):
    def __init__(self):
        self.slides = []

    def get_slides(self):
        return self.slides

    def get_theme(self):
        return None

    def __repr__(self):
        return str(self.__dict__)


class GithubReaderSlide(PluginSlide):
    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        return 'template-github'

    def __repr__(self):
        return str(self.__dict__)


class GithubReaderSlideIssue(GithubReaderSlide):
    def __init__(self, repo_url, number_issues, duration, git_obj, logger, logger_extra):

        self._content = {'title-1': {'text': repo_url.split('/')[1]}, 'subtitle-1': {'text': 'Last modified issues'}}
        self._duration = duration

        issues = git_obj.get_repo(repo_url).get_issues(state="all")
        for i, issue in enumerate(issues[:number_issues]):
            if issue.state == 'open':
                self._content['text-' + str(i + 1)] = {
                    'text': '{}<br><font color = \"#7FFF00\">opened</font> on {}<br># comments : {}'
                    .format(issue.title, get_date_str(issue.created_at), str(issue.comments))
                }
            elif issue.state == 'closed':
                self._content['text-' + str(i + 1)] = {
                    'text': '{}<br><font color = \"red\">closed</font> on {}<br># comments : {}'
                    .format(issue.title, get_date_str(issue.created_at), str(issue.comments))}
            self._content['image-' + str(i + 1)] = {'src': issue.user.avatar_url}
        self._content['background-1'] = {'src': 'plugins/github/github-background.png', 'color': 'black',
                                         'size': 'content'}


class GithubReaderSlideCommit(GithubReaderSlide):
    def __init__(self, repo_url, number_commits, duration, git_obj, max_days, logger, logger_extra):
        self._content = {'title-1': {'text': repo_url.split('/')[1]}, 'subtitle-1': {'text': "Commits"},
                         'background-1': {'src': 'plugins/github/github-background.png', 'color': 'black',
                                          'size': 'content'}}
        self._duration = duration

        repo = git_obj.get_repo(repo_url)
        for i, commit in enumerate(repo.get_commits()[:number_commits]):
            message = commit.commit.message.split("\n")[0]
            name = commit.author.name or commit.author.login
            self._content['text-' + str(i+1)] = {
                'text': '{}<br>committed on {}<br><i>{}</i> &mdash; (<span style="color: green">+{}</span>&nbsp;&nbsp;<span style="color: red;">-{}</span>)'
                .format(name, get_date_str(commit.commit.author.date), message, commit.stats.additions, commit.stats.deletions)
            }
            self._content['image-' + str(i+1)] = {'src': commit.author.avatar_url}


class GithubReaderSlideRelease(GithubReaderSlide):
    def __init__(self, repo_url, number_releases, duration, git_obj, logger, logger_extra):
        self._content = {'title-1': {'text': repo_url.split('/')[1]}, 'subtitle-1': {'text': 'Recent releases'}}
        self._duration = duration
        repo = git_obj.get_repo(repo_url)
        releases = repo.get_releases()
        if not releases:
            logger.warning('no release', extra=logger_extra)
        for i, release in enumerate(releases[:number_releases]):
            name = release.author.name
            if not name:
                name = "Undefined"
            self._content['text-' + str(i + 1)] = {
                'text': '{} released on {} by {} version {}'
                .format(release.title, get_date_str(release.created_at), name, release.tag_name)
            }
            self._content['image-' + str(i + 1)] = {'src': ''}
        if 'text-1' not in self._content:
            raise NoContentError()
        self._content['background-1'] = {'src': 'plugins/github/github-background.png', 'color': 'black',
                                         'size': 'content'}


class GithubReaderSlideContributor(GithubReaderSlide):
    def __init__(self, repo_url, number_contributors, duration, git_obj, logger, logger_extra):
        self._content = {'title-1': {'text': repo_url.split('/')[1]}}
        self._duration = duration

        contributors = git_obj.get_repo(repo_url).get_stats_contributors()
        sorted_contributors = sorted(contributors, reverse=True, key=lambda k: k.weeks[-1].c)
        for i, contributor in enumerate(sorted_contributors[:number_contributors]):
            name = contributor.author.name or contributor.author.login
            week_contribution = contributor.weeks[-1]
            if week_contribution.c == 0:
                break
            self._content['text-' + str(i + 1)] = {
                'text': '{}<br># commits: {}<br><span style="color: green">+{}</span>&nbsp;&nbsp;<span style="color: '
                        'red;">-{}</span>'.format(name, week_contribution.c, week_contribution.a, week_contribution.d)
            }
            self._content['image-' + str(i + 1)] = {'src': contributor.author.avatar_url}
        self._content['subtitle-1'] = {
            'text': 'Best contributors since ' + get_date_str(sorted_contributors[0].weeks[-1].w, date_format='%d %B %Y')}
        self._content['background-1'] = {'src': 'plugins/github/github-background.png', 'color': 'black',
                                         'size': 'content'}


class GithubReaderSlideOrganization(GithubReaderSlide):
    def __init__(self, orga_url, number_organizations, duration, git_obj, logger, logger_extra):
        if not orga_url:
            logger.warning('No organization provided', extra=logger_extra)
            raise NoContentError()
        organization = git_obj.get_organization(orga_url)
        if not organization:
            logger.warning('No organization found', extra=logger_extra)
            raise NoContentError()

        repos_organization = []

        repos = [e for e in organization.get_repos()]  # easier to print repos, makes a list from a Paginated list (which has not a suitable print function)

        sorted_repos = sorted(repos, reverse=True, key=lambda k: k.updated_at)
        for repo in sorted_repos[:number_organizations]:
            repos_organization.append(
                '<p><p style=\"font-weight: 900;\">{}</p><i style="font-size: 80%;">{}</i><p>updated on {}'
                .format(repo.full_name.split('/')[1], repo.description or '', get_date_str(repo.updated_at)))

        self._content = {'title-1': {'text': 'Last modified repos'}, 'subtitle-1': {'text': organization.name}}
        self._duration = duration
        dispText = ''
        i = 1
        for repo in repos_organization:
            dispText += repo + '<br>'
            i += 1
        self._content['text-' + str(1)] = {'text': dispText}
        self._content['image-' + str(1)] = {'src': organization.avatar_url}
        self._content['background-1'] = {'src': 'plugins/github/github-background.png', 'color': 'black',
                                         'size': 'content'}
