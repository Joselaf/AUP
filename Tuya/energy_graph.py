"""
Energy graph: cumulative kWh line chart styled like Smart Life.
Press G from the dashboard to open, G/Q/Esc to close.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Vertical, ScrollableContainer
from rich.text import Text
from rich.style import Style
from rich.color import Color

CHART_HEIGHT = 10
Y_AXIS_WIDTH = 9

_LINE  = Style(color=Color.from_rgb(0, 210, 230), bold=True)
_FILL  = Style(color=Color.from_rgb(0, 90, 110))
_AXIS  = Style(dim=True)
_TITLE = Style(color="yellow", bold=True)
_TOTAL = Style(color="green", bold=True)


class EnergyGraph(Widget):
    """Cumulative kWh line chart for one breaker."""

    DEFAULT_CSS = """
    EnergyGraph {
        height: auto;
        width: 100%;
        border: tall $primary-darken-2;
        background: $surface;
        margin: 0 0 1 0;
        padding: 0 1;
    }
    """

    def __init__(self, device_name: str, history: list, **kwargs):
        super().__init__(**kwargs)
        self._device_name = device_name
        self._history = history

    def render(self) -> Text:
        out = Text()
        history = self._history
        chart_w = max(10, self.size.width - Y_AXIS_WIDTH - 4)

        # Title
        out.append(f" ⚡ {self._device_name}", style=_TITLE)

        if not history:
            out.append("\n  Collecting data…\n", style="dim italic")
            return out

        timestamps, values = zip(*history)
        values = list(values)
        total = values[-1]

        out.append("   Total: ", style=_AXIS)
        out.append(f"{total:.3f} kWh\n", style=_TOTAL)

        # Sample to fit chart width
        if len(values) > chart_w:
            step = len(values) / chart_w
            sampled_v = [values[int(i * step)] for i in range(chart_w)]
            sampled_t = [timestamps[int(i * step)] for i in range(chart_w)]
        else:
            pad = chart_w - len(values)
            sampled_v = [values[0]] * pad + values
            sampled_t = [timestamps[0]] * pad + list(timestamps)

        min_v = min(sampled_v)
        max_v = max(sampled_v)
        span = max_v - min_v or 1.0

        def to_row(v):
            return int((1.0 - (v - min_v) / span) * (CHART_HEIGHT - 1))

        rows = [to_row(v) for v in sampled_v]

        # Build grid
        line_grid = [[" "] * chart_w for _ in range(CHART_HEIGHT)]
        fill_grid = [[" "] * chart_w for _ in range(CHART_HEIGHT)]

        for col in range(chart_w):
            r = rows[col]
            # Line character
            if col == 0:
                line_grid[r][col] = "•"
            else:
                prev_r = rows[col - 1]
                if prev_r == r:
                    line_grid[r][col] = "─"
                elif prev_r > r:
                    line_grid[r][col] = "╭"
                else:
                    line_grid[r][col] = "╰"
                # Vertical connectors for steep changes
                if abs(prev_r - r) > 1:
                    for mid in range(min(prev_r, r) + 1, max(prev_r, r)):
                        line_grid[mid][col] = "│"
            # Fill below line
            for fr in range(r + 1, CHART_HEIGHT):
                fill_grid[fr][col] = "▒"

        # Y-axis labels
        mid_v = (min_v + max_v) / 2
        y_labels = []
        for row in range(CHART_HEIGHT):
            if row == 0:
                y_labels.append(f"{max_v:7.3f} ┤")
            elif row == CHART_HEIGHT // 2:
                y_labels.append(f"{mid_v:7.3f} ┤")
            elif row == CHART_HEIGHT - 1:
                y_labels.append(f"{min_v:7.3f} ┤")
            else:
                y_labels.append(f"{'':7} │")

        # Render chart
        for row in range(CHART_HEIGHT):
            out.append(y_labels[row], style=_AXIS)
            for col in range(chart_w):
                lc = line_grid[row][col]
                fc = fill_grid[row][col]
                if lc != " ":
                    out.append(lc, style=_LINE)
                elif fc != " ":
                    out.append(fc, style=_FILL)
                else:
                    out.append(" ")
            out.append("\n")

        # X-axis
        out.append(f"{'':8}└{'─' * chart_w}\n", style=_AXIS)

        # Time labels
        t0 = sampled_t[0].strftime("%H:%M")
        tm = sampled_t[len(sampled_t) // 2].strftime("%H:%M")
        t1 = sampled_t[-1].strftime("%H:%M")
        pad_size = max(1, (chart_w - len(t0) - len(tm) - len(t1)) // 2)
        out.append(f"{'':9}{t0}{' ' * pad_size}{tm}{' ' * pad_size}{t1}\n", style=_AXIS)

        # Footer
        out.append(f" {len(history)} packets accumulated", style="dim italic")
        return out


class GraphScreen(Screen):
    """Full-screen energy graph overlay."""

    BINDINGS = [
        ("q", "app.pop_screen", "Close"),
        ("escape", "app.pop_screen", "Close"),
        ("g", "app.pop_screen", "Close"),
    ]

    DEFAULT_CSS = """
    GraphScreen {
        background: $background;
        layout: vertical;
    }
    #graph-title {
        text-align: center;
        background: $primary-darken-3;
        color: $text;
        width: 100%;
        height: 1;
    }
    #graph-scroll {
        width: 100%;
        height: 1fr;
        padding: 1;
    }
    """

    def __init__(self, breaker_data: list[tuple[str, list]], **kwargs):
        super().__init__(**kwargs)
        self._breaker_data = breaker_data

    def compose(self) -> ComposeResult:
        yield Label(
            "⚡ Cumulative Energy (add_ele)  [dim]G / Q / Esc → back[/]",
            id="graph-title",
        )
        with ScrollableContainer(id="graph-scroll"):
            if not self._breaker_data:
                yield Label("  No energy data yet — waiting for add_ele packets.", style="dim")
                return
            for name, history in self._breaker_data:
                yield EnergyGraph(name, history, id=f"graph-{_safe_id(name)}")


def _safe_id(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name).strip("-")
