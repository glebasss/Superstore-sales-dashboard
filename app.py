import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import json


class MyCard:
    def __init__(self, card_id, text_id, title):
        self.card_id = card_id
        self.text_id = text_id
        self.title = title

    def create_card(self):
        return dbc.Card(
            dbc.CardBody([
                html.H4(self.title, className='card-title text-center',
                        style={'color': fontcolor1}),
                html.H4(id=self.text_id, className='card-text text-center mt-3',
                        style={'color': fontcolor1}),
                html.I(className="bi bi-info-circle-fill me-2"),
            ]),
            id=self.card_id,
            color=fontcolor2,
            className='border border-white border border-2 rounded-1',
            style={'margin-left': '-10px',
                   'margin-right': '-10px',
                   'height': '130px',
                   },
            inverse=True,
        )


def short_name(str_):
    str__ = str_.split()
    if len(str__) <= 1:
        return str_
    else:
        str__ = f'{str__[0]} {str__[1]}'
    return str(str__)


def create_modal(graph_id, title):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                dcc.Graph(
                    id=f'{graph_id}-modal',
                    style={'height': '80vh'},  # Большой график
                    config=config,
                )
            ),
        ],
        id=f'{graph_id}-modal-container',
        size="xl",  # Размер модального окна
        is_open=False  # По умолчанию закрыто
    )


app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH])
app.config.suppress_callback_exceptions = True

with open('state_codes.json', 'r') as f:
    state_codes = json.load(f)
fontcolor1 = '#f5cbcb'
fontcolor2 = '#00008B'
cardcolor = '#4069E1'
second_layercol = '#C0C0C0'
config = {
    'displayModeBar': True,  # Показывает панель инструментов (ModeBar)
    'responsive': True,  # Делает график адаптивным по размеру
    'scrollZoom': True,  # Включает возможность зуммирования скроллом
    'doubleClick': 'reset+autosize',  # Двойной клик для сброса масштаба и размера
    'displaylogo': False,  # Убирает логотип Plotly из панели инструментов
    # Добавление дополнительных кнопок панели инструментов
    'modeBarButtonsToAdd': ['toggleSpikelines', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetViews', 'toggleHover', 'resetGeo'],
    # Убирает ненужные кнопки, например, выбор областей
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',  # Формат изображения при сохранении
        'filename': 'custom_image',  # Имя файла при сохранении
        'height': 800,  # Высота изображения
        'width': 1200,  # Ширина изображения
        'scale': 2  # Масштаб изображения
    }
}

df = pd.read_csv("Sample - Superstore.csv", encoding='cp1252')
dfinfo = pd.read_csv('Info.csv')
df['short name'] = df['Product Name'].apply(short_name)
df_cat = df.groupby('Category')['Sales'].sum().reset_index()
df_data = df.copy()
df_data['Order Date'] = pd.to_datetime(df_data['Order Date'])
df_data = df_data[['Order Date', 'Sales', 'Profit', 'State']]
df_data[df_data['Order Date'].between('2014-01-03', '2014-01-05')]
df_data = df_data.groupby(['Order Date', 'State'])[
    ['Sales', 'Profit']].sum().reset_index()
df_data['date_num'] = (df_data['Order Date'] -
                       pd.to_datetime('2014-01-03')).dt.days
df_data = df_data.sort_values(by='Order Date')

card1 = MyCard('card1', 'text-card1', 'Total Sales').create_card()
card2 = MyCard('card2', 'text-card2', 'Total Profit').create_card()
card3 = MyCard('card3', 'text-card3', 'Average day profit').create_card()
card4 = MyCard('card4', 'text-card4', 'Average day Sales').create_card()
card5 = MyCard('card5', 'text-card5', 'Average Order Value').create_card()
card6 = MyCard('card6', 'text-card6', 'Top Customer').create_card()
card7 = MyCard('card7', 'text-card7', 'Repeat Customer Rate').create_card()
card8 = MyCard('card8', 'text-card8', 'Average Shipping Time').create_card()

marks = {}

# Добавление меток для каждого года
for year in range(df_data['Order Date'].dt.year.min(), df_data['Order Date'].dt.year.max() + 1):
    # Первый день года
    date_start = pd.to_datetime(f'{year}-01-01')
    date_num_start = (date_start - df_data['Order Date'].min()).days
    marks[date_num_start] = str(year)

    # Полугодие (второе полугодие)
    date_mid = pd.to_datetime(f'{year}-07-01')
    date_num_mid = (date_mid - df_data['Order Date'].min()).days
    marks[date_num_mid] = f'{year}-H2'

range_slider_data1 = dcc.RangeSlider(
    id='range-slider',
    min=df_data['date_num'].min(),
    max=df_data['date_num'].max(),
    step=1,
    value=[df_data['date_num'].min(), df_data['date_num'].max()],
    marks=marks,
    updatemode='mouseup',
    included=True,
    className="p-3",
    vertical=False
)

