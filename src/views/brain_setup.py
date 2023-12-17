from dataclasses import dataclass, field
from io import StringIO
from typing import Any
from uuid import uuid4
import toml
from os.path import join
import logging

from nicegui import ui, events
from nicegui.element import Element

from drain3.template_miner_config import TemplateMinerConfig

from src.views import View
from src.widgets import settings_frame
from logs.brain import BrainManager, BrainSettingsSchema, BrainConfig
from src.consts import CONFIGS_LOCAL_PATH
from src.views.select_files import SelectFiles
from src.views.parser_setup import ParserSetup

LABEL_TEXT_1 = "Brain depth ({}): "
LABEL_TEXT_2 = "Brain Simmilarity threshold ({}): "

logger = logging.getLogger("drain_setup")

@dataclass
class RegexSelection(View):
    ready: bool = False
    regex: str = ""

    def show(self) -> Element:
        with ui.grid(1, 2) as el:
            el.tailwind.width("full")
            self.l2 = ui.input(
                label="regex",
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "regex")

        self.container = el
        return el

    def update(self, sender: object = None):
        self.l2.value = self.regex

        self.ready = len(self.regex) > 0

    def clear(self):
        try:
            self.container.clear()
            del self.container
        except AttributeError:
            # There is no `container` yet defined
            pass

@dataclass
class BrainSetup(ParserSetup):
    """
    This view is responsible for configuring Brain.
    It supports saving/loading brain configs and tweaking individual options.
    """
    select_files: SelectFiles

    dataset_name = ""
    space_chars = ""
    brain_sim_th: float = 0.4
    log_format: str = "<Content>"
    delimeters: str = ""
    regex_amount: int = 0
    regex_list: list[RegexSelection] = field(
        default_factory=lambda: []
    )

    def show(self):
        with settings_frame() as outer:
            continents = [
                'HealthApp :=|',
                'Android ():=',
                'HPC =-:',
                'BGL =()..',
                'Hadoop _:=()',
                'HDFS :',
                'Linux =:',
                'Spark :',
                'Thunderbird :=',
                'Windows :=[]',
                'Zookeeper :=',
                'Other'
            ]

            def on_select(sender):
                if sender.value == "Other":
                    self.space_chars_input.enable()
                    self.space_chars_input.set_visibility(True)
                else:
                    self.space_chars_input.value = ''
                    self.space_chars_input.disable()
                    self.space_chars_input.set_visibility(False)

                self.state_changed.send(self)

            self.dataset_select = ui.select(options=continents, with_input=True, label="Space character packet",
                    on_change=on_select).classes('w-40').bind_value_to(self, "dataset_name")
            
            self.space_chars_input = ui.input(
                label="Space after: ",
                value=self.space_chars,
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "space_chars")
            self.space_chars_input.disable()
            self.space_chars_input.set_visibility(False)
            
            with ui.grid(columns=2):
                self.brain_similarity_label = ui.label(LABEL_TEXT_2.format(self.brain_sim_th))
                self.brain_similarity_slider = ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self.brain_sim_th,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "brain_sim_th")
                self.brain_similarity_slider.tailwind.width("40")

                self.log_fomrat_input = ui.input(
                    label="log_format",
                    value=self.log_format,
                    on_change=lambda: self.state_changed.send(self),
                ).bind_value_to(self, "log_format")

            self.delimeter_input = ui.input(
                    label="delimeters",
                    value=self.delimeters,
                    on_change=lambda: self.state_changed.send(self),
                ).bind_value_to(self, "delimeters")
            
            self.regex_container = ui.element("div")
            self.regex_n = ui.number(
                "Regex",
                value=self.regex_amount,
                on_change=self.update,
            ).bind_value_to(self, "regex_amount")


            with ui.row() as el:
                el.tailwind.margin("mt-2")
                el.tailwind.margin("mb-4")

                with ui.dialog() as dialog:
                    def on_file(event: events.UploadEventArguments):
                        try:
                            buffer = StringIO(event.content.read().decode("utf-8"))
                            self.load_config(buffer.read())
                            dialog.close()
                        except Exception as ex:
                            ui.notify(f"Uploading config file failed with: {str(ex)}")
                            return

                    dialog.tailwind.padding("p-40")
                    ui.upload(
                        label="Upload file here",
                        on_upload=on_file,
                        auto_upload=True,
                        max_files=1,
                    )

                ui.button("Load", on_click=dialog.open)
                ui.button("Save", on_click=lambda: self.save_config())

        self.container = outer
        return outer

    def clear(self, parser_setup_div):
        try:
            with parser_setup_div:
                self.container.clear()
                self.container.delete()
                del self.container
        except AttributeError:
            # There is no `container` yet defined
            pass
    
    def update(self, sender: object = None):
        self.dataset_select.value = self.dataset_name
        self.space_chars_input.value = self.space_chars
        self.brain_similarity_label.text = LABEL_TEXT_2.format(self.brain_sim_th)
        self.brain_similarity_slider.value = self.brain_sim_th
        self.log_fomrat_input.value = self.log_format
        self.delimeter_input.value = self.delimeters
        self.regex_amount = max(0, self.regex_amount)
        self.regex_n.value = self.regex_amount

        # Update masking instructions view
        with self.regex_container:
            while self.regex_amount < len(self.regex_list):
                self.regex_list.pop().clear()

            while self.regex_amount > len(self.regex_list):
                regex = RegexSelection()
                regex.show()
                regex.state_changed.connect(
                    lambda _: self.state_changed.send(self), weak=False
                )
                self.regex_list.append(regex)

    def build_parser_config(self) -> BrainConfig:
        config = BrainConfig()
        config.dataset = self.dataset_name
        config.brain_sim_th = self.brain_sim_th
        config.log_format = self.log_format
        config.delimeter = list(self.delimeters)
        config.regex_list = [
            regex.regex
            for regex in self.regex_list
            if regex.ready
        ]
        config.space_chars = list(self.space_chars)

        return config

    def build_parser(self) -> BrainManager:
        return BrainManager(self.build_parser_config())

    def save_config(self):
        schema = BrainSettingsSchema()
        dump: dict = schema.dump(self.build_parser_config())
        config_path = join(CONFIGS_LOCAL_PATH, f"{uuid4()}.toml")
        with open(config_path, "w") as f:
            toml.dump(dump, f)

        ui.download(config_path)

    def load_config(self, config: str):
        schema = BrainSettingsSchema()
        obj = toml.loads(config)
        parsed_config: dict[str, Any] = schema.load(obj)
        self.brain_sim_th = parsed_config.get("brain_sim_th")

        self.state_changed.send(self)
