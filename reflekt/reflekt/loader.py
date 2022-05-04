# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from pathlib import Path

import yaml
from loguru import logger

from reflekt.logger import logger_config
from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.plan import ReflektPlan
from reflekt.reflekt.project import ReflektProject

# Setup logger
logger.configure(**logger_config)


# The class ReflektLoader is a derivative work based on the class
# PlanLoader from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektLoader(object):
    def __init__(self, plan_dir, plan_name, raise_validation_errors=True):
        self._validation_errors = []
        if ReflektProject().exists:
            try:
                self.plan_name = plan_name
                self._load_plan_file(plan_dir / "plan.yml")
                self._load_events(plan_dir / "events")
                self._load_identify_traits(plan_dir / "identify_traits.yml")
                self._load_group_traits(plan_dir / "group_traits.yml")
                self._plan.validate_plan()
            except ReflektValidationError as error:
                if raise_validation_errors:
                    raise error
                else:
                    self._validation_errors.append(error)

    @property
    def plan(self):
        return self._plan

    @property
    def has_validation_errors(self):
        return len(self._validation_errors) > 0

    @property
    def validation_errors(self):
        return self._validation_errors

    def _load_plan_file(self, path):
        with open(path, "r") as plan_file:
            yaml_obj = yaml.safe_load(plan_file)
            self._plan = ReflektPlan(plan_yaml_obj=yaml_obj, plan_name=self.plan_name)

    def _load_events(self, path):
        for file in sorted(Path(path).glob("**/*.yml")):  # Get .yml files in /events
            logger.info(
                f"    Parsing event file {file.name}",
            )

            with open(file, "r") as event_file:
                yaml_event_obj = yaml.safe_load(event_file)
                for event_version in yaml_event_obj:
                    self.plan.add_event(event_version)

    def _load_identify_traits(self, path):
        if not path.exists():
            return

        with open(path, "r") as identify_file:
            yaml_obj = yaml.safe_load(identify_file)
            for trait in yaml_obj.get("traits", []):
                self.plan.add_identify_trait(trait)

    def _load_group_traits(self, path):
        if not path.exists():
            return

        with open(path, "r") as group_file:
            yaml_obj = yaml.safe_load(group_file)
            for trait in yaml_obj.get("traits", []):
                self.plan.add_group_trait(trait)
