import logparser.Brain as BrainParser

class ParserManager():
    def __init__(self, parser_name: str, config: TemplateMinerConfig) -> None:
        if parser_name == "Brain":
            self.log_parser = BrainParser()
        else:
            # Should never happen
            assert(True)
        self.miner = TemplateMiner(None, config)

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