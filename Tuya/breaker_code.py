def breaker_code(err):
    match err:
        case None:
            return "No error"
        case 1:
            return "OverCurrent"
        case 2:
            return "OverVoltage"
        case 3:
            return "UnderVoltage"
        case 4:
            return "Leakage"
        case 5:
            return "OverTemperature"
        case 6:
            return "ShortCircuit"
        