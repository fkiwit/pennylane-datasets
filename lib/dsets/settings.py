from functools import cached_property
from pathlib import Path
from typing import ClassVar

import boto3
from dulwich.repo import Repo
from pydantic_settings import BaseSettings

from .lib.s3 import S3Client, S3Path


class Settings(BaseSettings):
    """Global settings for pennylane-datasets."""

    datasets_admin_api_url: str | None = None

    bucket_public_domain: str = "datasets.cloud.pennylane.ai"
    bucket_name: str = "swc-prod-pennylane-datasets"

    bucket_prefix_build: ClassVar[S3Path] = S3Path("build")
    bucket_prefix_data: ClassVar[S3Path] = S3Path("data")
    bucket_prefix_assets: ClassVar[S3Path] = S3Path("assets")

    datasets_build_s3_metadata_key: ClassVar[str] = "x-amz-meta-context"

    audience_url: str = "https://cloud.pennylane.ai"
    auth_url: str = "https://auth.cloud.pennylane.ai/oauth"
    graphql_url: str = "https://cloud.pennylane.ai/graphql"
    client_id: str = "MkuZM5qKutufNBkHorThEKv6s9W5p7Fq"

    @property
    def url_prefix_assets(self) -> str:
        return f"https://{self.bucket_public_domain}/{self.bucket_prefix_assets}"


class CLIContext:
    """Context object for CLI commands."""

    settings: Settings

    @property
    def auth_path(self):
        return self.repo_root / ".auth.json"

    @property
    def repo_root(self) -> Path:
        """Path to repository root, relative to the
        current working directory."""
        return Path(self.repo.path).relative_to(Path.cwd())

    @property
    def data_dir(self) -> Path:
        """Path to data directory, relative to the
        current working directory."""
        return self.repo_root / "data"

    @property
    def content_dir(self) -> Path:
        """Path to the content dir, relative to the current
        working directory."""
        return self.repo_root / "content"

    @property
    def build_dir(self) -> Path:
        return self.repo_root / "_build"

    @cached_property
    def repo(self) -> Repo:
        """dulwich ``Repo`` object for the pennylane-datasets
        repo."""
        return Repo.discover()

    @cached_property
    def aws_client(self) -> boto3.Session:
        """AWS client."""
        return boto3.Session()

    @cached_property
    def s3_client(self) -> S3Client:
        """S3 Client."""
        return self.aws_client.client("s3")

    def commit_sha(self, short: bool = False) -> str:
        """Return git SHA for currently checked out
        commit.

        Args:
            short: If True, only return the first 7
                characters.

        Returns:
            Commit sha, in hex format
        """
        sha = self.repo.head().hex()
        if short:
            return sha[:7]

        return sha

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
