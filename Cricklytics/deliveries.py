import pandas as pd
import plotly as py
import plotly.graph_objs as go
from plotly import tools

balls = pd.read_csv('deliveries.csv')
matches = pd.read_csv('matches.csv')

balls = balls.merge(matches, left_on='match_id', right_on='id')

COLORS = {
    'Sunrisers Hyderabad': '#ff822a',
    'Royal Challengers Bangalore': '#ec1c24',
    'Mumbai Indians': '#004ba0',
    'Rising Pune Supergiant': '#D11D9B',
    'Gujarat Lions': '#E04F16',
    'Kolkata Knight Riders': '#2e0854',
    'Kings XI Punjab': '#A7A9AC',
    'Delhi Daredevils': '#00008B',
    'Chennai Super Kings': '#ffff3c',
    'Rajasthan Royals': '#cba92b',
    'Deccan Chargers': '#D9E3EF',
    'Kochi Tuskers Kerala': '#632B72',
    'Pune Warriors': '#2F9BE3',
    'Rising Pune Supergiants': '#D11D9B'
}


def get_batsman_data(batsman):
    return balls[balls.batsman == batsman]


def get_bowler_data(bowler):
    bowler_data = balls[balls.bowler == bowler]
    bowler_data = bowler_data[
        ['season', 'batsman', 'bowler', 'bowling_team', 'player_dismissed', 'dismissal_kind', 'batsman_runs',
         'extra_runs', 'total_runs', 'ball']]

    bowling_data = bowler_data.groupby(['season', 'bowler', 'bowling_team']).agg({'batsman_runs': sum, 'ball': len})[
        ['batsman_runs', 'ball']].reset_index()

    return bowling_data


def get_batsman_runs(batsman):
    batsman_data = get_batsman_data(batsman)
    batsman_data = batsman_data[['season', 'batsman_runs', 'batsman', 'bowler', 'batting_team']]

    batsman_run_data = batsman_data.groupby(['season', 'batting_team'])[['batsman_runs']].sum().reset_index()

    return batsman_run_data


