# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import shutil
from loguru import logger
from reflekt.logger import logger_config
import yaml
import funcy
from pathlib import Path
from inflection import dasherize, underscore
from reflekt.avo.parser import parse_avo_event, parse_avo_property
from reflekt.reflekt.dumper import ReflektYamlDumper

logger.configure(**logger_config)


# TODO - update all this to use avo JSON schema
class AvoPlan(object):
    def __init__(self, plan_json):
        self.plan_json = plan_json

    @classmethod
    def parse_string(cls, json_string):
        parsed_json = json.loads(json_string)
        return cls(parsed_json)

    @classmethod
    def parse_file(cls, json_file_path):
        with open(json_file_path, "r") as f:
            contents = f.read()
        return cls.parse_string(contents)

    @property
    def name(self):
        return self.plan_json.get("name")

    def build_reflekt(self, plan_dir):
        events_dir = plan_dir / "events"
        # If plan directory already exists, remove it.
        if plan_dir.is_dir():
            shutil.rmtree(plan_dir)
        # Re-make directories for reflekt tracking plan(s)
        for dir in [plan_dir, events_dir]:
            if not dir.exists():
                dir.mkdir()

        logger.info(f"Building reflekt plan at {plan_dir}")
        self._build_reflekt_plan_file(plan_dir)

        for event_json in self.plan_json.get("events", []):
            self._build_reflekt_event_file(events_dir, event_json)

    def _build_reflekt_plan_file(self, plan_dir):
        plan_file = plan_dir / "plan.yml"
        plan_obj = {"name": self.name}
        with open(plan_file, "w") as f:
            yaml.dump(plan_obj, f)

    def _build_reflekt_event_file(self, events_dir, event_json):
        event_name = event_json.get("name")
        event_file_name = dasherize(
            underscore(event_json["name"].replace(" ", "-").replace("/", ""))
        )
        event_file = events_dir / f"{event_file_name}.yml"
        logger.info(f"Building reflekt event `{event_name}` at {event_file}")
        event_obj = parse_avo_event(event_json)

        with open(event_file, "w") as f:
            yaml.dump(
                [event_obj],
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )
