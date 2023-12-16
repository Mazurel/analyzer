from log_parsers.Brain import LogParser as BrainParser
# from drain3.template_miner_config import TemplateMinerConfig
from marshmallow import Schema, ValidationError, fields
from src.logs.types import LogFile, Template
from dataclasses import dataclass

from src.consts import LOG_WORKDIR
from src.logs.parser import ParserManager


class BrainConfig():
    def __init__(self) -> None:
        self.dataset = ""
        self.brain_sim_th = 0
        self.regex_list = []
        self.log_format = ""
        self.delimeter = []


class BrainManager(ParserManager):
    def __init__(self, config: BrainConfig) -> None:
        # TODO add condig class for Brain, add regex support and log format
        self.config = config

    def learn(self, file: LogFile):
        self.log_parser = BrainParser(logname=self.config.dataset, log_format=self.config.log_format, indir=LOG_WORKDIR, outdir=LOG_WORKDIR, delimeter=self.config.delimeter, threshold=self.config.brain_sim_th, rex=self.config.regex_list)
        self.log_parser.parse(file.file_name)

    def annotate(self, file: LogFile):
        self.log_parser.df_log
        for idx, line in enumerate(file.lines):
            template = Template(int(self.log_parser.df_log["EventId"][idx][1:]), self.log_parser.df_log["EventTemplate"][idx])
            line.template = template


class BrainSettingsSchema(Schema):
    brain_sim_th = fields.Float(default=0.4)

    def update_settings(self, data: dict, config: BrainConfig):
        data = self.load(data)
        config.brain_sim_th = data["brain_sim_th"]
        return config
    