range_slider_data1.style = {
    'width': '90%',
    'margin': '20px auto',
    'padding': '10px',
    'border': '2px solid #007bff',
    'border-radius': '12px',
    'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
    'background-color': '#e9ecef',
    'font-size': '16px',
    'font-family': 'Arial, sans-serif',
    'color': '#333333',
    'outline': 'none',
    'height': '45px'
}


page_0 = dbc.Container(
    [
        dbc.Row([
            html.H1('Category sales',
                    className='text-center mt-4  ',
                    style={'color': fontcolor2},
                    ),
            html.Hr(style={
                'border': 'none',
                'border-top': '8px solid',
                'width': '100%',
                'margin-top': '20px',
                'margin-bottom': '20px'
            })
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        dcc.RadioItems(
                            ['Sales', 'Profit'], id='sales_or_profit',
                            value='Sales',
                            inline=True,
                            className='text-left mt-4 mb-4 mx-0',
                            style={'color': fontcolor2,
                                   'font-weight': 'bold', 'font-size': '18px'},
                            inputStyle={
                                "margin-right": "12px",
                                "margin-left": "20px",
                                "transform": "scale(1.5)",
                                "accent-color": fontcolor2}
                        ),
                        dcc.Checklist(
                            pd.Series([i for i in df['Segment']]
                                      ).unique().tolist(),
                            id='Segment-type',
                            value=['Consumer'],
                            inline=True,
                            className='text-left mt-4 mb-4 mx-0',
                            style={'color': fontcolor2,
                                   'font-weight': 'bold', 'font-size': '18px'},
                            inputStyle={
                                "margin-right": "12px",
                                "margin-left": "20px",
                                "transform": "scale(1.5)",
                                "accent-color": fontcolor2}
                        ),
                        dcc.Checklist(
                            pd.Series([i for i in df['Ship Mode']]
                                      ).unique().tolist(),
                            id='Ship-Mode-type',
                            value=['Standard Class'],
                            inline=True,
                            className='text-left mt-4 mb-4 mx-0',
                            style={'color': fontcolor2,
                                   'font-weight': 'bold', 'font-size': '18px'},
                            inputStyle={
                                "margin-right": "12px",
                                "margin-left": "20px",
                                "transform": "scale(1.5)",
                                "accent-color": fontcolor2}
                        ),
                        html.Div([
                            dbc.Button("Submit",
                                       id='button-page1',
                                       n_clicks=0,
                                       className="me-1 text-center",
                                       style={
                                           'color': fontcolor2,
                                           'background-color': fontcolor1,
                                       },
                                       ),
                        ],
                            className='d-grid gap-2 d-md-flex justify-content-md-end',
                        ),
                    ],)
                ),


            ],

                width=8),
            dbc.Col(dcc.RadioItems(
                ['In %', 'Average Profit'], id='coef_or_profit', value='In %',
                inline=True,
                className='text-left mt-4 mb-4 mx-0',
                style={'color': fontcolor2,
                       'font-weight': 'bold', 'font-size': '18px'},
                inputStyle={
                    "margin-right": "12px",
                    "margin-left": "20px",
                    "transform": "scale(1.5)",
                    "accent-color": fontcolor2},
            ),
            )
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='categories', style={'height': '65vh'}),
                    width={"size": 4}
                    ),
            dbc.Col(dcc.Graph(id='sub-categories',
                    style={'height': '65vh'}), width={"size": 4, }),
            dbc.Col([
                dcc.Graph(id='one-sales-profit', style={'height': '60vh'}),
            ], width=4),
        ]),
        dbc.Row([
            html.Hr(style={
                'border': 'none',
                'border-top': '8px solid',
                'width': '100%',
                'margin-top': '20px',
                'margin-bottom': '20px'
            })
        ]),
        dbc.Row([
            dbc.Col(card1),
            dbc.Col(card2),
            dbc.Col(card4),
            dbc.Col(card3),
        ]),
        dbc.Row([
            dbc.Col(card5),
            dbc.Col(card6),
            dbc.Col(card7),
            dbc.Col(card8),
        ]),
        dbc.Row([
            dbc.Col(range_slider_data1),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='slider-output', className='mt-4')),
        ]),

        create_modal('categories', 'Categories Graph'),
        create_modal('sub-categories', 'Sub-Categories Graph'),
        create_modal('one-sales-profit', 'Sales and Profit Graph'),

    ], fluid=True
)

range_slider_data2 = dcc.RangeSlider(
    id='range-slider2',
    min=df_data['date_num'].min(),
    max=df_data['date_num'].max(),
    step=1,
    value=[df_data['date_num'].min(), df_data['date_num'].max()],
    marks=marks,
    updatemode='mouseup',
    included=True,
    className="p-3",
    vertical=False
)

