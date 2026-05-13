def breaker_code(value: int) -> str:
    match value:
        case 0:
            return "Over-Current"
        case 1:
            return "Over-Voltage"
        case 2:
            return "Over-Power"
        case 3:
            return "Low-Sensitivity Current"
        case 4:
            return "Low-Sensitivity Voltage"
        case 5:
            return "Low-Sensitivity Power"
        case 6:
            return "Short-Circuit"
        case 7:
            return "Overload"
        case 8:
            return "Leakage-Current"
        case 9:
            return "Self-Test"
        case 10:
            return "High-Temperature"
        case 11:
            return "Unbalance"
        case 12:
            return "Miss-Phase"
        case _:
            return "unknown"

