from src.helpers.github import GHHelper

class TestGHHelper:
    # TODO: Mock out the GitHub API calls, write proper tests
    def test_create(self):
        gh_helper = GHHelper("token", "repo")
        assert gh_helper is not None