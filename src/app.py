from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


@st.cache
def read_dataframes():
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


@st.cache
def histograms(away_df_before, away_df_after, home_df_before, home_df_after):
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


no_strength_dist, away_df_before, away_df_after, home_df_before, home_df_after = read_dataframes()
tenn_hist, lib_hist = histograms(
    away_df_before, away_df_after, home_df_before, home_df_after
)

# begin actual app display
st.title("autobracket analysis")

# link back to the main site for now
link = "[Back to tarpey.dev](https://tarpey.dev)"
st.markdown(link)

st.header("Simulation distribution before/after adding relative strength")
no_strength_dist

st.header("Tennessee simulation points, before and after (n=100)")
# display chart
tenn_hist

st.header("Liberty simulation points, before and after (n=100)")
# display chart
lib_hist
