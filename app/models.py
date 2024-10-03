from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class DetectorType(str, Enum):
    SMA = "sma"
    EMA = "ema"


class GeneratorPhase(str, Enum):
    NORMAL = "normal"
    RAMP_UP = "ramp_up"
    HIGH = "high"
    RAMP_DOWN = "ramp_down"
