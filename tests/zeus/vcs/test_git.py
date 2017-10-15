def _set_author(remote_path, name, email):
        'cd {0} && git config --replace-all "user.name" "{1}"'.format(
            remote_path, name),
        'cd {0} && git config --replace-all "user.email" "{1}"'.format(
            remote_path, email),
def vcs(git_repo_config, default_repo):
    return GitVcs(url=git_repo_config.url, path=git_repo_config.path, id=default_repo.id.hex)
def test_get_default_revision(git_repo_config, vcs):
def test_log_with_authors(git_repo_config, vcs):
    _set_author(git_repo_config.remote_path,
                'Another Committer', 'ac@d.not.zm.exist')
        'cd %s && touch BAZ && git add BAZ && git commit -m "bazzy"' % git_repo_config.remote_path, shell=True
    assert_revision(
        revisions[0], author='Another Committer <ac@d.not.zm.exist>', message='bazzy')
    assert_revision(
        revisions[0], author='Another Committer <ac@d.not.zm.exist>', message='bazzy')
def test_log_with_branches(git_repo_config, vcs):
    remote_path = git_repo_config.remote_path
    check_call('cd %s && git checkout %s' %
               (remote_path, vcs.get_default_revision(), ), shell=True)
        'cd %s && touch IPSUM && git add IPSUM && git commit -m "3rd branch"' % (
            remote_path, ),
    assert_revision(
        previous_rev, message='second branch commit', branches=['B2'])
    assert_revision(revisions[3], message='test', branches=[
                    vcs.get_default_revision(), 'B2', 'B3'])
    assert_revision(revisions[2], message='test', branches=[
                    vcs.get_default_revision(), 'B2', 'B3'])
    check_call('cd %s && git checkout %s' %
               (remote_path, vcs.get_default_revision(), ), shell=True)
    assert len(revision.sha) == 40
    assert revisions[0].parents == [revisions[1].sha]
    diff = vcs.export(revisions[0].sha)
        child_in_question=revisions[0].sha, parent_in_question=revisions[1].sha
        child_in_question=revisions[1].sha, parent_in_question=revisions[0].sha
def test_get_known_branches(git_repo_config, vcs):
    check_call('cd %s && git checkout -B test_branch' %
               git_repo_config.remote_path, shell=True)