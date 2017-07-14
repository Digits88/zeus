import responses

from zeus.models import Repository, RepositoryAccess, RepositoryBackend, RepositoryProvider

REPO_DETAILS_RESPONSE = """{
    "id": 1,
    "full_name": "getsentry/zeus",
    "clone_url": "https://github.com/getsentry/zeus.git"
}"""

KEY_RESPONSE = """{
  "id": 1,
  "key": "ssh-rsa AAA...",
  "url": "https://api.github.com/repos/getsentry/zeus/keys/1",
  "title": "zeus",
  "verified": true,
  "created_at": "2014-12-10T15:53:42Z",
  "read_only": true
}"""


def test_repo_list(client, default_login, default_repo, default_repo_access):
    resp = client.get('/api/repos')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == str(default_repo.id)


def test_repo_list_without_access(client, default_login, default_repo):
    resp = client.get('/api/repos')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_new_repository_native(client, default_login, default_user):
    resp = client.post(
        '/api/repos',
        json={
            'provider': 'native',
            'url': 'https://github.com/getsentry/zeus.git',
            'backend': 'git',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id']

    repo = Repository.query.unrestricted_unsafe().get(data['id'])
    assert repo.url == 'https://github.com/getsentry/zeus.git'
    assert repo.backend == RepositoryBackend.git
    assert repo.provider == RepositoryProvider.native
    assert repo.external_id is None

    access = list(RepositoryAccess.query.filter(RepositoryAccess.repository_id == repo.id))
    assert len(access) == 1
    assert access[0].user_id == default_user.id


def test_new_repository_github(client, default_login, default_user, default_identity):
    responses.add(
        'GET',
        'https://api.github.com/repos/getsentry/zeus',
        match_querystring=True,
        body=REPO_DETAILS_RESPONSE
    )

    responses.add('POST', 'https://api.github.com/repos/getsentry/zeus/keys', body=KEY_RESPONSE)

    resp = client.post(
        '/api/repos', json={
            'provider': 'github',
            'github.name': 'getsentry/zeus',
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['id']

    repo = Repository.query.unrestricted_unsafe().get(data['id'])
    assert repo.url == 'https://github.com/getsentry/zeus.git'
    assert repo.backend == RepositoryBackend.git
    assert repo.provider == RepositoryProvider.github
    assert repo.external_id == '1'
    assert repo.data == {'github': {'full_name': 'getsentry/zeus'}}

    access = list(RepositoryAccess.query.filter(RepositoryAccess.repository_id == repo.id))
    assert len(access) == 1
    assert access[0].user_id == default_user.id