def plot_batsman_runs(batsman):
    batsman_run_data = get_batsman_runs(batsman)

    color_values = batsman_run_data.batting_team.map(COLORS)

    data = [go.Bar(
        x=batsman_run_data.season,
        y=batsman_run_data.batsman_runs,
        text=batsman_run_data.batting_team,
        marker=dict(
            color=color_values
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Runs scored by {} per season".format(batsman),
            font=dict(size=20)
        ),

        xaxis=dict(
            dtick=1,
            title='Season',
            showgrid=False,
            linewidth=2,
        ),
        yaxis=dict(
            title='Runs',
            showgrid=False,
        ),
        dragmode=False,
        autosize=True,
    )

    figure = go.Figure(data=data, layout=layout)
    return figure


def distribution_of_runs(batsman):
    batsman_data = get_batsman_data(batsman)

    # Ensure 'batsman_runs' exists in the DataFrame before processing
    if 'batsman_runs' not in batsman_data.columns:
        raise KeyError(f"'batsman_runs' column not found in batsman_data")

    # Get value counts and reset index properly
    batsman_distribution = batsman_data['batsman_runs'].value_counts().reset_index()
    batsman_distribution.columns = ['runs', 'count']  # Rename columns explicitly

    # Set the index to the 'runs' column
    batsman_distribution = batsman_distribution.set_index('runs')

    # Rename the index values for clarity
    batsman_distribution = batsman_distribution.rename(index={
        0: 'Dot',
        1: '1 Run',
        2: '2 Runs',
        3: '3 Runs',
        4: 'Fours',
        5: '5 Runs',
        6: 'Sixes'
    })

    # Plotly pie chart
    data = [go.Pie(
        labels=batsman_distribution.index,
        values=batsman_distribution['count'],  # Use correct column name
        marker=dict(
            line=dict(width=0.8)
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Distribution of runs scored by {}".format(batsman),
            font=dict(size=20),
        ),
        hovermode='closest',
        dragmode=False
    )

    figure = go.Figure(data, layout)
    return figure


def plot_bowler_runs(bowler):
    bowling_data = get_bowler_data(bowler)

    color_values = bowling_data.bowling_team.map(COLORS)

    data = [go.Bar(
        x=bowling_data.season,
        y=bowling_data.batsman_runs,
        text=bowling_data.bowling_team,
        marker=dict(
            color=color_values
        ),
    )]

    layout = go.Layout(
        title=dict(
            text="Runs conceded by {} per season".format(bowler),
            font=dict(size=20)
        ),
        xaxis=dict(
            dtick=1,
            title='Season',
            showgrid=False,
            linewidth=2,
        ),
        yaxis=dict(
            title='Runs',
            showgrid=False,
        ),
        dragmode=False,
        autosize=True,
    )

    figure = go.Figure(data=data, layout=layout)
    return figure


def plot_economy_rate(bowler):
    bowling_data = get_bowler_data(bowler)

    bowling_data['economy'] = bowling_data.batsman_runs / (bowling_data.ball / 6)

    color_values = bowling_data.bowling_team.map(COLORS)

    data = [go.Scatter(
        x=bowling_data.season,
        y=bowling_data.economy,
        text=bowling_data.bowling_team,
        marker=dict(
            color=color_values,
            size=15
        ),
        line=dict(
            dash='dot',
            width=1.5
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Economy rate of {} by Season".format(bowler),
            font=dict(size=20)
        ),
        xaxis=dict(
            dtick=1,
            title='Season',
            showgrid=False,
            linewidth=2
        ),
        yaxis=dict(
            title='Economy Rate',
            showgrid=False,
        ),
        dragmode=False
    )

    figure = go.Figure(data=data, layout=layout)
    return figure


def wicket_data(bowler):
    bowling_data = balls[balls.bowler == bowler]

    wickets = bowling_data.groupby(['dismissal_kind', 'season']).size().reset_index()
    wick = wickets.pivot(index='season', columns='dismissal_kind', values=0).fillna(0)

    data = []

    for i, r in wick.iteritems():
        t = go.Bar(
            x=wick.index,
            y=r,
            text=i.upper(),
            name=i.upper(),
            hoverinfo='y+text'
        )
        data.append(t)

    layout = go.Layout(
        title=dict(
            text='Distribution of wickets for {}'.format(bowler),
            font=dict(size=20)
        ),
        barmode='stack',
        hovermode='closest',
        xaxis=dict(
            dtick='1',
            title='Season',
            showgrid=False,
            linewidth=2
        ),
        yaxis=dict(
            title='Wickets',
            showgrid=False,
        ),
        dragmode=False
    )

    figure = go.Figure(data=data, layout=layout)
    return figure


def most_wickets_against(bowler):
    bowler_data = balls[balls.bowler == bowler]

    most_wick = bowler_data.groupby('batsman')['dismissal_kind'].count().reset_index().sort_values(by='dismissal_kind',
                                                                                                   ascending=False)

    data = [go.Table(
        header=dict(
            values=['Batsman', 'No. of wickets'],
            font=dict(
                size=15,
                color='white'
            ),
            fill=dict(color="#f44336")
        ),
        cells=dict(
            values=[most_wick['batsman'], most_wick['dismissal_kind']],
            height=25,
            fill = dict(color="#ffcdd2")
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Wickets by {}".format(bowler),
            font=dict(size=25)
        )
    )

    figure = go.Figure(data, layout)
    return figure


def fav_venues(player):
    venue = balls[balls.batsman == player]
    venue_count = venue.groupby('venue')[['batsman_runs']].sum().reset_index().sort_values('batsman_runs',
                                                                                           ascending=False)

    data = [go.Table(
        header=dict(
            values=['Venue', 'Runs by batsman'],
            font=dict(
                size=15,
                color='white'
            ),
            fill=dict(color="#f44336")
        ),
        cells=dict(
            values=[venue_count.venue, venue_count.batsman_runs],
            height=25,
            fill=dict(color="#ffcdd2")
        )
    )]

    layout = go.Layout(
        title=dict(
            text='Most runs scored by {} by venue'.format(player),
            font=dict(size=25)
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def fav_bowlers(batsman):
    batsman_data = balls[balls.batsman == batsman]
    batsman_fav_bowler = batsman_data.groupby('bowler').agg({'ball': len, 'batsman_runs': sum})[
        ['ball', 'batsman_runs']].reset_index()
    batsman_fav_bowler.sort_values('batsman_runs', ascending=False, inplace=True)
    batsman_fav_bowler = batsman_fav_bowler[batsman_fav_bowler.ball >= 6]

    data = [go.Table(
        header=dict(
            values=['Bowler', 'Runs'],
            font=dict(
                size=15,
                color='white'
            ),
            fill=dict(color="#f44336")
        ),
        cells=dict(
            values=[batsman_fav_bowler.bowler, batsman_fav_bowler.batsman_runs],
            height=25,
            fill=dict(color="#ffcdd2")
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Runs by {} against bowlers (min. 6 balls)".format(batsman),
            font=dict(size=25)
        )
    )

    figure = go.Figure(data, layout)
    return figure


def most_runs_against_team(batsman):
    batsman_data = balls[balls.batsman == batsman]

    runs_against_team = batsman_data.groupby('bowling_team')[['batsman_runs']].sum().reset_index().sort_values(
        'batsman_runs', ascending=False)

    color_values = runs_against_team.bowling_team.map(COLORS)

    data = [go.Bar(
        x=runs_against_team.bowling_team,
        y=runs_against_team.batsman_runs,
        marker=dict(
            color=color_values
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Runs scored against teams by {}".format(batsman),
            font=dict(size=20)
        ),
        hovermode='closest',
        xaxis=dict(
            title="Team",
            showgrid=False,
            linewidth=2
        ),
        yaxis=dict(
            title="Runs",
            showgrid=False,
        ),
        dragmode=False
    )

    figure = go.Figure(data, layout)
    return figure


def runs_by_over(batsman):
    batsman_data = get_batsman_data(batsman)

    runs_per_over = batsman_data.groupby('over')[['batsman_runs']].sum().reset_index()

    balls_faced = batsman_data.groupby('over').size().reset_index()

    runs_per_over.merge(balls_faced, left_on='over', right_on='over', )

    over_div = pd.DataFrame.from_dict({
        '0-6': runs_per_over[(runs_per_over['over'] >= 0) & (runs_per_over['over'] <= 6)].batsman_runs.sum(),
        '7-11': runs_per_over[(runs_per_over['over'] >= 7) & (runs_per_over['over'] <= 11)].batsman_runs.sum(),
        '12-15': runs_per_over[(runs_per_over['over'] >= 12) & (runs_per_over['over'] <= 15)].batsman_runs.sum(),
        '16-20': runs_per_over[(runs_per_over['over'] >= 16) & (runs_per_over['over'] <= 20)].batsman_runs.sum()
    }, orient='index')

    trace1 = go.Bar(
        x=over_div.index,
        y=over_div[0],
        name='Runs'
    )

    trace2 = go.Bar(
        x=runs_per_over.over,
        y=runs_per_over.batsman_runs,
        name='Runs'
    )

    layout = go.Layout(
        title=dict(
            text="Runs per over of {}".format(batsman),
            font=dict(size=20)
        ),
        hovermode='closest',
        showlegend=False,
        xaxis1=dict(
            title="Overs",
            dtick=1,
            showgrid=False,
            linewidth=2
        ),
        xaxis2=dict(
            title="Overs",
            dtick=1,
            showgrid=False,
            linewidth=2
        ),
        yaxis=dict(
            title="Runs",
            showgrid=False,
        ),
        yaxis2=dict(
            title="Runs",
            showgrid=False,
        )
    )

    fig = tools.make_subplots(rows=1, cols=2)

    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace1, 1, 2)

    fig['layout'].update(layout)

    return fig


def wickets_by_over(bowler):
    bowler_data = balls[balls.bowler == bowler]

    wicket_per_over = bowler_data.groupby(['over', 'dismissal_kind']).size().reset_index()
    wpo = wicket_per_over.pivot(index='over', columns='dismissal_kind', values=0).fillna(0)

    data = []

    for i, r in wpo.iteritems():
        t = go.Bar(
            x=wpo.index,
            y=r,
            text=i.upper(),
            name=i.upper(),
            hoverinfo='y+text'
        )
        data.append(t)

    layout = go.Layout(
        title=dict(
            text='Wickets per over for {}'.format(bowler),
            font=dict(size=20)
        ),
        barmode='stack',
        hovermode='closest',
        xaxis=dict(
            dtick='1',
            title='Over',
            showgrid=False,
            linewidth=2
        ),
        yaxis=dict(
            title='Wickets',
            showgrid=False,
        ),
        dragmode=False
    )

    figure = go.Figure(data=data, layout=layout)
    return figure


def outcome_by_toss(toss_cond, toss_decision):
    toss = matches[['season', 'team1', 'team2', 'toss_winner', 'toss_decision', 'winner']]
    win = (toss.winner == toss.toss_winner)
    loss = (toss.winner != toss.toss_winner)
    toss.loc[:, "win_on_toss"] = win if toss_cond == 'win' else loss

    piv_toss = toss.groupby(['toss_decision', 'win_on_toss', 'winner']).size().reset_index()

    trace1 = go.Bar(
        x=piv_toss.winner.unique(),
        y=piv_toss[(piv_toss.loc[:, 'toss_decision'] == toss_decision) & (piv_toss.loc[:, 'win_on_toss'] == True)][0],
        name="{} first & Win".format(toss_decision.capitalize()),
        marker=dict(
            color="#2E7D32"
        )
    )

    trace2 = go.Bar(
        x=piv_toss.winner.unique(),
        y=piv_toss[(piv_toss.loc[:, 'toss_decision'] == toss_decision) & (piv_toss.loc[:, 'win_on_toss'] == False)][0],
        name="{} first & Lost".format(toss_decision.capitalize()),
        marker=dict(
            color="#f44336"
        )
    )

    layout = go.Layout(
        title=dict(
            text="Count of outcomes when team: Toss = {}, Decision = {}".format(toss_cond.capitalize(),
                                                                                toss_decision.capitalize(),
                                                                                ),
            font=dict(size=20)
        ),

        yaxis=dict(
            title='Count',
            showgrid=False,
        ),

        yaxis2=dict(
            title='Count',
            showgrid=False,
        ),

        xaxis=dict(
            title='Team',
            showgrid=False,
            linewidth=2,
            tickfont=dict(size=12.5)
        ),

        xaxis2=dict(
            title='Team',
            showgrid=False,
            linewidth=2,
            tickfont=dict(size=12.5)
        ),
        hovermode='closest',
        dragmode=False,
        autosize=True
    )
    fig = tools.make_subplots(rows=1, cols=2, subplot_titles=('Match won', 'Match lost'))
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 2)

    fig['layout'].update(layout)

    return fig


def strike_rate_batsman_bowler(batsman, bowler):
    faceoff = balls[(balls.batsman == batsman) & (balls.bowler == bowler)]

    strike_rate = faceoff.groupby('season').agg({'batsman_runs': sum, 'ball': len})[
        ['ball', 'batsman_runs']].reset_index()
    strike_rate['str_rate'] = (strike_rate.batsman_runs / strike_rate.ball) * 100

    data = [go.Scatter(
        x=strike_rate.season,
        y=strike_rate.str_rate,
        mode='lines+markers',
        marker=dict(
            size=12,
            color='#673AB7'
        ),
        line=dict(
            dash='dot',
            width=1.2
        )
    )]

    layout = go.Layout(
        title=dict(
            text="Strike rate of {} against {} by season".format(batsman, bowler),
            font=dict(size=20)
        ),
        hovermode='closest',
        xaxis=dict(
            title='Season',
            dtick=1,
            showgrid=False,
            linewidth=2,
            zeroline=False
        ),
        yaxis=dict(
            title='Strike Rate',
            showgrid=False,
        ),
        dragmode=False,
        autosize=True
    )

    figure = go.Figure(data, layout)
    return figure


def wickets_batsman_bowler(batsman, bowler):
    faceoff = balls[(balls.batsman == batsman) & (balls.bowler == bowler)]

    try:
        how_out = faceoff.groupby(['season', 'dismissal_kind']).size().unstack().fillna(0)
    except ValueError:
        how_out = faceoff.groupby(['season', 'dismissal_kind']).fillna(0).reset_index()

    data = []
    for t in how_out.columns:
        trace = go.Bar(
            x=how_out.index,
            y=how_out[t],
            name=t.capitalize(),
            text=t.capitalize(),
        )

        data.append(trace)

    layout = go.Layout(
        title=dict(
            text="How {} takes wickets of {}".format(bowler, batsman),
            font=dict(size=20)
        ),
        xaxis=dict(
            dtick=1,
            showgrid=False,
            linewidth=2,
            title='Season'
        ),
        yaxis=dict(
            showgrid=False,
            linewidth=2,
            title='No. of wickets'
        ),
        dragmode=False,
        autosize=True,
        barmode='group',
        hovermode='closest'
    )

    fig = go.Figure(data, layout)

    return fig
