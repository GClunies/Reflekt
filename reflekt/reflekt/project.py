# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import yaml
from git import InvalidGitRepositoryError, Repo

from reflekt.reflekt.errors import ReflektProjectError


class ReflektProject:
    def __init__(self, raise_project_errors=True):
        self._project_errors = []
        self.project_dir = self._get_project_root(Path.cwd())
        self.project_yml = self.project_dir / "reflekt_project.yml"
        self.exists = True if self.project_yml.exists() else False

        if self.exists:
            with open(self.project_yml, "r") as f:
                self.project = yaml.safe_load(f)

            try:
                self.validate_project()
            except ReflektProjectError as err:
                if raise_project_errors:
                    raise err
                else:
                    self._project_errors.append(err)

    def _is_git_repo(self, path):
        """Checks if the directory is a git repo. Returns True if it is, else False"""
        try:
            _ = Repo(path).git_dir
            return True
        except InvalidGitRepositoryError:
            return False

    def _get_project_root(self, path):
        """Gets the working tree directory for reflekt project. reflekt project
        must be a in git repo.
        """
        if self._is_git_repo(path):
            repo = Repo(path, search_parent_directories=True)
            return Path(repo.working_tree_dir)
        else:
            raise ReflektProjectError(
                "\n"
                "\nGit repository not detected. Your reflekt project must be inside a Git repo to function correctly."  # noqa E501
                "\nCreate a git repo by either:"
                "\n     - Running `git init` at root of your reflekt project."
                "\n     - Cloning a repo containing an existing reflekt project from GitHub/Gitlab."  # noqa E501
            )

    def _get_project_name(self):
        try:
            self.name = self.project["name"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a project name in reflekt_project.yml. Like so:"
                "\n"
                "\nname: my_project  # letters, digits, underscores"
                "\n"
            )

    def _get_config_profile(self):
        try:
            self.config_profile = self.project["config_profile"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a config profile in reflekt_project.yml. Like so:"
                "\n"
                "\nconfig_profile: my_config_profile  # letters, digits, underscores"
                "\n"
            )

    def _get_config_path(self):
        config_path_check = self.project.get("config_path")

        if config_path_check is not None:
            self.config_path = Path(config_path_check)

            if not self.config_path.exists():
                raise ReflektProjectError(
                    f"\n\nOptional `config_path:` {str(self.config_path)} in reflekt_project.yml does not exist!"  # noqa E501
                )

            if not self.config_path.is_absolute():
                raise ReflektProjectError(
                    f"\n\n"
                    f"Optional `config_path:` {str(self.config_path)} in reflekt_project.yml must be an absolute path!"  # noqa E501
                )
        else:
            self.config_path = None

    def _get_events_case_or_pattern(self):
        self.events_case = (
            self.project.get("tracking_plans").get("naming").get("events").get("case")
        )
        self.events_pattern = (
            self.project.get("tracking_plans").get("naming").get("events").get("pattern")
        )

        if self.events_case is None and self.events_pattern is None:
            raise ReflektProjectError(
                "\n\nMust define a `case:` or `pattern:` rule for events naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
                "\nOR (never both)"
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      pattern: '[A-Z][a-z]'  # regex pattern"
                "\n"
            )

    def _get_events_allow_numbers(self):
        try:
            self.events_allow_numbers = self.project["tracking_plans"]["naming"][
                "events"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `allow_numbers:` rule for events naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      allow_numbers: true  # Or false"
                "\n"
            )

    def _get_events_reserved(self):
        try:
            self.events_reserved = self.project["tracking_plans"]["naming"]["events"][
                "reserved"
            ]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `reserved:` rule for events naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      reserved: ['My Reserved Event']  # List event names. Can be an empty list!"  # noqa E501
                "\n"
            )

    def _get_properties_case_or_pattern(self):
        self.properties_case = (
            self.project.get("tracking_plans")
            .get("naming")
            .get("properties")
            .get("case")
        )
        self.properties_pattern = (
            self.project.get("tracking_plans")
            .get("naming")
            .get("properties")
            .get("pattern")
        )

        if self.properties_case is None and self.properties_pattern is None:
            raise ReflektProjectError(
                "\n\nMust define a `case:` or `pattern:` rule for properties naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
                "\nOR (never both)"
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      pattern: '[A-Z][a-z]'  # regex pattern"
                "\n"
            )

    def _get_properties_allow_numbers(self):
        try:
            self.properties_allow_numbers = self.project["tracking_plans"]["naming"][
                "properties"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `allow_numbers:` rule for properties naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      allow_numbers: true  # Or false"
                "\n"
            )

    def _get_properties_reserved(self):
        try:
            self.properties_reserved = self.project["tracking_plans"]["naming"][
                "properties"
            ]["reserved"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `reserved:` rule for properties naming in reflekt_project.yml. Like so:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      reserved: ['my_reserved_property']  # List properties names. Can be an empty list!"  # noqa E501
                "\n"
            )

    def _get_data_types(self):
        try:
            self.data_types = self.project["tracking_plans"]["data_types"]["allowed"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define allowed data types for event properties in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  data_types:"
                "\n    allowed:"
                "\n      - list"
                "\n      - data"
                "\n      - types"
                "\n      - here"
                "\n"
                "\nAvailable data types are: ['string', 'integer', 'boolean', 'number', 'object', 'array', 'any']"  # noqa E501
            )

    def _get_dbt_schema_map(self):
        try:
            self.schema_map = self.project["dbt"]["schema_map"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define `schema_map:` in reflekt_project.yml. Each trackign plan in your reflekt project must"  # noqa E501
                " be mapped to a corresponding schema in data warehouse where it's raw event data is stored. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  schema_map:"
                "\n    my-plan-name: schema_with_raw_events"
                "\n"
            )

    def _get_dbt_src_prefix(self):
        try:
            self.src_prefix = self.project["dbt"]["sources"]["prefix"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define `prefix:` for templated dbt sources in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  sources:"
                "\n    prefix: src_"
            )

    def _get_dbt_stg_prefix(self):
        try:
            self.stg_prefix = self.project["dbt"]["staged_models"]["prefix"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define `prefix:` for templated dbt staged models in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  sources:"
                "\n    prefix: src_"
            )

    def _get_dbt_stg_incremental_logic(self):
        try:
            self.incremental_logic = self.project["dbt"]["staged_models"][
                "incremental_logic"
            ]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define incremental logic for staged dbt models in reflekt_project.yml. Example:"  # noqa E501
                "\n\n"
                "\ndbt:"
                "\n  incremental_logic: |"
                "\n    {%- if is_incremental() %}"
                "\n        where event_timestamp >= (select max(event_timestamp)::date from {{ this }})"  # noqa E501
                "\n    {%- endif %}"
            )

    def _get_metadata_schema(self):
        if self.project.get("tracking_plans").get("metadata") is not None:
            self.metadata_schema = (
                self.project.get("tracking_plans").get("metadata").get("schema")
            )
        else:
            self.metadata_schema = None

    def validate_project(self):
        self._get_project_name()
        self._get_config_profile()
        self._get_config_path()
        self._get_events_case_or_pattern()
        self._get_events_allow_numbers()
        self._get_events_reserved()
        self._get_properties_case_or_pattern()
        self._get_properties_allow_numbers()
        self._get_properties_reserved()
        self._get_data_types()
        self._get_dbt_schema_map()
        self._get_dbt_src_prefix()
        self._get_dbt_stg_prefix()
        self._get_dbt_stg_incremental_logic()
        self._get_metadata_schema()
