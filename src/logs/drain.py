from src.logs.types import LogFile, Template

from drain3.template_miner_config import TemplateMinerConfig, MaskingInstruction
from drain3 import TemplateMiner
from marshmallow import Schema, ValidationError, fields


class MaskingInstructions(fields.Field):
    def _serialize(
        self, value: list[MaskingInstruction], *_, **__
    ) -> list[dict[str, str]]:
        try:
            return [
                {"name": instruction.mask_with, "pattern": instruction.pattern}
                for instruction in value
            ]
        except Exception as ex:
            raise ValidationError(str(ex))

    def _deserialize(
        self, value: list[dict[str, str]], *_, **__
    ) -> list[MaskingInstruction]:
        return [
            MaskingInstruction(instruction["pattern"], instruction["name"])
            for instruction in value
        ]


class DrainSettingsSchema(Schema):
    drain_depth = fields.Int(default=10)
    drain_sim_th = fields.Float(default=0.4)
    masking_instructions = MaskingInstructions(default=[])

    def update_settings(self, data: dict, config: TemplateMinerConfig):
        data = self.load(data)
        config.drain_depth = data["drain_depth"]
        config.drain_sim_th = data["drain_sim_th"]
        config.masking_instructions = data["masking_instructions"]
        return config


class DrainManager:
    def __init__(self) -> None:
        self.config = TemplateMinerConfig()
        self.config.drain_depth = 15
        self.config.drain_sim_th = .2
        self.miner = TemplateMiner(None, self.config)
    
    def learn(self, file: LogFile):
        for line in file.lines:
            self.miner.add_log_message(line.line)
    
    def build_templates(self):
        self.templates = {
            cluster.cluster_id: Template(
                cluster.cluster_id,
                cluster.get_template()
            )
            for cluster in self.miner.drain.clusters
        }
 
    def annotate(self, file: LogFile):
        self.build_templates()
        for line in file.lines:
            result = self.miner.match(line.line)
            line.template = self.templates[result.cluster_id]
