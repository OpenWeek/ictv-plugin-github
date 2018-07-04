from github import Github


class GitIctv():

    def __init__(self, token, repo, organization=None):
        self.g = Github(token)
        self.repo = self.g.get_repo(repo)
        self.organization = None

        if(organization):
            self.organization = self.g.get_organization("scala")



    def get_issue(self, number_of_issues):
        issues = self.repo.get_issues(state="all")
        issue_list = []
        for issue in range(number_of_issues):
            try:
                issue_list.append({'title':issues[issue].title, 'state': issues[issue].state, 'closed_at': issues[issue].closed_at.strftime("%d %B, %Y"), 'created_at': issues[issue].created_at.time.strftime("%d %B, %Y"), 'comments': issues[issue].comments, 'avatar_url': issues[issue].user.avatar_url })
            except Exception as e:
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
                break

        if len(commit_list) > 0:

            return commit_list


        return None

    def get_organization(self):
        if (self.organization):
            repos_organization = []
            repos = self.organization.get_repos()
            for repo in repos:
                repos_organization.append(repo.name)

            return {"avatar-url": self.organization.avatar_url, "name": self.organization.name, "repos":repos_organization}
        else:
            return None

    def top_contributor(self, number_of_contributors):
        pass




if __name__ == "__main__":

    git = GitIctv("8f56162284548f2917b7fa22f9e8cc70e3279839", 'scala/scala', "scala")
    print(git.get_issue(5))
