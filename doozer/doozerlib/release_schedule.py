from datetime import datetime
import os

import yaml

from doozerlib import gitdata


class ReleaseSchedule:
    """
    This class is a Singleton. Only at first object construction, it will clone ocp-release-schedule repo inside Doozer
    working directory, parse and store yaml data related to the current OCP version
    """

    _instance = None

    def __new__(cls, runtime):
        if cls._instance is None:
            cls._instance = super(ReleaseSchedule, cls).__new__(cls)
            cls.initialize(runtime)
        return cls._instance

    @classmethod
    def initialize(cls, runtime):
        if 'GITLAB_TOKEN' not in os.environ:
            raise RuntimeError('A GITLAB_TOKEN env var must be defined')

        # Clone ocp-release-schedule in doozer working dir
        git_data = gitdata.GitData(
            data_path=f'https://oauth2:{os.environ["GITLAB_TOKEN"]}@gitlab.cee.redhat.com/ocp-release-schedule/schedule.git',
            clone_dir=runtime.working_dir
        )

        # Parse and store relevant yaml
        major = runtime.group_config.vars['MAJOR']
        minor = runtime.group_config.vars['MINOR']
        config_file = f'{git_data.data_dir}/schedules/{major}.{minor}.yaml'
        with open(config_file) as f:
            cls._instance.schedule_data = yaml.safe_load(f.read())

    def get_ff_date(self) -> datetime:
        event = next(item for item in self.schedule_data['events'] if item["name"] == "feature-freeze")
        return datetime.strptime(event['date'], '%Y-%m-%dT%H:00:00-00:00')
