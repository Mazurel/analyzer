from src.logs.types import MaskingInstruction

CONFIGS_ENDPOINT = "configs/"
CONFIGS_LOCAL_PATH = "configs/"

COMMON_MASKING_INSTRUCTIONS: list[MaskingInstruction] = [
    MaskingInstruction("IPv4", "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}"),
    MaskingInstruction("24h-time", "[0-9]{1,2}:[0-9]{1,2}"),
    MaskingInstruction("Unix Path", r"(/[a-zA-Z\-]+)+/?"),
]
