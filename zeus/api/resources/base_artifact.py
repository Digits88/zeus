from flask import Response
from uuid import UUID

from zeus.models import Artifact, Build, Job, Repository, RepositoryProvider

from .base import Resource


class BaseArtifactResource(Resource):
    def dispatch_request(
        self, provider: str, owner_name: str, repo_name: str, build_number: int, job_number: int, artifact_id: UUID, *args, **kwargs
    ) -> Response:
        queryset = Artifact.query \
            .join(Job, Job.id == Artifact.job_id) \
            .join(Build, Build.id == Job.build_id) \
            .join(Repository, Repository.id == Build.repository_id) \
            .filter(
                Repository.provider == RepositoryProvider(provider),
                Repository.owner_name == owner_name,
                Repository.name == repo_name,
                Build.number == build_number,
                Job.number == job_number,
                Artifact.id == artifact_id,
            )

        if self.select_resurce_for_update():
            queryset = queryset.with_for_update()
        artifact = queryset.first()
        if not artifact:
            return self.not_found()

        return Resource.dispatch_request(self, artifact, *args, **kwargs)
