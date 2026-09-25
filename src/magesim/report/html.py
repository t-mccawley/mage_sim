"""Self-contained HTML report."""

import html
from datetime import datetime
from pathlib import Path
from typing import Final

import plotly.graph_objects as go

from magesim.experiment.stats import CandidateSummary, Percentiles
from magesim.model.meta import MetaConfig

# Reference categorical palette, fixed order.
SERIES_COLORS: Final = (
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#4a3aa7",
    "#e34948",
)
BAR_COLOR: Final = SERIES_COLORS[0]
OVERFLOW_COLOR: Final = "#a3a29c"
SURFACE: Final = "#fcfcfb"
TEXT_PRIMARY: Final = "#0b0b0b"
TEXT_SECONDARY: Final = "#52514e"
GRID: Final = "#e6e5e0"
FONT: Final = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"


def _layout(fig: go.Figure, title: str, height: int) -> None:
    fig.update_layout(
        title={"text": title, "x": 0, "font": {"size": 16, "color": TEXT_PRIMARY}},
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font={"family": FONT, "color": TEXT_SECONDARY, "size": 12},
        margin={"l": 60, "r": 30, "t": 50, "b": 50},
        hoverlabel={"bgcolor": "white", "font": {"color": TEXT_PRIMARY}},
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)


def _bar_chart(summaries: list[CandidateSummary], title: str, attr: str) -> go.Figure:
    """Horizontal median bars with 15th-85th percentile whiskers, best on top."""
    ranked = sorted(summaries, key=lambda s: _pct(s, attr).median)
    stats = [_pct(s, attr) for s in ranked]
    labels = [s.candidate.label for s in ranked]
    fig = go.Figure(
        go.Bar(
            x=[p.median for p in stats],
            y=labels,
            orientation="h",
            marker={"color": BAR_COLOR, "cornerradius": 4},
            error_x={
                "type": "data",
                "symmetric": False,
                "color": TEXT_SECONDARY,
                "thickness": 1.5,
                "array": [p.high - p.median for p in stats],
                "arrayminus": [p.median - p.low for p in stats],
            },
            text=[f"{p.median:.1f}" for p in stats],
            textposition="inside",
            insidetextanchor="end",
            textfont={"color": "white"},
            customdata=[
                [p.low, p.high, s.candidate.rotation.display_name]
                for p, s in zip(stats, ranked, strict=True)
            ],
            hovertemplate=(
                "%{y} · %{customdata[2]}<br>median %{x:.1f}<br>"
                "p15 %{customdata[0]:.1f} · p85 %{customdata[1]:.1f}<extra></extra>"
            ),
        )
    )
    _layout(fig, title, height=max(220, 44 * len(summaries) + 100))
    fig.update_layout(bargap=0.35)
    fig.update_xaxes(title="DpS", rangemode="tozero")
    return fig


def _pct(summary: CandidateSummary, attr: str) -> Percentiles:
    value: Percentiles = getattr(summary, attr)
    return value


def _series_chart(summaries: list[CandidateSummary]) -> go.Figure:
    """Median cumulative DpS over time; top 8 colored, the rest start hidden."""
    ranked = sorted(summaries, key=lambda s: s.total_dps.median, reverse=True)
    colored = {id(s): SERIES_COLORS[i] for i, s in enumerate(ranked[: len(SERIES_COLORS)])}
    fig = go.Figure()
    for s in sorted(summaries, key=lambda s: s.candidate.number):
        color = colored.get(id(s), OVERFLOW_COLOR)
        fig.add_trace(
            go.Scatter(
                x=s.times,
                y=s.median_dps_series,
                mode="lines",
                name=f"{s.candidate.label} {s.candidate.rotation.display_name}",
                line={"color": color, "width": 2},
                visible=True if id(s) in colored else "legendonly",
                hovertemplate=(
                    f"{s.candidate.label}<br>%{{x:.1f}} s · %{{y:.1f}} DpS<extra></extra>"
                ),
            )
        )
    _layout(fig, "Median cumulative DpS over time", height=460)
    fig.update_layout(hovermode="x unified", legend={"orientation": "v"})
    fig.update_xaxes(title="Time (s)")
    fig.update_yaxes(title="DpS", rangemode="tozero")
    return fig