range_slider_data2.style = {
    'margin': '20px 0',
    'padding': '10px',
    'border': '1px solid #007bff',
    'border-radius': '8px',
    'box-shadow': '2px 2px 10px rgba(0, 123, 255, 0.2)',
    'background-color': '#f8f9fa',
}

df_states_w_city = df.drop(['Order Date', 'short name'], axis=1).groupby(
    ['State', 'City']).sum()[['Sales', 'Profit']].reset_index()
df_states_w_city['State code'] = df_states_w_city['State'].map(state_codes)
df_states_no_city = df_states_w_city.drop('City', axis=1).groupby(
    ['State', 'State code']).sum().reset_index()
df_states_no_city['Profit'] = df_states_no_city['Profit'].round().apply(
    lambda x: f'{x} $')
df_states_no_city['Sales'] = df_states_no_city['Sales'].round()

page_1 = dbc.Container([
    dbc.Row([
            html.H1('Sales map',
                    className='text-center mt-4 md-4',
                    style={'color': fontcolor2},
                    ),
            html.Hr(style={
                    'border': 'none',
                    'border-top': '8px solid',
                    'width': '100%',
                    'margin-top': '20px',
                    'margin-bottom': '20px'
                    })
            ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='map',
            style={'padding': '0px', 'margin': '0px', 'height': '70vh'},
            config={'scrollZoom': False,
                    },
            className='container-fluid')
        ),
        dbc.Row([
            dbc.Col(range_slider_data2,
                style={
                    'margin-top': '50px',
                    'margin-bottom': '50px',
                }
            )
        ])
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(figure={}, id='map_state',
                      style={'padding': '0px',
                             'margin': '0px', 'height': '45vh'},
                      className='container-fluid',),
            width=6
        ),
        dbc.Col(
            dcc.Graph(figure={}, id='sub-category-in-state',
                      className='container-fluid',
                      style={'padding': '0px', 'margin': '0px', 'height': '45vh'}),
            width=6
        ),
    ]),
    create_modal('map_state', 'Sales by City'),
    create_modal('sub-category-in-state', 'Sales by Sub-Category'),

], fluid=True, className="mt-1")

page_2 = dbc.Container([
    dbc.Row([
            dbc.Col([
                html.H1('Product popularity',
                        className='text-center mt-0 md-4',
                        style={'color': fontcolor2},
                        ),
                    html.Hr(style={
                        'border': 'none',
                        'border-top': '8px solid',
                        'width': '100%',
                        'margin-top': '20px',
                        'margin-bottom': '20px'
                    }),
                    ], width=12),
            ]),
    dbc.Row([
        dbc.Col([
            html.H3('Profit by sales',
                    className='text-center mt-4 mb-4',
                    style={'color': fontcolor2},
                    ),
            dcc.Dropdown(
                id='category-for-product',
                options=[{'label': label, 'value': label}
                         for label in df['Product Name'].unique()],
                value=['Staples', 'Staple remover'],
                multi=True,
                searchable=True,
                placeholder="Select products or categories...",
                clearable=True,
                style={
                    'font-family': 'Arial',
                    'font-weight': 'bold',
                    'font-size': '16px',
                    'color': fontcolor2,
                    'background-color': 'transparent',  # Прозрачный фон
                    'padding': '5px',
                    'width': '700px',
                    'margin-bottom': '10px'
                }
            ),


            dcc.Checklist(['discount', 'no discount'],
                          value=['discount'],
                          id='checkboxer-for-discount',
                          inline=True,
                          style={'color': fontcolor2,
                                 'font-weight': 'bold', 'font-size': '18px'},
                          inputStyle={
                "margin-right": "12px",
                "margin-left": "20px",
                "transform": "scale(1.5)",
                "accent-color": fontcolor2},
            ),
            html.Div([
                dbc.Button("Submit",
                           color="primary",
                           className="me-1",
                           id='submitiion-button-for-graphs-page2',
                           n_clicks=0,
                           style={
                               'color': fontcolor2,
                               'background-color': fontcolor1,
                           },
                           ),
            ],
                className='d-grid gap-2 d-md-flex justify-content-md-end mb-5',
            ),
            dcc.Graph(figure={}, id='profit-sale-product-compare',
                      style={'height': '40vh'}),
            dcc.Graph(figure={}, id='product-impact-linear',
                      style={'height': '40vh'}),

        ], width=6),
        dbc.Col([
            html.H3('Choose category',
                    className='text-center mt-4 mb-4',
                    style={'color': fontcolor2},
                    ),
            dcc.Dropdown(
                options=[{'label': category, 'value': category} for category in [
                    'Technology', 'Furniture', 'Office Supplies']],
                value=['Technology', 'Furniture', 'Office Supplies'],
                multi=True,
                id='category-for-products',
                searchable=True,
                placeholder="Select category...",
                clearable=True,
                style={
                    'font-family': 'Arial',
                    'font-weight': 'bold',
                    'font-size': '16px',
                    'color': fontcolor2,
                    'background-color': 'transparent',  # Прозрачный фон
                    'padding': '5px',
                    'width': '700px',
                    'margin-bottom': '10px',
                    'margin-top': '0px',
                }
            ),
            dcc.Slider(2, 15, 1, value=7, id='slider-of-products'),
            dcc.Graph(figure={}, id='products', style={
                      'height': '90vh'}),  # Полная высота колонки
        ], width=6)
    ], style={'height': '100vh'}),
], fluid=True, className="mt-4")

