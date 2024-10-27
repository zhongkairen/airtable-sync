from python_graphql_client import GraphqlClient
from .config import GitHubConfig
from .graphqlquery import GraphQLQuery
from .issue import GitHubIssue
from ..custom_logger import CustomLogger

logger = CustomLogger(__name__)


class GitHubClient:
    """Client for interacting with a GitHub repository."""

    def __init__(self, github_config: GitHubConfig):
        """Initializes the GitHub client with the given configuration."""
        self.github_config = github_config
        self._query = GraphQLQuery(github_config)
        self._client = GraphqlClient(endpoint="https://api.github.com/graphql")
        self.epic_issues = []

    @property
    def config(self):
        """GitHub configuration."""
        return self.github_config

    @property
    def query(self):
        """GitHub GraphQL query."""
        return self._query

    def fetch_project_id(self):
        """
        Fetch the project ID for the given project name.
        If the project name is found, it will be set to configuration, otherwise an exception is raised.
        """
        response = self._client.execute(
            query=self._query.project(), headers=self._query.headers())

        if 'errors' in response:
            raise Exception(f"Error fetching project ID: {response['errors']}")

        projects = response['data']['repository']['projectsV2']['nodes']
        project = next(
            (p for p in projects if p['title'] == self.github_config.project_name), None)
        if project:
            self.github_config.project_id = project['id']
            return

        raise Exception(
            f"Failed to fetch project ID for project: {self.github_config.project_name}")

    def fetch_project_items(self):
        """Fetch items from the GitHub project and their field values."""
        after_cursor = None
        has_next_page = True
        total_items = 0
        page_size = 50

        logger.verbose(
            f"Fetching issues for project: {self.github_config.project_name} ({self.github_config.project_id})")
        while has_next_page:
            response = self._client.execute(
                query=self._query.issues(
                    page_size=page_size, after_cursor=after_cursor),
                headers=self._query.headers())

            if 'errors' in response:
                raise Exception(f"Error fetching items: {response['errors']}")

            response_items = response['data']['node']['items']
            total_items += self._handle_issues_data(response_items['nodes'])

            page_info = response_items['pageInfo']
            has_next_page = page_info['hasNextPage']
            after_cursor = page_info['endCursor']

        logger.verbose(
            f"Found {len(self.epic_issues)} epic issues out of {total_items} items")
        for issue in self.epic_issues:
            logger.debug(f"{issue.issue_number} - {issue.title}")

    def fetch_issue(self, issue_number: int) -> GitHubIssue:
        """Fetch the issue details from GitHub and return the issue object."""
        issue = self.get_issue(issue_number)
        if issue:
            return issue

        query = self.query.issue(issue_number)
        response = self._client.execute(
            query=query, headers=self.query.headers())
        if 'errors' in response:
            logger.error(f"Errors in response: {response}")
            raise Exception(f"Error fetching items: {response['errors']}")

        item = response['data']['repository']['issue']
        fields = item.get('projectItems', {}).get('nodes')
        first_issue_fields = (fields[0] if fields else {})
        issue = GitHubIssue(url=item.get('url'))
        issue.load_fields(item, first_issue_fields)
        return issue

    def get_issue(self, issue_number: int) -> GitHubIssue:
        """Get the issue details from loaded epic issue list."""
        return next((issue for issue in self.epic_issues if issue.issue_number == issue_number), None)

    def _handle_issues_data(self, items) -> int:
        """
        Extract and process issue data from the provided items.
        Look for issues marked as epics and append them to the `epic_issues` list.
        Args:
            items (list): A list of dictionaries containing issue data.
        Returns:
            int: The number of items processed.
        """

        epic_issues = []
        for item in items:
            content = item.get('content')
            if not content:
                continue
            issue = GitHubIssue(url=content.get('url'))
            issue.load_fields(base_data=content, fields=item)

            if (issue.is_epic):
                epic_issues.append(issue)

        self.epic_issues.extend(epic_issues)
        return len(items)
