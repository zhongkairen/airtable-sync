
from .config import GitHubConfig


class GraphQLQuery:
    def __init__(self, github_config: GitHubConfig):
        self.github_config = github_config

    def issue(self, issue_number: int):
        return f"""
        query {{
        repository(owner: "{self.github_config.repo_owner}", name: "{self.github_config.repo_name}") {{
            issue(number: {issue_number}) {{
            title
            body
            assignees(first: 10) {{
                nodes {{
                    login
                }}
            }}
            labels(first: 10) {{
                nodes {{
                    name
                    color
                }}
            }}
            projectItems(first: 1) {{
                nodes {{
                fieldValues(first: 10) {{
                    nodes {{
                    ... on ProjectV2ItemFieldSingleSelectValue {{
                        name
                        field {{
                            ... on ProjectV2FieldCommon {{
                                name
                            }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldTextValue {{
                        text
                        field {{
                            ... on ProjectV2FieldCommon {{
                                name
                            }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldDateValue {{
                        date
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                            }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldNumberValue {{
                        number
                        field {{
                            ... on ProjectV2FieldCommon {{
                                name
                            }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldIterationValue {{
                        duration
                        startDate
                        title
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    }}
                }}
                }}
            }}
            }}
        }}
        }}
        """

    def issues(self, after_cursor: int, page_size: int = 20):
        """Constructs a GraphQL query to fetch issues from a GitHub project.
           Pull requests and draft issues are not included in the query, but will be included in the query response.
        Args:
            after_cursor (int): The cursor after which to fetch the next set of issues.
            page_size (int, optional): The number of issues to fetch per page. Defaults to 20.
        Returns:
            str: The constructed GraphQL query string.
        """
        query = f"""
        query {{
        node(id: "{self.github_config.project_id}") {{
            ... on ProjectV2 {{
            items(first: {page_size}, after: "{after_cursor}") {{
                nodes {{
                id
                fieldValues(first: 20) {{
                    nodes {{
                    ... on ProjectV2ItemFieldTextValue {{
                        text
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldDateValue {{
                        date
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldSingleSelectValue {{
                        name
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldNumberValue {{
                        number
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    ... on ProjectV2ItemFieldIterationValue {{
                        duration
                        startDate
                        title
                        field {{
                        ... on ProjectV2FieldCommon {{
                            name
                        }}
                        }}
                    }}
                    }}
                }}
                content {{
                    ... on Closable {{
                        closed
                        closedAt
                    }}
                    ... on Issue {{
                    title
                    url
                    state
                    body
                    assignees(first: 10) {{
                        nodes {{
                        login
                        }}
                    }}
                    labels(first: 10) {{
                        nodes {{
                            name
                            color
                        }}
                    }}
                    }}
                }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
            }}
        }}
        }}
        """
        return query

    def project(self):
        query = f"""
        query {{
        repository(owner: "{self.github_config.repo_owner}", name: "{self.github_config.repo_name}") {{
            projectsV2(first: 100) {{
            nodes {{
                id
                title
            }}
            }}
        }}
        }}
        """
        return query

    def headers(self):
        return {"Authorization": f"Bearer {self.github_config.token}"}
