"""Self-contained HTML report."""

import html
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

import numpy as np
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
            insidetextanchor="start",
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


def _series_chart(summaries: list[CandidateSummary], warmup_seconds: float) -> go.Figure:
    """Median cumulative DpS over time; top 8 colored, the rest start hidden.

    The y-axis fits the data after the warmup, where near-zero time inflates DpS.
    """
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
    settled = [
        float(np.nanmax(s.median_dps_series[s.times >= warmup_seconds]))
        for s in summaries
        if np.any(~np.isnan(s.median_dps_series[s.times >= warmup_seconds]))
    ]
    y_range = [0.0, max(settled) * 1.1] if settled else None
    fig.update_yaxes(title="DpS", range=y_range)
    return fig


@dataclass(frozen=True, slots=True)
class _Column:
    """Legend table column; `numeric` sorts by value, `facet` gets a filter dropdown."""

    title: str
    numeric: bool = False
    facet: bool = False


_LEGEND_COLUMNS: Final = (
    _Column("#", numeric=True),
    _Column("Total DpS", numeric=True),
    _Column("Total p15-p85"),
    _Column("Peak DpS", numeric=True),
    _Column("Encounter", facet=True),
    _Column("Rotation", facet=True),
    _Column("Talents", facet=True),
    _Column("Character", facet=True),
    _Column("Kills", numeric=True),
    _Column("Drinking (s)", numeric=True),
    _Column("Blocked (s)", numeric=True),
    _Column("Damage share"),
    _Column("Notes"),
)


def _cell(text: str, sort: float | str | None = None, css: str = "") -> str:
    """A table cell; `sort` overrides the value used for sorting and filtering."""
    attrs = f" data-sort='{_esc(str(sort))}'" if sort is not None else ""
    attrs += f" class='{css}'" if css else ""
    return f"<td{attrs}>{text}</td>"


def _legend_row(s: CandidateSummary) -> str:
    c = s.candidate
    notes = []
    if s.unimplemented_talents:
        notes.append("Unmodeled talents: " + ", ".join(s.unimplemented_talents))
    if s.blocked_seconds_per_iteration:
        top = list(s.blocked_seconds_per_iteration.items())[:3]
        notes.append("Blocked: " + ", ".join(f"{k} ({v:.0f} s)" for k, v in top))
    share = ", ".join(f"{k} {v:.0%}" for k, v in list(s.damage_share.items())[:4])
    total, peak = s.total_dps, s.peak_dps
    blocked = sum(s.blocked_seconds_per_iteration.values())
    rotation = (
        f"<b>{_esc(c.rotation.display_name)}</b><br>"
        f"<span class='muted'>{_esc(c.rotation.description)}</span>"
    )
    talents = f"<a href='{_esc(c.talents.url)}'>{_esc(c.talents.display_name)}</a>"
    cells = (
        _cell(c.label, c.number, "num"),
        _cell(f"{total.median:.1f}", total.median, "num"),
        _cell(f"{total.low:.1f} - {total.high:.1f}", total.median, "num"),
        _cell(f"{peak.median:.1f}", peak.median, "num"),
        _cell(_esc(c.encounter.display_name), c.encounter.display_name),
        _cell(rotation, c.rotation.display_name),
        _cell(talents, c.talents.display_name),
        _cell(f"{_esc(c.character.display_name)} (L{c.character.level})", c.character.display_name),
        _cell(f"{s.mean_kills:.1f}", s.mean_kills, "num"),
        _cell(f"{s.mean_drinking_time:.0f}", s.mean_drinking_time, "num"),
        _cell(f"{blocked:.0f}", blocked, "num"),
        _cell(_esc(share)),
        _cell(_esc("; ".join(notes)), css="muted"),
    )
    return f"<tr>{''.join(cells)}</tr>"


def _legend_section(summaries: list[CandidateSummary]) -> str:
    """Titled, searchable, sortable candidate table (best total DpS first)."""
    headers = "".join(
        f"<th data-col='{i}' data-numeric='{int(col.numeric)}' data-facet='{int(col.facet)}' "
        f"aria-sort='none' tabindex='0'>{_esc(col.title)}</th>"
        for i, col in enumerate(_LEGEND_COLUMNS)
    )
    rows = "".join(
        _legend_row(s) for s in sorted(summaries, key=lambda s: s.total_dps.median, reverse=True)
    )
    return f"""
<h2>Candidate Legend</h2>
<div class="controls">
  <input id="legend-search" type="search" placeholder="Search candidates..."
         aria-label="Search candidates">
  <span id="legend-facets"></span>
  <span id="legend-count" class="muted"></span>
</div>
<div class="scroll"><table id="legend"><thead><tr>{headers}</tr></thead>
<tbody>{rows}</tbody></table></div>"""


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