def _legend_table(summaries: list[CandidateSummary]) -> str:
    rows = []
    for s in sorted(summaries, key=lambda s: s.total_dps.median, reverse=True):
        c = s.candidate
        notes = []
        if s.unimplemented_talents:
            notes.append("Unmodeled talents: " + ", ".join(s.unimplemented_talents))
        if s.blocked_seconds_per_iteration:
            top = ", ".join(
                f"{k} ({v:.0f} s/run)" for k, v in list(s.blocked_seconds_per_iteration.items())[:3]
            )
            notes.append("Blocked picks: " + top)
        share = ", ".join(f"{k} {v:.0%}" for k, v in list(s.damage_share.items())[:4])
        rows.append(
            "<tr>"
            f"<td class='num'>{c.label}</td>"
            f"<td class='num'>{s.total_dps.median:.1f}</td>"
            f"<td>{_esc(c.character.display_name)} (L{c.character.level})</td>"
            f"<td>{_esc(c.encounter.display_name)}</td>"
            f"<td><b>{_esc(c.rotation.display_name)}</b><br>"
            f"<span class='muted'>{_esc(c.rotation.description)}</span></td>"
            f"<td><a href='{_esc(c.talents.url)}'>{_esc(c.talents.display_name)}</a></td>"
            f"<td>{_esc(share)}<br><span class='muted'>kills {s.mean_kills:.1f}, "
            f"drinking {s.mean_drinking_time:.0f} s</span></td>"
            f"<td class='muted'>{_esc('; '.join(notes))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>#</th><th>Median DpS</th><th>Character</th><th>Encounter</th>"
        "<th>Rotation</th><th>Talents</th><th>Damage share</th><th>Notes</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


_CSS: Final = f"""
body {{ background:{SURFACE}; color:{TEXT_PRIMARY}; font-family:{FONT}; margin:0; }}
main {{ max-width:1200px; margin:0 auto; padding:24px 16px 48px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.muted {{ color:{TEXT_SECONDARY}; font-size:12px; }}
.card {{ border:1px solid {GRID}; border-radius:8px; padding:8px; margin:16px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:16px; }}
.scroll {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:13px; }}
th, td {{ text-align:left; padding:8px; border-bottom:1px solid {GRID}; vertical-align:top; }}
th {{ color:{TEXT_SECONDARY}; font-weight:600; }}
td.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
a {{ color:{BAR_COLOR}; }}
"""


def render_report(summaries: list[CandidateSummary], meta: MetaConfig) -> str:
    """Build the report HTML."""
    figs = [
        _bar_chart(summaries, "Total DpS (median, whiskers p15-p85)", "total_dps"),
        _bar_chart(summaries, "Peak DpS (median, whiskers p15-p85)", "peak_dps"),
        _series_chart(summaries),
    ]
    divs = [
        f.to_html(
            full_html=False,
            include_plotlyjs="cdn" if i == 0 else False,
            config={"displaylogo": False, "responsive": True},
        )
        for i, f in enumerate(figs)
    ]
    subtitle = " · ".join(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            f"{len(summaries)} candidates",
            f"{meta.iterations} iterations each",
            f"seed {meta.seed}",
            f"tick {meta.tick_seconds}s",
            f"peak DpS ignores the first {meta.peak_warmup_seconds:g}s",
        ]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MageSim Results</title><style>{_CSS}</style></head>
<body><main>
<h1>MageSim results</h1>
<div class="muted">{subtitle}</div>
<div class="grid"><div class="card">{divs[0]}</div><div class="card">{divs[1]}</div></div>
<div class="card">{divs[2]}</div>
<div class="card scroll">{_legend_table(summaries)}</div>
</main></body></html>"""


def write_report(summaries: list[CandidateSummary], meta: MetaConfig) -> Path:
    """Write the report to `meta.output_dir` and return its path."""
    meta.output_dir.mkdir(parents=True, exist_ok=True)
    path = meta.output_dir / f"magesim_{datetime.now():%Y%m%d_%H%M%S}.html"
    path.write_text(render_report(summaries, meta), encoding="utf-8")
    return path