allert_press = dbc.Alert(
    [
        html.H3("Some advices!!", className="alert-heading",
                style={'color': fontcolor2, 'text-align': 'center', 'font-weight': 'bold'}),
        html.P(
            "You can interact with the charts by clicking on them.",
            style={'font-size': '18px',
                   'color': fontcolor2, 'text-align': 'center'}
        ),

    ],
    duration=6500,
    style={
        'width': '500px',
        'margin': '0 auto',
        'text-align': 'center',
        'position': 'fixed',
        'z-index': '1000',
        'left': '0',
        'right': '0',
        'background-color': fontcolor1,
        'border': fontcolor1,
        'text-align': 'center',
        'opacity': '0.85',
    }
)


app.layout = dbc.Container([
    allert_press,
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        brand="Superstore",
        # Увеличение размера текста и добавление жирности
        brand_style={'color': fontcolor1,
                     'font-size': '36px', 'font-weight': 'bold'},
        brand_href="/",
        color=fontcolor2,
        dark=True,
        expand='lg',  # Расширение на больших экранах
        style={'width': '100%'},  # Задание ширины навбара
        children=[
            dbc.NavItem(dcc.Link(children='Category Sales', href='/',
                        className='nav-link', style={'color': fontcolor1, 'font-size': '18px'})),
            dbc.NavItem(dcc.Link('Sales map', href='/page-1', className='nav-link',
                        style={'color': fontcolor1, 'font-size': '18px'})),
            dbc.NavItem(dcc.Link('Products', href='/page-2', className='nav-link',
                        style={'color': fontcolor1, 'font-size': '18px'})),
        ]
    ),
    html.Div(id='page-content')
], fluid=True)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return page_0
    elif pathname == '/page-1':
        return page_1
    elif pathname == '/page-2':
        return page_2


