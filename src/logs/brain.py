from log_parsers.Brain import LogParser as BrainParser
# from drain3.template_miner_config import TemplateMinerConfig
from marshmallow import Schema, ValidationError, fields
from src.logs.types import LogFile, Template
from dataclasses import dataclass

from src.consts import LOG_WORKDIR


@dataclass
class BrainConfig():
    brain_sim_th: float
    brain_depth: float


class BrainManager():
    def __init__(self, config: BrainConfig) -> None:
        # TODO add condig class for Brain, add regex support and log format
        self.config = config

    def learn(self, log_name: str):
        self.log_parser = BrainParser(log_format="<Content>", indir=LOG_WORKDIR, outdir=LOG_WORKDIR, depth=self.config.brain_depth, st=self.config.brain_sim_th)
        self.log_parser.parse(log_name)

    def annotate(self, file: LogFile):
        self.log_parser.df_log
        # self.build_templates()
        for line in file.lines:
            result = self.miner.match(line.line_without_timestamp)
            line.template = self.templates[result.cluster_id]


class BrainSettingsSchema(Schema):
    brain_depth = fields.Int(default=10)
    brain_sim_th = fields.Float(default=0.4)

    def update_settings(self, data: dict, config: BrainConfig):
        data = self.load(data)
        config.brain_depth = data["brain_depth"]
        config.brain_sim_th = data["brain_sim_th"]
        return config
    