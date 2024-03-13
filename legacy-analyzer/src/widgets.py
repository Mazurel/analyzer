from io import StringIO
import gc
from typing import Callable, Awaitable
from asyncio import Lock

from src.logs.types import LogFile, LogLine

from nicegui import ui, events, run
from nicegui.element import Element


parsing_file_lock = Lock()


class LogFileUpload(ui.upload):
    def _set_status_progress(self, text: str):
        self._status_element.clear()
        with self._status_element:
            ui.spinner(size="lg")
            ui.label(text)

    def _set_status_done(self, text: str):
        self._status_element.clear()
        with self._status_element:
            ui.icon("done", size="lg")
            ui.label(text)

    def _set_status_fail(self, text: str):
        self._status_element.clear()
        with self._status_element:
            ui.icon("cancel", size="lg")
            ui.label(text)

    async def _parse_file(self, event: events.UploadEventArguments):
        global parsing_file_lock

        log_file = None
        self._set_status_progress("Waiting for file parsing lock ...")
        await parsing_file_lock.acquire()

        try:
            buffer = await run.io_bound(
                lambda: StringIO(event.content.read().decode("utf-8"))
            )
            self._set_status_progress("Parsing file ...")
            log_file = await run.cpu_bound(LogFile, buffer)
            self._set_status_done("File loaded and initialized !")
        except Exception as ex:
            self._set_status_fail(f"Uploading log file failed with: {str(ex)}")
        finally:
            gc.collect(0)  # Clear memory afterwards as well as possible
            parsing_file_lock.release()

        if log_file is not None:
            await self._on_upload(log_file)

    def __init__(self, label: str, on_upload: Callable[[LogFile], Awaitable[None]]):
        with ui.column():
            super().__init__(
                label=label,
                on_upload=self._parse_file,
                auto_upload=True,
                on_rejected=lambda _: self._set_status_fail("File rejected"),
                max_files=1,
            )

            self._status_element = ui.row()
            self._status_element.tailwind.align_items("center")

        self._on_upload = on_upload


def log_line(line: LogLine) -> Element:
    with ui.grid(columns=3) as el:
        el.tailwind.flex("auto").align_items("start").gap("2.5").align_content(
            "start"
        ).justify_items("start").font_family("mono").user_select("none").text_overflow(
            "text-clip"
        )
        el.style("grid-template-columns: 60px 200px 1fr;")
        ui.label(f"{line.line_number}")
        ui.label(f"{str(line.timestamp) if line.has_timestamp else ''}")
        ui.label(f"{line.line_without_timestamp}")

    return el


def settings_frame() -> Element:
    el = ui.element("div")
    el.tailwind.border_color("indigo-300")
    el.tailwind.border_width("2")
    el.tailwind.padding("p-4")
    el.tailwind.border_radius("lg")
    return el
