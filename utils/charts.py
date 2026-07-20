"""
Chart helpers. Limited to charts that map to real data the tools return
— no fabricated categories. Skill coverage has a real numerator/
denominator; ATS breakdown has real counts; the ATS gauge reflects the
actual ats_score the LLM produced.
"""
import plotly.graph_objects as go

PRIMARY = "#14B8A6"
SECONDARY = "#0EA5E9"
WARNING = "#F59E0B"
DANGER = "#EF4444"
BORDER = "#26314A"
TEXT = "#EDF1FA"
TEXT_MUTED = "#8D96B8"


def _base_layout(fig, height=280):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED, family="Inter, sans-serif"),
        height=height,
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    return fig


def skill_coverage_donut(current_count: int, missing_count: int):
    total = current_count + missing_count
    if total == 0:
        current_count, missing_count = 1, 0
    fig = go.Figure(data=[go.Pie(
        labels=["Have", "Missing"],
        values=[current_count, missing_count],
        hole=0.7,
        marker=dict(colors=[PRIMARY, BORDER]),
        textinfo="none",
        sort=False,
    )])
    coverage_pct = round((current_count / total) * 100) if total else 0
    fig.add_annotation(
        text=f"<b>{coverage_pct}%</b><br><span style='font-size:11px;color:{TEXT_MUTED}'>coverage</span>",
        showarrow=False, font=dict(size=20, color=TEXT),
    )
    return _base_layout(fig, height=230)


def ats_breakdown_bar(missing_keywords_count: int, formatting_flags_count: int):
    fig = go.Figure(data=[go.Bar(
        x=[missing_keywords_count, formatting_flags_count],
        y=["Missing keywords", "Formatting flags"],
        orientation="h",
        marker=dict(color=[SECONDARY, WARNING]),
        text=[missing_keywords_count, formatting_flags_count],
        textposition="outside",
    )])
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False)
    return _base_layout(fig, height=190)


def score_gauge(score: int, label: str):
    """Circular gauge for a 0-100 score, used on the ATS Optimization page."""
    color = PRIMARY if score >= 75 else (WARNING if score >= 50 else DANGER)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"size": 30, "color": TEXT}},
        title={"text": label, "font": {"size": 13, "color": TEXT_MUTED}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": BORDER, "tickfont": {"color": TEXT_MUTED, "size": 10}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [{"range": [0, 100], "color": BORDER}],
        },
    ))
    return _base_layout(fig, height=220)