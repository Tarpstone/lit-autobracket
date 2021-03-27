from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import requests
import streamlit as st


# load default plotly theme for customizing
lit_plotly_layout = go.Layout(
    margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=0, #top margin
    )
)


FLAVOR_DICT = {
    "All": False,
    "Vanilla": "none",
    "Mild": "mild",
    "Medium": "medium",
    "MAX SPICE": "max",
}


@st.cache
def performance_by_bracket(flavor: str = "All"):
    # fetch results data from API
    r = requests.get(
        "https://api.tarpey.dev/autobracket/performance/bracket"
    )

    # convert JSON
    df = pd.DataFrame(r.json())

    # filter by requested flavor
    if FLAVOR_DICT[flavor]:
        df = df.loc[df.flavor == FLAVOR_DICT[flavor]].copy()

    # sample size
    n = len(df)

    if flavor == "All":
        n_flavor = f"All {n}"
    else:
        n_flavor = f"{n} {flavor}"

    # make a hist from the dist
    correct_hist = go.Figure(layout=lit_plotly_layout)
    correct_hist.add_trace(
        go.Histogram(
            x=df.games_correct,
            name="games_correct",
            xbins=dict(size=1),
        )
    )

    # layout
    subheader = f"{n_flavor} brackets (through 52 of 67 games)"

    # styling
    correct_hist.update_traces(
        marker_color="#606890",
        marker_line_color="#000e2f",
        marker_line_width=2,
    )
    return correct_hist, subheader


@st.cache
def performance_by_game(flavor: str = "All"):
    # fetch results data from API
    r = requests.get(
        "https://api.tarpey.dev/autobracket/performance/game"
    )

    # convert JSON
    df = pd.DataFrame(r.json())
    df = df[[flavor]].copy()
    df.sort_values(by=[flavor], ascending=True, inplace=True)

    # sample size
    n = len(df)

    if flavor == "All":
        n_flavor = f"All {n}"
    else:
        n_flavor = f"{n} {flavor}"

    # make a hist from the dist
    matchup_bars = go.Figure(layout=lit_plotly_layout)
    matchup_bars.add_trace(
        go.Bar(
            x=getattr(df, flavor),
            y=df.index,
            name="percent_correct",
            orientation='h',
        )
    )

    # layout
    matchup_bars.update_layout(
        height=900,
    )

    # styling
    matchup_bars.update_traces(
        marker_color="#606890",
        marker_line_color="#000e2f",
        marker_line_width=2,
    )

    # subheader
    subheader = f"{flavor} flavored brackets"

    return matchup_bars, subheader


@st.cache
def factor_dataframes():
    dist_files = [
        "TENNvLIBRTYnostrengthdist.json",
        "TENNvLIBRTYwithstrengthdist.json",
    ]
    json_paths = [Path("data", file) for file in dist_files]
    data = []
    for path in json_paths:
        with open(path) as f:
            data.append(json.load(f))
    no_strength_dist = pd.DataFrame(data, index=["before", "after"]).transpose()
    box_score_files = [
        "TENNvLIBRTYnostrength.json",
        "TENNvLIBRTYwithstrength.json",
    ]
    json_paths = [Path("data", file) for file in box_score_files]
    data = []
    for path in json_paths:
        with open(path) as f:
            data.append(json.load(f))
    # extract just the team box scores from the JSON
    team_box_scores_before = [data[0][x]["team_box_score"] for x in range(len(data[0]))]
    team_box_scores_after = [data[1][x]["team_box_score"] for x in range(len(data[1]))]
    # away before and after
    away_team_box_before = [
        team_box_scores_before[x]["TENN"] for x in range(len(team_box_scores_before))
    ]
    away_df_before = pd.DataFrame(away_team_box_before)
    away_team_box_after = [
        team_box_scores_after[x]["TENN"] for x in range(len(team_box_scores_after))
    ]
    away_df_after = pd.DataFrame(away_team_box_after)
    # home before and after
    home_team_box_before = [
        team_box_scores_before[x]["LIBRTY"] for x in range(len(team_box_scores_before))
    ]
    home_df_before = pd.DataFrame(home_team_box_before)
    home_team_box_after = [
        team_box_scores_after[x]["LIBRTY"] for x in range(len(team_box_scores_after))
    ]
    home_df_after = pd.DataFrame(home_team_box_after)
    return no_strength_dist, away_df_before, away_df_after, home_df_before, home_df_after


def factor_histograms(away_df_before, away_df_after, home_df_before, home_df_after):
    tenn_hist = go.Figure()
    tenn_hist.add_trace(
        go.Histogram(
            x=away_df_before.sim_points,
            name="no relative strength",
            xbins=dict(size=4),
            marker_color="#D17492",
        )
    )
    tenn_hist.add_trace(
        go.Histogram(
            x=away_df_after.sim_points,
            name="with relative strength",
            xbins=dict(size=4),
            marker_color="#017492",
        )
    )
    # chart formatting
    tenn_hist.update_layout(barmode='overlay')
    tenn_hist.update_traces(opacity=0.50)
    # chart TENN before and after
    lib_hist = go.Figure()
    lib_hist.add_trace(
        go.Histogram(
            x=home_df_before.sim_points,
            name="no relative strength",
            xbins=dict(size=4),
            marker_color="#D17492",
        )
    )
    lib_hist.add_trace(
        go.Histogram(
            x=home_df_after.sim_points,
            name="with relative strength",
            xbins=dict(size=4),
            marker_color="#017492",
        )
    )
    # chart formatting
    lib_hist.update_layout(barmode='overlay')
    lib_hist.update_traces(opacity=0.50)
    return tenn_hist, lib_hist


flavor_filter = st.sidebar.radio("Flavor", ["All", "Vanilla", "Mild", "Medium", "MAX SPICE"])

# all data work happens here
correct_hist, hist_subheader = performance_by_bracket(flavor=flavor_filter)
matchup_bars, bars_subheader = performance_by_game(flavor=flavor_filter)
no_strength_dist, away_df_before, away_df_after, home_df_before, home_df_after = factor_dataframes()
tenn_hist, lib_hist = factor_histograms(
    away_df_before, away_df_after, home_df_before, home_df_after
)

# begin actual app display
st.title("autobracket analysis")

# link back to the main site for now
link = "[Back to tarpey.dev](https://tarpey.dev)"
st.markdown(link)

st.header("Model performance by # of games correct")
st.subheader(hist_subheader)
col1, col2 = st.beta_columns([1,7])
with col1:
    st.write("column test =]")

with col2:
    st.plotly_chart(correct_hist, use_container_width=True)


st.header("Percentage of brackets with correct winner")
st.subheader(bars_subheader)
st.plotly_chart(matchup_bars, use_container_width=True)

st.header("Simulation distribution before/after adding relative strength")
no_strength_dist

st.header("Tennessee simulation points, before and after (n=100)")
# display chart
st.plotly_chart(tenn_hist, use_container_width=True)

st.header("Liberty simulation points, before and after (n=100)")
# display chart
st.plotly_chart(lib_hist, use_container_width=True)