@callback(
    Output('sub-categories', 'figure'),
    Output('one-sales-profit', 'figure'),
    Output('categories', 'figure'),
    Input('button-page1', 'n_clicks'),
    Input('categories', 'clickData'),
    State('sales_or_profit', 'value'),
    State('range-slider', 'value'),
    State('coef_or_profit', 'value'),
    State('Segment-type', 'value'),
    State('Ship-Mode-type', 'value'),

)
def update_bar_char(_, clickData, val, date, coef_or_profit, segment_type, ship_mode_type):
    start_date = pd.to_datetime('2014-01-01') + \
        pd.to_timedelta(date[0], unit='D')
    end_date = pd.to_datetime('2014-01-01') + \
        pd.to_timedelta(date[1], unit='D')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df_subs_cat = df[df['Order Date'].between(start_date, end_date)].drop('Order Date', axis=1).\
        groupby(['Sub-Category', 'Category', 'Ship Mode', 'Segment']
                ).sum()[['Sales', 'Quantity', 'Profit']].reset_index()
    df_subs_cat = df_subs_cat[(df_subs_cat['Ship Mode'].isin(
        ship_mode_type)) & (df_subs_cat['Segment'].isin(segment_type))]
    if clickData == None:
        selected_category = 'Furniture'
    else:
        selected_category = clickData['points'][0]['label']
    filtered_df = df_subs_cat[df_subs_cat['Category'] == selected_category]

    category_orders = {
        'Sub-Category': filtered_df.groupby('Sub-Category')[val]
        .sum().reset_index().sort_values(by=val)['Sub-Category'].tolist(),
    }

    fig = px.bar(
        filtered_df,
        y='Sub-Category',
        color='Ship Mode',
        pattern_shape='Segment',
        x=val,
        title=f'{val.capitalize()} in {selected_category}',
        color_discrete_sequence=px.colors.sequential.Viridis,
        category_orders=category_orders,
    )

    fig.update_traces(
        texttemplate='%{x:.2s}',
        textposition='inside',
        insidetextanchor='middle',
        marker_line_color='#FFFFFF',
        marker_line_width=1.5,
        showlegend=False
    )

    fig.update_layout(
        title=dict(
            text=f'{val.capitalize()} in {selected_category}',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
        ),
        xaxis=dict(
            title=val.capitalize(),
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=True,
            gridcolor='#d9e3f1',
        ),
        yaxis=dict(
            title='Sub-Category',
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=False
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )

    filtered_df2 = filtered_df.copy()
    filtered_df2['In %'] = (filtered_df2['Profit'] /
                            filtered_df2['Sales'] + 1) * 100
    filtered_df2['Average Profit'] = filtered_df2['Profit'] / \
        filtered_df2['Quantity']
    if coef_or_profit == 'In %':
        suffix = "%"
    else:
        suffix = "$"
    if coef_or_profit == 'In %':
        texttempl2 = '%{y:.2f}%'
    else:
        texttempl2 = '%{y:.2f}$'

    filtered_df2 = filtered_df2.sort_values(
        by=[coef_or_profit, 'Segment', 'Ship Mode'])
    category_orders = {
        'Sub-Category': filtered_df2.groupby('Sub-Category')[coef_or_profit]
        .sum().reset_index().sort_values(by=coef_or_profit)['Sub-Category'].tolist(),
    }
    fig2 = px.bar(
        filtered_df2,
        x='Sub-Category',
        y=coef_or_profit,
        color='Ship Mode',
        pattern_shape='Segment',
        title='Profit by One Sale',
        color_discrete_sequence=px.colors.sequential.Viridis,
        category_orders=category_orders,
    )
    fig2.update_traces(
        texttemplate=texttempl2,
        textposition='inside',
        marker_line_color='#FFFFFF',
        insidetextanchor='middle',
        marker_line_width=1.5,
        showlegend=False
    )

    fig2.update_layout(
        title=dict(
            text='Profit by One Sale per Sub-Category',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
            pad=dict(b=100)
        ),
        xaxis=dict(
            title='Sub-Category',
            tickangle=-45,
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=False
        ),
        yaxis=dict(
            title=coef_or_profit.replace('_', ' ').capitalize(),
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            ticksuffix=suffix,
            showgrid=True,
            gridcolor='#d9e3f1',
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )

    fig3 = px.pie(
        data_frame=df_subs_cat,
        values=val,
        names='Category',
        title='Category Distribution',
        hole=.35,
        color_discrete_sequence=px.colors.sequential.Viridis,
    )

    fig3.update_traces(
        textinfo='percent+label',
        textposition='inside',
        textfont_size=14,
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == max(df_subs_cat[val])
              else 0 for i in df_subs_cat[val]]
    )

    # Настройка заголовка и легенды
    fig3.update_layout(
        title=dict(
            text='Category Distribution of Sales',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
        ),
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )
    return fig, fig2, fig3


@callback(
    Output('text-card1', 'children'),
    Output('text-card2', 'children'),
    Output('text-card3', 'children'),
    Output('text-card4', 'children'),
    Output('text-card5', 'children'),
    Output('text-card6', 'children'),
    Output('text-card7', 'children'),
    Output('text-card8', 'children'),
    Input('range-slider', 'value')
)
def cards(date):
    start_date = pd.to_datetime('2014-01-01') + \
        pd.to_timedelta(date[0], unit='D')
    end_date = pd.to_datetime('2014-01-01') + \
        pd.to_timedelta(date[1], unit='D')
    df_ = df.copy()
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_subs_cat = df_[df_['Order Date'].between(start_date, end_date)].drop('Order Date', axis=1).\
        groupby(['Sub-Category', 'Category']
                ).sum()[['Sales', 'Quantity', 'Profit']].reset_index()
    sales = df_subs_cat['Sales'].sum().round()
    profit = df_subs_cat['Profit'].sum().round()
    df_ = df.copy()
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_ = df_[df_['Order Date'].between(start_date, end_date)]
    aov = (df_['Sales'].sum() / df_['Order ID'].nunique()).round(2)
    top_customer = df_.groupby('Customer Name')['Sales'].sum().idxmax()
    top_customer_sales = df_.groupby('Customer Name')[
        'Sales'].sum().max().round()
    repeat_customers = df_[
        'Customer ID'].value_counts().loc[lambda x: x > 1].count()
    total_customers = df_['Customer ID'].nunique()
    repeat_customer_rate = (repeat_customers / total_customers) * 100
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_['Ship Date'] = pd.to_datetime(df_['Ship Date'])
    df_['Shipping Time'] = (df_['Ship Date'] - df_['Order Date']).dt.days
    average_shipping_time = df_['Shipping Time'].mean().round(2)
    df_ = df_.groupby('Order Date')[['Sales', 'Profit']].sum().reset_index()
    day_sales = df_['Sales'].mean().round()
    day_profit = df_['Profit'].mean().round()
    return f'{sales} $', f'{profit} $', f'{day_profit} $', f'{day_sales} $', \
        aov, f'{top_customer}-{top_customer_sales}$', f'{repeat_customer_rate:.2f}%', \
        f'{average_shipping_time} days'


@callback(
    Output('slider-output', 'children'),
    Input('range-slider', 'value'),
)
def range_slider(val):
    start_date = pd.to_datetime('2014-01-01') + \
        pd.to_timedelta(val[0], unit='D')
    end_date = pd.to_datetime('2014-01-01') + pd.to_timedelta(val[1], unit='D')
    return f'Selected range: {start_date.date()} to {end_date.date()}'


@callback(
    Output('map', 'figure'),
    Input('range-slider2', 'value'),
)
def mapp_graph(val_):
    df_ = df_data.drop('Order Date', axis=1).\
        groupby(['State', 'date_num']).sum().reset_index()
    df_['date_num'] = df_['date_num'].apply(lambda x: round((x/200))*200)
    df_['State code'] = df_['State'].map(state_codes)
    df_ = df_.groupby(['State', 'State code', 'date_num']).sum().reset_index()
    df_ = df_[df_['date_num'].between(val_[0], val_[1])]
    df_ = df_.drop('date_num', axis=1).groupby(
        ['State', 'State code']).sum().reset_index()
    df_['Sales Rounded'] = df_['Sales'].round(2)
    df_['Profit Rounded'] = df_['Profit'].round(2)
    mapp = px.choropleth(
        df_,
        locations='State code',
        locationmode="USA-states",
        color='Sales',
        scope="usa",
        hover_name='State',
        custom_data=['Sales Rounded', 'Profit Rounded'],
        color_continuous_scale='Viridis'
    )

    mapp.update_traces(
        marker_line_color='#FFFFFF',
        marker_line_width=1.5,
        hovertemplate='<b>%{hovertext}</b><br>' +
        'Sales: %{customdata[0]:,.2f} $<br>' +
        'Profit: %{customdata[1]:,.2f} $'
    )

    mapp.update_layout(
        title=dict(
            text='Sales Distribution by State',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
            pad=dict(b=100),
        ),
        geo=dict(
            lakecolor='#d9e3f1',
            bgcolor='#d9e3f1',
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
        font=dict(size=12, color=fontcolor2),
    )
    return mapp


@app.callback(
    Output('map_state', 'figure'),
    Input('map', 'clickData'),
    Input('range-slider2', 'value')
)
def update_bar_chart(clickData, val):
    if clickData is None:
        state_name = 'California'
    else:
        state_name = clickData['points'][0]['hovertext']
    df_ = df.copy()
    df_ = df_[['State', 'City', 'Ship Date', 'Sales', 'Profit', 'Order Date']]
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_['date_num'] = (df_['Order Date']-pd.to_datetime('2014-01-03')).dt.days
    df_['date_num'] = df_['date_num'].apply(lambda x: round((x/200))*200)
    df_ = df_.drop('Order Date', axis=1).groupby(['date_num', 'State', 'City'])[
        ['Sales', 'Profit']].sum().reset_index()
    df_ = df_[(df_['date_num'].between(val[0], val[1]))
              & (df_['State'] == state_name)]
    df_ = df_[['City', 'Sales', 'Profit']].groupby('City').sum().reset_index()
    df_ = df_.sort_values('Sales', ascending=False)
    df_ = df_[:10].sort_values('Sales')
    df_.index = np.arange(0, len(df_))
    middle_index = round(len(df_)/2)
    fig = px.bar(
        df_,
        x='City',
        y='Sales',
        color='Sales',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Sales by City'
    )

    fig.update_traces(
        texttemplate='%{y:.2f}$',
        textposition='inside',
        marker_line_color='#FFFFFF',
        insidetextanchor='middle',
        marker_line_width=1.5,
        showlegend=False
    )

    fig.update_layout(
        title=dict(
            text='Sales by City',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
            pad=dict(b=100)
        ),
        xaxis=dict(
            title='City',
            tickangle=-45,
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=False
        ),
        yaxis=dict(
            title='Sales ($)',
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            ticksuffix='$',
            showgrid=True,
            gridcolor='#d9e3f1',
            range=[0, (df_.iloc[middle_index]['Sales'] * 2)],
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )
    return fig


@callback(
    Output('sub-category-in-state', 'figure'),
    Input('map', 'clickData'),
    Input('range-slider2', 'value')
)
def update_bar_subcategory(clickData, val):
    if clickData is None:
        state_name = 'California'
    else:
        state_name = clickData['points'][0]['hovertext']
    df_ = df.copy()
    df_ = df_[['State', 'Sub-Category', 'Ship Date',
               'Sales', 'Profit', 'Order Date']]
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_['date_num'] = (df_['Order Date']-pd.to_datetime('2014-01-03')).dt.days
    df_['date_num'] = df_['date_num'].apply(lambda x: round((x/200))*200)
    df_ = df_.drop('Order Date', axis=1).groupby(
        ['date_num', 'State', 'Sub-Category'])[['Sales', 'Profit']].sum().reset_index()
    df_ = df_[(df_['date_num'].between(val[0], val[1]))
              & (df_['State'] == state_name)]
    df_ = df_[['Sub-Category', 'Sales', 'Profit']
              ].groupby('Sub-Category').sum().reset_index()
    df_ = df_.sort_values('Sales', ascending=False)
    df_ = df_[:10].sort_values('Sales')
    df_.index = np.arange(0, len(df_))
    middle_index = round(len(df_)/2)
    fig = px.bar(
        df_,
        x='Sub-Category',
        y='Sales',
        color='Sales',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='Sales by Sub-Category'
    )

    fig.update_traces(
        texttemplate='%{y:.2f}$',
        textposition='inside',
        marker_line_color='#FFFFFF',
        insidetextanchor='middle',
        marker_line_width=1.5,
        showlegend=False
    )

    fig.update_layout(
        title=dict(
            text='Sales by Sub-Category',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5,
            pad=dict(b=100)
        ),
        xaxis=dict(
            title='Sub-Category',
            tickangle=-45,
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=False
        ),
        yaxis=dict(
            title='Sales ($)',
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            ticksuffix='$',
            showgrid=True,
            gridcolor='#d9e3f1',
            range=[0, (df_.iloc[middle_index]['Sales'] * 2)],
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )

    return fig


@callback(
    Output('products', 'figure'),
    Input('slider-of-products', 'value'),
    Input('category-for-products', 'value')
)
def product_slider(quantity, category):
    df_ = df[df['Category'].isin(category)]
    df_ = df_[['Product Name', 'short name']].value_counts()[
        :quantity].reset_index()
    fig = px.pie(
        df_,
        values='count',
        names='short name',
        hole=0.35,
        color_discrete_sequence=px.colors.sequential.Viridis,
        title='Distribution by Short Name'
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        textfont_size=14,
        marker=dict(line=dict(color='#FFFFFF', width=2)),
    )

    fig.update_layout(
        title=dict(
            text='Distribution by Short Name',
            font=dict(size=24, color=fontcolor2,
                      family='Arial', weight='bold'),
            x=0.5
        ),
        legend=dict(
            title='Short Name',
            title_font=dict(size=16, color=fontcolor2, family='Arial'),
            font=dict(size=14, color=fontcolor2),
            bgcolor='#d9e3f1',
            bordercolor=fontcolor2,
            borderwidth=1,
            orientation='h',
            yanchor='top',
            xanchor='center',
            x=0.5,
            y=-0.2,
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )
    return fig


@callback(
    Output('profit-sale-product-compare', 'figure'),
    Input('submitiion-button-for-graphs-page2', 'n_clicks'),
    State('checkboxer-for-discount', 'value'),
    State('category-for-product', 'value'),
)
def profit_sale_product_compare(_, discount, selected_product):
    df_ = df[df['Product Name'].isin(selected_product)]
    df_['Discount_presence'] = df_['Discount'].apply(
        lambda x: 'discount' if x > 0 else 'no discount')
    df_ = df_[['Sales', 'Profit', 'Product Name', 'short name', 'Discount_presence']].groupby(
        ['Product Name', 'short name', 'Discount_presence']).sum().reset_index()
    df_['Impact'] = df_['Profit']/df_['Sales']
    df_['Impact'] = (df_['Impact'] + 1).round(4)
    df_ = df_[df_['Discount_presence'].isin(discount)]
    fig = px.bar(
        df_,
        x='short name',
        y='Impact',
        color='Impact',
        pattern_shape='Discount_presence',
        color_continuous_scale=px.colors.sequential.Viridis,
    )

    fig.update_traces(
        texttemplate='%{y:.2f}',
        textposition='inside',
        marker_line_color='#FFFFFF',
        marker_line_width=1.5,
        insidetextanchor='middle',
    )

    fig.update_layout(
        title=dict(
            text='Impact by Short Name',
            font=dict(size=24, color=fontcolor2, family='Arial',
                      weight='bold'),
            x=0.5,
            pad=dict(b=100)
        ),
        xaxis=dict(
            title='Short Name',
            tickangle=-45,
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=False
        ),
        yaxis=dict(
            title='Impact',
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=True,
            gridcolor='#d9e3f1',
        ),
        legend=dict(
            title='Discount Presence',
            title_font=dict(size=14, color=fontcolor2,
                            family='Arial', weight='bold'),
            font=dict(size=12, color=fontcolor2, family='Arial'),
            bordercolor=fontcolor2,
            borderwidth=1,
            orientation="v",
            yanchor="top",
            y=1.4,
            xanchor="left",
            x=.02
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )

    return fig


@callback(
    Output('product-impact-linear', 'figure'),
    Input('submitiion-button-for-graphs-page2', 'n_clicks'),
    State('category-for-product', 'value'),
    State('checkboxer-for-discount', 'value'),
)
def range_slider_impact(_, selected_product, discount):
    df_ = df.copy()
    df_['Order Date'] = pd.to_datetime(df_['Order Date'])
    df_ = df_[['Order Date', 'Sales', 'Profit',
               'Product Name', 'short name', 'Discount']]
    df_['Discount_presence'] = df_['Discount'].apply(
        lambda x: 'discount' if x > 0 else 'no discount')
    df_ = df_.groupby(['Order Date', 'Product Name', 'short name', 'Discount_presence'])[
        ['Sales', 'Profit']].sum().reset_index()
    df_['date_num'] = (df_['Order Date']-pd.to_datetime('2014-01-03')).dt.days
    df_ = df_.sort_values(by='Order Date')
    df_['Impact'] = ((df_['Profit']/df_['Sales']) + 1) * 100
    df_['Impact'] = df_['Impact'].round(2)
    df_ = df_[df_['Product Name'].isin(selected_product)]
    df_ = df_[df_['Discount_presence'].isin(discount)]
    df_['date'] = pd.to_datetime('2014-01-03') + \
        pd.to_timedelta(df_['date_num'], unit='D')
    fig = px.line(
        df_,
        y='Impact',
        x='date',
        color='short name',
        title='Impact Over Time',
        color_discrete_sequence=px.colors.sequential.Viridis,
        hover_data={
            'Impact': ':.2f',
            'date_num': False,
            'short name': True
        },
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='#FFFFFF')),
        mode='lines+markers',
        showlegend=True,
        connectgaps=True,
    )

    fig.update_layout(
        title=dict(
            text='Impact Over Time',
            font=dict(size=24, color=fontcolor2, family='Arial',
                      weight='bold'),
            x=0.5,
            pad=dict(b=10)
        ),
        xaxis=dict(
            title='Date',
            tickangle=-45,
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            showgrid=True,
            gridcolor='#d9e3f1',
        ),
        yaxis=dict(
            title='Impact',
            title_font=dict(size=20, color=fontcolor2, family='Arial'),
            tickfont=dict(size=12, color=fontcolor2),
            ticksuffix='%',
            showgrid=True,
            gridcolor=fontcolor1,
            gridwidth=2,
        ),
        legend=dict(
            title='Short Name',
            title_font=dict(size=14, color=fontcolor2,
                            family='Arial', weight='bold'),
            font=dict(size=12, color=fontcolor2, family='Arial'),
            bordercolor=fontcolor2,
            borderwidth=1,
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(t=40, b=80, l=40, r=40),
        paper_bgcolor='#d9e3f1',
        plot_bgcolor='#d9e3f1',
    )

    return fig


# Callback's for modules

@callback(
    Output('categories-modal-container', 'is_open'),
    Input('categories', 'clickData'),
    State('categories-modal-container', 'is_open')
)
def toggle_modal_categories(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


@callback(
    Output('sub-categories-modal-container', 'is_open'),
    Input('sub-categories', 'clickData'),
    State('sub-categories-modal-container', 'is_open')
)
def toggle_modal_sub_categories(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


@callback(
    Output('one-sales-profit-modal-container', 'is_open'),
    Input('one-sales-profit', 'clickData'),
    State('one-sales-profit-modal-container', 'is_open')
)
def toggle_modal_sales_profit(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


@callback(
    Output('map_state-modal-container', 'is_open'),
    Input('map_state', 'clickData'),
    State('map_state-modal-container', 'is_open'),
)
def toggle_modal_figure_map_state(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


@callback(
    Output('sub-category-in-state-modal-container', 'is_open'),
    Input('sub-category-in-state', 'clickData'),
    State('sub-category-in-state-modal-container', 'is_open'),
)
def toggle_modal_figure_sub_category_in_state(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


@callback(
    Output('categories-modal', 'figure'),
    Input('categories', 'clickData'),
    State('categories', 'figure')
)
def update_modal_figure_categories(clickData, figure):
    if clickData is None:
        return no_update
    return figure


@callback(
    Output('sub-categories-modal', 'figure'),
    Input('sub-categories', 'clickData'),
    State('sub-categories', 'figure')
)
def update_modal_figure_sub_categories(clickData, figure):
    if clickData is None:
        return no_update
    return figure


@callback(
    Output('one-sales-profit-modal', 'figure'),
    Input('one-sales-profit', 'clickData'),
    State('one-sales-profit', 'figure')
)
def update_modal_figure_sales_profit(clickData, figure):
    if clickData is None:
        return no_update
    return figure


@callback(
    Output('map_state-modal', 'figure'),
    Input('map_state', 'clickData'),
    State('map_state', 'figure'),
)
def update_modal_figure_map_state(clickData, figure):
    if clickData is None:
        return no_update
    return figure


@callback(
    Output('sub-category-in-state-modal', 'figure'),
    Input('sub-category-in-state', 'clickData'),
    State('sub-category-in-state', 'figure'),
)
def update_modal_figure_sub_category_in_state(clickData, figure):
    if clickData is None:
        return no_update
    return figure


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