# Sorting (click a header), text search, and per-column filter dropdowns.
_LEGEND_JS: Final = """
(() => {
  const table = document.getElementById("legend");
  const body = table.tBodies[0];
  const rows = [...body.rows];
  const headers = [...table.tHead.rows[0].cells];
  const search = document.getElementById("legend-search");
  const count = document.getElementById("legend-count");
  const facets = {};
  const key = (row, col) => {
    const cell = row.cells[col];
    return cell.dataset.sort ?? cell.textContent.trim();
  };
  headers.filter(h => h.dataset.facet === "1").forEach(h => {
    const col = +h.dataset.col;
    const select = document.createElement("select");
    select.setAttribute("aria-label", "Filter " + h.textContent);
    const values = [...new Set(rows.map(r => key(r, col)))].sort();
    select.add(new Option("All " + h.textContent.toLowerCase(), ""));
    values.forEach(v => select.add(new Option(v, v)));
    select.addEventListener("change", apply);
    facets[col] = select;
    document.getElementById("legend-facets").append(select);
  });
  function apply() {
    const terms = search.value.toLowerCase().split(/\\s+/).filter(Boolean);
    let shown = 0;
    rows.forEach(r => {
      const text = r.textContent.toLowerCase();
      const ok = terms.every(t => text.includes(t)) &&
        Object.entries(facets).every(([col, s]) => !s.value || key(r, +col) === s.value);
      r.hidden = !ok;
      shown += ok;
    });
    count.textContent = shown + " of " + rows.length + " candidates";
  }
  function sortBy(header) {
    const col = +header.dataset.col;
    const numeric = header.dataset.numeric === "1";
    const asc = header.getAttribute("aria-sort") !== "ascending";
    headers.forEach(h => h.setAttribute("aria-sort", "none"));
    header.setAttribute("aria-sort", asc ? "ascending" : "descending");
    const cmp = (a, b) => numeric
      ? parseFloat(key(a, col)) - parseFloat(key(b, col))
      : key(a, col).localeCompare(key(b, col), undefined, {numeric: true});
    rows.sort((a, b) => asc ? cmp(a, b) : cmp(b, a)).forEach(r => body.append(r));
  }
  headers.forEach(h => {
    h.addEventListener("click", () => sortBy(h));
    h.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); sortBy(h); }
    });
  });
  headers[1].setAttribute("aria-sort", "descending");
  search.addEventListener("input", apply);
  apply();
})();
"""


_CSS: Final = f"""
body {{ background:{SURFACE}; color:{TEXT_PRIMARY}; font-family:{FONT}; margin:0; }}
main {{ max-width:1200px; margin:0 auto; padding:24px 16px 48px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
h2 {{ font-size:16px; margin:4px 8px 12px; }}
.muted {{ color:{TEXT_SECONDARY}; font-size:12px; }}
.card {{ border:1px solid {GRID}; border-radius:8px; padding:8px; margin:16px 0; }}
.scroll {{ overflow-x:auto; }}
.controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:0 8px 12px; }}
.controls input, .controls select {{ font:inherit; font-size:13px; padding:6px 8px;
  border:1px solid {GRID}; border-radius:6px; background:white; color:{TEXT_PRIMARY}; }}
.controls input {{ min-width:220px; }}
#legend-facets {{ display:contents; }}
table {{ border-collapse:collapse; width:100%; font-size:13px; }}
th, td {{ text-align:left; padding:8px; border-bottom:1px solid {GRID}; vertical-align:top; }}
th {{ color:{TEXT_SECONDARY}; font-weight:600; cursor:pointer; user-select:none;
  white-space:nowrap; position:sticky; top:0; background:{SURFACE}; }}
th:hover {{ color:{TEXT_PRIMARY}; }}
th[aria-sort="ascending"]::after {{ content:" \\25B2"; }}
th[aria-sort="descending"]::after {{ content:" \\25BC"; }}
tbody tr:hover {{ background:#f3f2ee; }}
td.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
a {{ color:{BAR_COLOR}; white-space:nowrap; }}
"""


def render_report(summaries: list[CandidateSummary], meta: MetaConfig) -> str:
    """Build the report HTML."""
    figs = [
        _bar_chart(summaries, "Total DpS (median, whiskers p15-p85)", "total_dps"),
        _bar_chart(summaries, "Peak DpS (median, whiskers p15-p85)", "peak_dps"),
        _series_chart(summaries, meta.peak_warmup_seconds),
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
<div class="card">{divs[0]}</div>
<div class="card">{divs[1]}</div>
<div class="card">{divs[2]}</div>
<div class="card">{_legend_section(summaries)}</div>
</main><script>{_LEGEND_JS}</script></body></html>"""


def write_report(summaries: list[CandidateSummary], meta: MetaConfig) -> Path:
    """Write the report to `meta.output_dir` and return its path."""
    meta.output_dir.mkdir(parents=True, exist_ok=True)
    path = meta.output_dir / f"magesim_{datetime.now():%Y%m%d_%H%M%S}.html"
    path.write_text(render_report(summaries, meta), encoding="utf-8")
    return path
