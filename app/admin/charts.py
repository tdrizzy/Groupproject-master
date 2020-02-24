import pandas as pd
from flask import session

from app import db
import logging
import json
import plotly


def stats_chart():
    year = bytes(session['academic_year'], 'utf8')

    layout = {'height': 350, 'width': 800, 'margin': {'l': 40, 'r': 10, 'b': 80, 't': 10, 'pad': 4},
              'legend': {'orientation': "h", 'x': 0.3, 'y': 1.0}}

    query  = b"SELECT i.id, p.id, i.user_id, i.created_date "
    query += b"FROM interest i JOIN project p ON i.project_id = p.id "
    query += b"WHERE p.academic_year = '" + year + b"'"
    query += b"ORDER BY i.created_date"

    df = pd.read_sql(query,
                     db.engine.raw_connection(),
                     index_col='created_date', parse_dates=True)
    df['count'] = range(1, df.index.size + 1)
    graph_data = dict(data=[
        {'x': df.index, 'y': df['count'] / 10, 'name': 'Notes of interest (tens)', 'mode': 'lines', 'type': 'scatter'}],
                      layout=layout)

    query  = b"SELECT t.id, p.id, t.created_by, t.created_date "
    query += b"FROM team t JOIN project p ON t.project_id = p.id "
    query += b"WHERE p.academic_year = '" + year + b"'"

    df = pd.read_sql(query,
                     db.engine.raw_connection(),
                     index_col='created_date', parse_dates=True)
    df['count'] = range(1, df.index.size + 1)
    graph_data['data'].append({'x': df.index, 'y': df['count'], 'name': 'Teams', 'mode': 'lines', 'type': 'scatter'})

    query  = b"SELECT id, created_date "
    query += b"FROM project "
    query += b"WHERE academic_year = '" + year + b"'"

    df = pd.read_sql(query,
                     db.engine.raw_connection(),
                     index_col='created_date', parse_dates=True)
    df['count'] = range(1, df.index.size + 1)
    graph_data['data'].append({'x': df.index, 'y': df['count'], 'name': 'Projects', 'mode': 'lines', 'type': 'scatter'})

    return graph_data


def projects_chart():
    year = session['academic_year']

    layout = {'height': 150, 'width': 260, 'margin': {'l': 20, 'r': 30, 'b': 50, 't': 10, 'pad': 4},
              'showlegend': False}

    query  = "SELECT s.name as Status, count(*) as status_count "
    query += "FROM   project p join status s on p.status_id = s.id "
    query += "WHERE  s.name = '{}' "
    query += "AND    p.academic_year = '" + year + "' "
    query += "GROUP BY s.name "

    df = pd.read_sql(bytes(query.format("New"), 'utf8'),
                     db.engine.raw_connection(),
                     index_col='Status')
    graph_data = dict(data=[{'x': df.index, 'y': df['status_count'], 'name': 'New', 'type': 'bar'}], layout=layout)

    df = pd.read_sql(bytes(query.format("Relisted"), 'utf8'),
                     db.engine.raw_connection(),
                     index_col='Status')
    graph_data['data'].append({'x': df.index, 'y': df['status_count'], 'name': 'Relisted', 'type': 'bar'})

    df = pd.read_sql(bytes(query.format("Live"), 'utf8'),
                     db.engine.raw_connection(),
                     index_col='Status')
    graph_data['data'].append({'x': df.index, 'y': df['status_count'], 'name': 'Live', 'type': 'bar'})

    df = pd.read_sql(bytes(query.format("Taken"), 'utf8'),
                     db.engine.raw_connection(),
                     index_col='Status')
    graph_data['data'].append({'x': df.index, 'y': df['status_count'], 'name': 'Taken', 'type': 'bar'})

    df = pd.read_sql(bytes(query.format("Complete"), 'utf8'),
                     db.engine.raw_connection(),
                     index_col='Status')
    graph_data['data'].append({'x': df.index, 'y': df['status_count'], 'name': 'Complete', 'type': 'bar'})

    return graph_data
