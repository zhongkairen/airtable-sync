import requests
import json
import sys


class TokenVerifier:
    def __init__(self, token, project_id, repo_name):
        self.token = token
        self.project_id = project_id
        self.repo_name = repo_name

    def verify(self):
        self.check_rows = [
            {'name': 'Project', 'errors': []},
            {'name': 'Repo', 'errors': []}
        ]
        self._verify_repo()
        self._verify_project()
        self._handle_errors()
        return self.is_valid

    @property
    def is_valid(self):
        return all(len(row['errors']) == 0 for row in self.check_rows)

    @property
    def headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json"
        }

    @property
    def owner(self):
        return self.repo_name.split('/')[0]

    @property
    def repo(self):
        return self.repo_name.split('/')[1]

    def _gql_request(self, query):
        query = {"query": query}
        response = requests.post(
            "https://api.github.com/graphql", headers=self.headers, data=json.dumps(query))

        if response.status_code != 200:
            raise Exception(
                f"Query failed to run by returning code of {response.status_code}. {response.text}")
        return response.json()

    def _query_project_id(self, project_name):
        query = f"""
            query {{
                repository(owner: "{self.owner}", name: "{self.repo}") {{
                    projectsV2(first: 10) {{
                        nodes {{
                            id
                            title
                        }}
                    }}
                }}
            }}
        """

        # Execute the GraphQL request
        result = self._gql_request(query)
        print(result)

        # Filter the results to find the project with the matching name
        projects = (result.get('data', {}).get('repository')
                    or {}).get('projectsV2', {}).get('nodes', [])
        project_id = next(
            (proj.get("id") for proj in projects if proj and proj.get("title") == project_name), None)
        return project_id

    def _verify_repo(self):
        # Verify the repo
        query = f"""
            query {{
                repository(owner: "{self.owner}", name: "{self.repo}") {{
                    id
                    name
                }}
            }}
        """

        result = self._gql_request(query)
        self._verify_repo_access(result)

    def _verify_repo_access(self, response):
        type = "INVALID_RESPONSE"
        errors = self.check_rows[1]['errors']
        if not response:
            return errors.append({'type': type, 'message': 'response not found'})

        repo = response.get('data', {}).get('repository', {})

        if 'errors' in response:
            return errors.extend(response['errors'])

        if not repo:
            return errors.append({'type': type, 'message': 'data.repository not found'})
        if repo.get('id'):
            return

        errors.append({'type': type, 'message': 'unknown error'})

    def _verify_project(self):
        # Verify the project
        query = f"""
            query {{
                node(id: "{self.project_id}") {{
                    ... on ProjectV2 {{
                        id
                        title
                    }}
                }}
            }}
        """

        result = self._gql_request(query)
        self._verify_project_access(result)

    def _verify_project_access(self, response):
        # Verify the user
        type = "INVALID_RESPONSE"
        errors = self.check_rows[0]['errors']
        if not response:
            return errors.append({'type': type, 'message': 'response not found'})

        node = response.get('data', {}).get('node', {})

        if 'errors' in response:
            return errors.extend(response['errors'])

        if not node:
            return errors.append({'type': type, 'message': 'data.node not found'})
        if node.get('id'):
            return

        errors.append({'type': type, 'message': 'unknown error'})

    def _handle_errors(self):
        PROJECT_HINTS = {
            'INVALID_RESPONSE': 'Check token has access to the project.',
            'FORBIDDEN': 'Check token access scope contains `projects` and the project is selected.',
            'NOT_FOUND': 'Check token resource owner is the same as the repo owner.',
        }
        REPO_HINTS = {
            'NOT_FOUND': 'Check token has repository read accesses.'
        }
        for row in self.check_rows:
            errors = row['errors']
            name = row['name']
            for error in errors:
                error_type = error['type']
                hint = ''
                if name == 'Project':
                    hint = PROJECT_HINTS.get(error_type, '')
                elif name == 'Repo':
                    hint = REPO_HINTS.get(error_type, '')

                error['hint'] = hint

    @property
    def checklist(self):
        rows = []
        for row in self.check_rows:
            name = row['name']
            errors = row['errors']
            result = len(errors) == 0
            result = '✅' if result else '❌'
            rows.append(f"{result} {name}")
            for error in errors:
                message = error['message']
                hint = error['hint']
                hint = f"\n    💡{hint}" if hint else ''
                rows.append(f"  - {message}{hint}")

        return "\n".join(rows)


if __name__ == "__main__":
    """
      How to find the project_id:
    OK, to begin with, you need a valid token, so chicken and egg problem.
    First use a valid token to get the project_id, then use the project_id
    here to verify another token.
    """
    """Uncomment the following lines to find the project_id"""
    project_name = ""  # "Ad Request"
    project_id = "PVT_kwDOAAaA1M4ABPtL"

    repo_name = "Unity-Technologies/mz-ad-request-team"

    if len(sys.argv) < 2:
        print("Usage: python verify_token.py <token_file>")
        sys.exit(1)

    token_file = sys.argv[1]

    try:
        with open(token_file, 'r') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print(f"Token file {token_file} not found.")
        sys.exit(1)

    verifier = TokenVerifier(token, project_id, repo_name)

    # Print the project_id for the given project
    if project_name:
        print(verifier._query_project_id(project_name))

    verifier.verify()
    print(verifier.checklist)

    print("Token is {}".format("valid" if verifier.is_valid else "invalid"))
