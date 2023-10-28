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

LABEL_TEXT_1 = "Brain depth ({}): "
LABEL_TEXT_2 = "Brain Simmilarity threshold ({}): "

logger = logging.getLogger("drain_setup")

@dataclass
class BrainSetup(View):
    """
    This view is responsible for configuring Brain.
    It supports saving/loading brain configs and tweaking individual options.
    """
    select_files: SelectFiles

    brain_depth: int = 10
    brain_sim_th: float = 0.4

    def show(self):
        with settings_frame() as outer:
            with ui.grid(columns=2):
                self.brain_depth_label = ui.label(LABEL_TEXT_1.format(self.brain_depth))
                self.brain_depth_slider = ui.slider(
                    min=2,
                    max=30,
                    step=1,
                    value=self.brain_depth,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "brain_depth")
                self.brain_depth_slider.tailwind.width("40")

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


        return outer

    def update(self, sender: object = None):
        self.brain_depth_label.text = LABEL_TEXT_1.format(self.brain_depth)
        self.brain_depth_slider.value = self.brain_depth
        self.brain_similarity_label.text = LABEL_TEXT_2.format(self.brain_sim_th)
        self.brain_similarity_slider.value = self.brain_sim_th

    def build_brain_config(self) -> BrainConfig:
        config = BrainConfig()
        config.brain_sim_th = self.brain_sim_th
        config.brain_depth = self.brain_depth
        return config

    def build_brain(self) -> BrainManager:
        return BrainManager(self.build_brain_config())

    def save_config(self):
        schema = BrainSettingsSchema()
        dump: dict = schema.dump(self.build_brain_config())
        config_path = join(CONFIGS_LOCAL_PATH, f"{uuid4()}.toml")
        with open(config_path, "w") as f:
            toml.dump(dump, f)

        ui.download(config_path)

    def load_config(self, config: str):
        schema = BrainSettingsSchema()
        obj = toml.loads(config)
        parsed_config: dict[str, Any] = schema.load(obj)
        self.brain_depth = parsed_config.get("brain_depth")
        self.brain_sim_th = parsed_config.get("brain_sim_th")

        self.state_changed.send(self)
