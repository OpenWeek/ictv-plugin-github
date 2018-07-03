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
                issue_list.append({'title':issues[issue].title, 'state': issues[issue].state, 'closed_at': issues[issue].closed_at, 'created_at': issues[issue].created_at, 'comments': issues[issue].comments, 'avatar_url': issues[issue].user.avatar_url })
            except Exception as e:
                print(e)
                break

        if len(issue_list) >0:
            return issue_list

        return None

    def get_release(self):
        releases = self.repo.get_releases()
        try:
            release = releases[0]
            #TO-DO Pas moyen de get l'auteur ainsi que son logo
            return {'title': release.title, 'author': release.author.name, 'body': release.body, 'created_at': release.created_at, 'version': release.tag_name}
        except:
            return None

    def get_commit(self, number_of_commits):
        commits = self.repo.get_commits()
        commit_list = []
        for commit in range(number_of_commits):
            try:
                message = commits[commit].commit.message
                message = message.split("\n")[0]
                commit_list.append({'author': commits[commit].author.name, 'message': message, "created_at": commits[commit].commit.author.date, 'avatar_url':commits[commit].author.avatar_url })
            except Exception as e:
                print(e)
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
    git = GitIctv("TOKEN", 'REPO')
