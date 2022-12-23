import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import os
import datetime
from dash import html
import pandas as pd
import plotly

# Generador de callbacks para click sobre tarjetas
def basicViewGraphCBGenerator(kpiName, eventName):
    def callback(_,__):
        triggeringCB = dash.callback_context.triggered_prop_ids
        print(dash.callback_context.triggered_id)

        fig = plotly.graph_objs.Figure()
        lastWeekMeanSeries = thisWeekKPIs_USPP.groupby([thisWeekKPIs_USPP['Start Time'].dt.date])[kpiName].mean()
        df = pd.DataFrame({'Start Time':lastWeekMeanSeries.index, lastWeekMeanSeries.name: lastWeekMeanSeries.values})

        fig.update_layout(
            title={
                'text':kpiName if kpiName else "",
                'font':{'size':10}
                },
            autosize=False,
            width=300,
            height=300,
            margin={'t':50, 'r':10, 'l':10, 'autoexpand':True,},
            xaxis={'fixedrange':True},
            yaxis={'fixedrange':True},
        )

        fig.add_trace(
            plotly.graph_objs.Scatter(
                x=df['Start Time'],
                y=df[lastWeekMeanSeries.name],
                )
            )

        if len(triggeringCB.keys()) and (list(triggeringCB.keys())[0] == eventName):
            print(triggeringCB.keys())
            return fig

        return fig

    return callback

# Cargado del dataframe de donde se va a sacar la data
def queryDataFromDB_USPP(start_date=datetime.datetime.today() - datetime.timedelta(days=20), end_date=datetime.datetime.today()) -> pd.DataFrame:
    """
    TODO: Termina de implementarme.
    Esta funcion hace un query hacia la base de datos para obtener la data que se encuentra dentro del 
    rango de fechas especificado
    """
    root_USPP = 'assets/data_uspp/'
    dfs_USPP = []
    for _, _, names in os.walk(root_USPP):
        for name in names:
            path = root_USPP+name
            dfs_USPP.append(pd.read_csv(path))

    df_USPP = pd.concat(dfs_USPP, ignore_index=True)
    df_USPP['Start Time'] = pd.to_datetime(df_USPP['Start Time'])
    return df_USPP[df_USPP['Start Time'] > start_date][df_USPP['Start Time'] < end_date]

kpiDF_USPP = queryDataFromDB_USPP()

thisWeekKPIs_USPP = kpiDF_USPP.copy(deep=True)

# cpu_kpi_list = dbc.ListGroup(children=[
#     dbc.ListGroupItem(dash.html.Div(children=[
#         'Mean ratio of the CPU usage of the main processor(%): ', thisWeekKPIs_USPP['Mean ratio of the CPU usage of the main processor(%)'].mean()
#     ])) ,
#     dbc.ListGroupItem(dash.html.Div(children=[
#         'Duration of peak load of CPU usage of the main processor(s): ', round(thisWeekKPIs_USPP['Duration of peak load of CPU usage of the main processor(s)'].mean(), 3) 
#     ]))
# ])

