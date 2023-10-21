import logparser.Brain as BrainParser
from drain3.template_miner_config import TemplateMinerConfig
from marshmallow import Schema, ValidationError, fields

class ParserManager():
    def __init__(self, parser_name: str, config: TemplateMinerConfig) -> None:
        # TODO add condig class for Parser, add regex support and log format
        if parser_name == "Brain":
            self.log_parser = BrainParser(log_format, indir=input_dir, outdir=output_dir, depth=4, st=0.5)
        else:
            # Should never happen
            assert(True)

        self.log_parser.parse(log_file)

    def learn(self, file: LogFile):
        for line in file.lines:
            self.miner.add_log_message(line.line_without_timestamp)

    def build_templates(self):
        self.templates = {
            cluster.cluster_id: Template(cluster.cluster_id, cluster.get_template())
            for cluster in self.miner.drain.clusters
        }

    def annotate(self, file: LogFile):
        self.build_templates()
        for line in file.lines:
            result = self.miner.match(line.line_without_timestamp)
            line.template = self.templates[result.cluster_id]


class ParserSettingsSchema(Schema):
    parser_depth = fields.Int(default=10)
    parser_sim_th = fields.Float(default=0.4)

    def update_settings(self, data: dict, config: TemplateMinerConfig):
        data = self.load(data)
        config.drain_depth = data["parser_depth"]
        config.drain_sim_th = data["parser_sim_th"]
        return config