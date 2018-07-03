from github import Github


class GitIctv():

    def __init__(self, token, repo, organization=None):
        self.g = Github(token)
        self.repo = self.g.get_repo(repo)
        self.organization = None

        if(organization):
            self.organization = self.g.get_organization(organization)



    def get_issue(self, number_of_issues):
        issues = self.repo.get_issues()
        issue_list = []
        for issue in range(number_of_issues):
            try:
                print(issues[issue].user.avatar_url)
                issue_list.append({'title':issues[issue].title, 'state': issues[issue].state, 'closed_at': issues[issue].closed_at, 'created_at': issues[issue].created_at, 'comments': issues[issue].comments, 'avatar': issues[issue].user.avatar_url })
            except Exception as e:
                break

        if len(issue_list) >0:
            return issue_list

        return None

    def get_release(self):
        releases = self.repo.get_releases()
        try:
            release = releases[0]
            return {'title': release.title, 'author': release.author, 'body': release.body, 'created_at': release.created_at, 'version': release.tag_name}
        except:
            return None

    def get_commit(self, number_of_commits):
        commits = self.repo.get_commits()
        commit_list = []
        for commit in range(number_of_commits):
            try:
                commit_list.append({'author': commits[commit].author, 'message': message, "created_at": commits[commit].created_at})
            except:
                break

        if len(commit_list) > 0:
            return commit_list

        return None

    def get_organization(self):
        if (self.organization):
            pass
        else:
            return None



if __name__ == "__main__":
    git = GitIctv("a275dcebd8a153fa547861ed291f39424571a4a2", 'fdardenne/TestRepo')
    t = git.get_issue(5)
    print(type(t))
    #git = Github("a275dcebd8a153fa547861ed291f39424571a4a2").get_organization("scala")
    #print(git.avatar_url)