spr_subs_kpi_list = dbc.ListGroup(children=[
    dbc.ListGroupItem(dash.html.Div(children=[
        'Number of Total SPR Subscribers: ', round(thisWeekKPIs_USPP['Number of SPR Subscribers'].mean()) 
    ])),
    # dbc.ListGroupItem(dash.html.Div(children=[
    #     'Total number of IP addresses in the PGW IP pool: ', round(thisWeekKPIs_USPP['Total number of IP addresses in the PGW IP pool'].mean(), 3) 
    # ])),
])

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='USPP (HSS/SPR)'),
    dash.dcc.Tabs(id="USPP-tabs", value='basicView', children=[
        dash.dcc.Tab(label='Basic view', value='basicView', children=[            
            dash.html.Div(id='basicTab',children=[
                dash.html.Div(className='card_container', children=[
                    
                    dash.html.Div(id='crm_operation_card',className='infoCard', children=[
                        dash.html.H3('CRM Operation'),
                        dash.html.H4('Daily Average'),
                        dash.html.Div(children=[
                            dash.html.Div(children=[
                                daq.Gauge(
                                    color={"gradient":True, "ranges":{"red":[0,40], "yellow":[40,80], "green": [80,100]}},
                                    value=int(kpiDF_USPP['Successful Ratio of BOSS Operation(%)'].mean()),
                                    showCurrentValue=True,
                                    units="%",
                                    label='CRM Operation Success (%)',
                                    max=100,
                                    min=0,
                                    size=200,
                                ),
                            ], className='gaugeDiv'),
                            dash.html.Div(children=[
                                daq.Gauge(
                                    color={"gradient":True, "ranges":{"red":[0,40], "yellow":[40,80], "green": [80,100]}},
                                    value=int(kpiDF_USPP['Successful Ratio of BOSS Operation(%)'].mean()),
                                    showCurrentValue=True,
                                    units="%",
                                    label='CRM Operation Success (%)',
                                    max=100,
                                    min=0,
                                    size=200,
                                ),
                            ], className='gaugeDiv'),
                        ], className='gaugeContainer'),
                        
                    ]),

                    dash.html.Div(id='spr_subs', className='infoCard', children=[
                        dash.html.H3('SPR Registered Users'),
                        dash.html.H4('Daily Average'),
                        #dash.dcc.Graph(id='daily_ip_usage', figure={'layout': {'height': 270, 'width':270, 'margin':{'t':50, 'r':10}, 'title': 'Peak load of CPU usage of the main processor(%)'}}, config={'displayModeBar':False, 'responsive':True, 'scrollZoom': True}),
                        daq.Gauge(
                           # color={"gradient":True, "ranges":{"green":[0,40], "yellow":[40,80], "red": [80,100]}},
                            #color={"gradient":True},
                            value=int(kpiDF_USPP['Number of SPR Registered User'].mean()),
                            showCurrentValue=True,
                            units='Users',
                            label='SPR Registered Users',
                            max=round(kpiDF_USPP['Number of SPR Subscribers'].mean()),
                            min=0,
                            size=200,
                        ),
                        spr_subs_kpi_list,
                        ]),
                    
                    dash.html.Div(id='crm_operation_card_hist',className='infoCard', children=[
                        dash.html.H3('CRM Operation'),
                        dash.html.H4('Week History'),
                        dash.dcc.Graph(id='weekly_crm_operation', 
                                      figure={'layout': {'height': 270, 'width':270, 'margin':{'t':50, 'r':10}, 'title': 'CRM Operation Success (%)'}}, 
                                      config={'displayModeBar':False, 'responsive':True, 'scrollZoom': True}
                        ),
                    ]),
                    
                    dash.html.Div(id='spr_users_card_hist',className='infoCard', children=[
                        dash.html.H3('SPR Users'),
                        dash.html.H4('Week History'),
                        dash.dcc.Graph(id='weekly_spr_users', 
                                      figure={'layout': {'height': 270, 'width':270, 'margin':{'t':50, 'r':10}, 'title': 'CRM Operation Success (%)'}}, 
                                      config={'displayModeBar':False, 'responsive':True, 'scrollZoom': True}
                        ),
                    ]),
                    
                    dash.html.Div(id='spr_subs_card_hist',className='infoCard', children=[
                        dash.html.H3('SPR Registered Users'),
                        dash.html.H4('Week History'),
                        dash.dcc.Graph(id='spr_subs', 
                                      figure={'layout': {'height': 270, 'width':270, 'margin':{'t':50, 'r':10}, 'title': 'CRM Operation Success (%)'}}, 
                                      config={'displayModeBar':False, 'responsive':True, 'scrollZoom': True}
                        ),
                    ]),
                    
                    ])
                ])
            ]),
        # dash.dcc.Tab(label='Advanced view', value='advancedView', id='advancedTabGraphTab',children=[
        #     html.Div(id='advancedTab', children=[
        #         html.Div(children=[
        #             dash.dcc.DatePickerRange(
        #                 id='dateRange',
        #                 min_date_allowed=kpiDF_USPP['Start Time'].min() - datetime.timedelta(days=1),
        #                 max_date_allowed=kpiDF_USPP['Start Time'].max() + datetime.timedelta(days=1),
        #                 initial_visible_month=kpiDF_USPP['Start Time'].max(),
        #                 start_date=kpiDF_USPP['Start Time'].min().date(),
        #                 end_date=kpiDF_USPP['Start Time'].max().date() + datetime.timedelta(days=1),
        #                 ),
        #             dash.html.Div(className='graphsContainer',children=[
        #                 dash.dcc.Graph(
        #                     id='advancedTabGraph',
        #                     figure={
        #                         'data':[{
        #                             'type':'line'
        #                             }],
        #                         'layout': {'margin':{'t':50, 'r':0}}
        #                         }
        #                     ),
        #                 dash.dcc.Graph(
        #                     id='dailyGraph',
        #                     figure={
        #                         'data':[{
        #                             'type':'line'
        #                             }],
        #                         'layout': {'margin':{'t':50, 'r':0}}
        #                         })
        #                 ]),
        #             dash.html.Label('Statistical information'),
        #             dash.dcc.Checklist(options=['std'], id='metricsCheckList', value=[]),
        #             dash.html.Br(),
        #             dash.html.Label('KPIs to be selected'),
        #             dash.dcc.Dropdown(options=kpiDF_USPP.columns[5:], value=[kpiDF_USPP.columns[7]], multi=True, id='kpiSelector', placeholder="Select a KPI"),
        #             ]),
        #         html.Div(id='statsContainer'),
        #         ]),
        #     ]),
        ]),
    ])

# Callbacks para los graficos de las cartas
dash.callback(
                dash.Output('weekly_crm_operation', 'figure'),
                dash.Input('weekly_crm_operation', 'figure'),
                dash.Input('weekly_crm_operation', 'clickData'),
                )(basicViewGraphCBGenerator('Successful Ratio of BOSS Operation(%)', 'weekly_crm_operation.clickData'))

dash.callback(
                dash.Output('weekly_spr_users', 'figure'),
                dash.Input('weekly_spr_users', 'figure'),
                dash.Input('weekly_spr_users', 'clickData'),
                )(basicViewGraphCBGenerator('Number of SPR Registered User', 'weekly_spr_users.clickData'))

dash.callback(
                dash.Output('spr_subs', 'figure'),
                dash.Input('spr_subs', 'figure'),
                dash.Input('spr_subs', 'clickData'),
                )(basicViewGraphCBGenerator('Number of SPR Subscribers', 'spr_subs.clickData'))