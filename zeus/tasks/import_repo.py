from __future__ import absolute_import, print_function

import logging

from celery import shared_task
from datetime import datetime

from zeus.config import db
from zeus.models import Repository, RepositoryStatus

logger = logging.getLogger('repo.sync')


@shared_task(max_retries=None)
def import_repo(repo_id, parent=None):
    repo = Repository.query.get(repo_id)
    if not repo:
        logger.error('Repository %s not found', repo_id)
        return

    vcs = repo.get_vcs()
    if vcs is None:
        logger.warning('Repository %s has no VCS backend set', repo.id)
        return

    if repo.status == RepositoryStatus.inactive:
        logger.info('Repository %s is inactive', repo.id)
        return

    Repository.query.filter(
        Repository.id == repo.id, ).update({
            'last_update_attempt': datetime.utcnow(),
        })
    db.session.commit()

    if vcs.exists():
        vcs.update()
    else:
        vcs.clone()

    for commit in vcs.log(parent=parent):
        revision, created = commit.save(repo)
        db.session.commit()
        parent = commit.id

    Repository.query.filter(
        Repository.id == repo.id, ).update({
            'last_update': datetime.utcnow(),
        })
    db.session.commit()

    if parent:
        import_repo.delay(
            repo_id=repo.id.hex,
            parent=parent, )
