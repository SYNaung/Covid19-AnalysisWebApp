#import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import pydeck as pdk
import datetime
import plotly.express as px
import plotly.graph_objects as go
import re
import random
from plotly.subplots import make_subplots
import matplotlib.gridspec as gridspec
import os

#plot style
plt.style.use("ggplot")
st.set_option('deprecation.showPyplotGlobalUse', False)

#pc or mobile
pc_user = st.sidebar.checkbox("Show interactive graphs (recommended for pc users)", value=False)

#music
playlist = ["playlist/Aerosmith - I don't want to miss a thing.mp3",
            "playlist/Clairo, Peter Cottontale - Softly.mp3",
            "playlist/Harry Styles - Carolina.mp3",
            "playlist/Kings of Convenience - Boat Behind.mp3",
            "playlist/Kiss - I Was Made For Lovin' You.mp3",
            "playlist/Leonard Cohen - The Future.flac",
            "playlist/My Chemical Romance - Helena.mp3",
            "playlist/Oasis - Live Forever.mp3",
            "playlist/Pink Floyd - Coming Back To Life.flac",
            'playlist/Simon & Garfunkel - El Condor Pasa (If I Could).mp3',
            "playlist/Arcitc Monkeys - Old Yellow Bricks.mp3",
            "playlist/Beastie Boys - Sabotage.mp3",
            "playlist/Derek & The Dominos - Layla.mp3",
            "playlist/Fleetwood Mac - Dreams.mp3",
            "playlist/John Paesano -  Subway Feels.mp3",
            "playlist/My Chemical Romance - Party Poison.mp3",
            "playlist/Paramore - Hard Times.mp3",
            "playlist/Red Hot Chili Peppers - Can't Stop.mp3",
            "playlist/The Alan Parsons Project - Eye in the Sky.mp3",
            "playlist/The Rolling Stones - Miss You.mp3"]
st.sidebar.markdown("### You can listen to music while scrolling!")

song_no = random.randint(0,19)
st.sidebar.text(re.sub("playlist/","",playlist[song_no]))
st.sidebar.audio(playlist[song_no])


#Map
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9GWlx9wsSxy253wGLjRqq79cQ1n4_X5N4dx6JemV7evq3DeGXSDdpnu4M9K4Rceujw3rt_CJRS5aD/pub?output=csv"
#url = "Case by Township - MMR-COVID19 - Sheet1.csv"
covid = pd.read_csv(url)

drop_list = ['Objectidfieldname','Uniqueidfield Name','Uniqueidfield Issystemmaintained',
 'Globalidfieldname','Servergens Minservergen','Servergens Servergen',
 'Geometrytype','Spatialreference Wkid','Spatialreference Latestwkid',
 'Fields Name','Fields Type','Fields Alias','Fields Sqltype','Fields Domain',
 'Fields Length','Features Attributes Globalid','Features Attributes Creator',
 'Features Attributes Editor','Fields Defaultvalue']

#drop columns
cov = covid.drop(drop_list, axis=1)

#change date format
def unixtodatetime(x):
    dt = datetime.datetime.fromtimestamp(int(x)/1000)
    return dt
cov["Datetime"] = cov["Features Attributes Creationdate"].apply(lambda x: unixtodatetime(x))

#another date column
def datetostr(y):
    strdate = datetime.datetime.fromtimestamp(int(y)/1000).strftime("%Y-%m-%d %H:%M")
    return strdate
cov["Datetime_str"] = cov["Features Attributes Creationdate"].apply(lambda y: datetostr(y))

#rename lat,long for map
cov.rename(columns={"Features Attributes Latitude":"latitude", "Features Attributes Longitude":"longitude"}, inplace=True)

#group region names
sr = cov.groupby(by="Features Attributes Sr").sum()
sr_list = list(sr.index)
st.title("Covid-19 Myanmar Status")
st.header("Cases by Township")

#for 3d map
township_confirmed = cov[["Features Attributes Township", "Features Attributes Confirmed", "Features Attributes Sr"]]
map3d = cov[["Features Attributes Township", "latitude","longitude", "Features Attributes Confirmed"]]
map3d.rename(columns={"Features Attributes Confirmed":"Confirmed_Cases"}, inplace=True)

#last updated date for map
mm_last_updated = (cov["Datetime"].sort_values(axis=0))[-1:]
mm_last_updated = mm_last_updated.dt.strftime("%d/%m/%y")

#remove 'township'
def township_remove(t):
    result = re.sub(" Township","",t)
    return result
township_confirmed["Features Attributes Township"] = township_confirmed["Features Attributes Township"].apply(lambda t: township_remove(t))

#3d view
def view_in_3D():
        view_select = st.selectbox("3D View Options:", ["ColumnLayer", "ScatterplotLayer", "HeatmapLayer"])

        if view_select == "ScatterplotLayer":
            opacity_value = 0.5,
        elif view_select == "ColumnLayer":
            opacity_value = 0.7,
        else:
            opacity_value =0.4,

        view_state = pdk.ViewState(
            longitude= 96.011,
            latitude= 17.8,
            zoom=6.5,
            min_zoom=4,
            max_zoom=16,
            pitch=35,
        )

        COLOR_BREWER_BLUE_SCALE = [
            [240, 249, 232],
            [204, 235, 197],
            [168, 221, 181],
            [123, 204, 196],
            [67, 162, 202],
            [8, 104, 172],
        ]

        CUSTOM_COLOR1 = [
            [255,255,178],
            [254,217,118],
            [254,178,76],
            [253,141,60],
            [240,59,32],
            [189,0,38]
        ]

        CUSTOM_COLOR2 = [
            [254,229,217],
            [252,187,161],
            [252,146,114],
            [251,106,74],
            [222,45,38],
            [165,15,21]
        ]

        layer = pdk.Layer(
            view_select,
            data=map3d,
            get_position=["longitude", "latitude"],
            get_elevation= "Confirmed_Cases",
            auto_highlight=True,
            radius=2000,
            opacity = opacity_value,
            filled=True,
            radius_min_pixels=5,
            radius_max_pixels=15,
            radius_scale=500,
            get_fill_color=[227,65,50,190],
            colorRange = CUSTOM_COLOR1,
            extruded=True,
            get_radius=2.5,
            pickable=True,
            elevation_scale=500,
            coverage=0.3,
        )



        map3dst = pdk.Deck(map_style="mapbox://styles/mapbox/dark-v9",
                          layers=[layer],
                          initial_view_state=view_state,
                          tooltip={"text": "{Features Attributes Township}, Confimed cases: {Confirmed_Cases}"})
        st.text("Last updated: " + mm_last_updated.to_string(index=False))
        st.write(map3dst)

#list for graph view
rs_names = list(np.unique(cov["Features Attributes Sr"]))
rs_names = rs_names[-1:] + rs_names[:-1]
rs_names.insert(0,"All Regions and States")

#graph view
def township_bar():
    rs_select = st.selectbox("Region/State:", rs_names)
    if rs_select == "All Regions and States":
        pie_fig = px.pie(cov, values="Features Attributes Confirmed", names="Features Attributes Sr",
                         labels={"Features Attributes Confirmed": "Confirmed Cases",
                                 "Features Attributes Sr": "Region/State"})
        st.text("Last updated: " + mm_last_updated.to_string(index=False))
        if pc_user==False:
            pie_fig.update_layout(height=470,width=430)
            st.write(pie_fig, use_container_width=True)
        elif pc_user==True:
            st.write(pie_fig, use_container_width=False)
    else:
        rs = township_confirmed[township_confirmed["Features Attributes Sr"] == rs_select]
        bar_township_fig = px.bar(rs, y="Features Attributes Township", x="Features Attributes Confirmed", labels={
            "Features Attributes Township": "Township",
            "Features Attributes Confirmed": "Confirmed Cases"
        }, orientation="h")
        total_rs_cases = rs["Features Attributes Confirmed"].sum()
        bar_township_fig.update_layout(height=500,xaxis_tickangle=90)
        bar_township_fig.update_yaxes(nticks=len(rs["Features Attributes Township"]), tickfont=dict(size=8))
        st.text("Last updated: " + mm_last_updated.to_string(index=False))
        st.text("Total cases in " + rs_select + ": " + str(total_rs_cases))


        #township_fig=sns.barplot(y="Features Attributes Township", x="Features Attributes Confirmed", data=rs, orient="h", color="royalblue")
        #township_fig.set(xlabel="Cases", ylabel="Township")
        #township_fig.set_yticklabels(rs["Features Attributes Township"],size=7)
        #for index, row in rs["Features Attributes Confirmed"].iterrows():
        #    township_fig.text(row.name, row.tip, round(row.total_bill, 2), color='black', ha="center")

        plt.barh(rs["Features Attributes Township"], rs["Features Attributes Confirmed"], color="royalblue")
        plt.yticks(rs["Features Attributes Township"], rotation=0, fontsize=6)
        for index, value in enumerate(rs["Features Attributes Confirmed"]):
            plt.text(value , index, str(int(value)), color="black", va="center", rotation=0,size=6)

        if pc_user==True:       st.write(bar_township_fig)
        elif pc_user==False:    st.pyplot()


#2d view
def view_in_2D():
    view_state = pdk.ViewState(
        longitude=96.011,
        latitude=17.8,
        zoom=3.5,
        max_zoom=20,
        pitch=0,
    )
    CUSTOM_COLOR1 = [
        [255, 255, 178],
        [254, 217, 118],
        [254, 178, 76],
        [253, 141, 60],
        [240, 59, 32],
        [189, 0, 38]
    ]
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map3d,
        get_position=["longitude", "latitude"],
        get_elevation="Confirmed_Cases",
        auto_highlight=True,
        radius=1000,
        opacity=0.5,
        filled=True,
        radius_min_pixels=5,
        radius_max_pixels=15,
        radius_scale=500,
        get_fill_color=[227, 65, 50, 190],
        colorRange=CUSTOM_COLOR1,
        extruded=False,
        get_radius=5.5,
        pickable=True,
        elevation_scale=0,
    )
    map2dst = pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                       layers=[layer],
                       initial_view_state=view_state,
                       tooltip={"text": "{Features Attributes Township}, Confimed cases: {Confirmed_Cases}"})
    st.text("Last updated: " + mm_last_updated.to_string(index=False))
    st.write(map2dst)


#select view
township_view = st.selectbox("View:", [ "2D map", "3D map","Graph"])

#display map view
if township_view == "3D map":
    view_in_3D()
elif township_view == "Graph":
    township_bar()
else:
    view_in_2D()
    


#Statistics

#urls
#confirmed_url = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv"
confirmed_url = "time_series_covid19_confirmed_global.csv"
recovered_url = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_recovered_global.csv&filename=time_series_covid19_recovered_global.csv"
#recovered_url = "time_series_covid19_recovered_global.csv"
death_url = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv"
#death_url = "time_series_covid19_deaths_global.csv"

#cleaning data for Myanmar
def data_loader(d):
    covid = pd.read_csv(d)
    covid.drop(["Lat", "Long"], axis=1, inplace=True)
    covid19 = covid.groupby("Country/Region").sum()
    covidBurma = pd.DataFrame(covid19.loc["Burma"])
    covidBurma.reset_index(inplace=True)
    covidBurma.rename(columns={"index": "Date", "Burma": "Cases"}, inplace=True)
    return covidBurma

#date convert
def global_date_convert(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date"] = df["Date"].dt.strftime("%d/%m/%y")
    return df

#LET'S GOOOOOOOOO
st.header("Statistics")

#load_data
confirmedMM = data_loader(confirmed_url)
recoveredMM = data_loader(recovered_url)
deathMM = data_loader(death_url)

#date convert..again. gosh so many.
confirmedMM = global_date_convert(confirmedMM)

analysis_df = cov[["Features Attributes Sr", "Features Attributes Township", "Datetime", "Features Attributes Confirmed"]]
analysis_df = analysis_df.sort_values(by="Datetime")

#"Oh fuck, so repeatitive" section :(
confirmed_last = int(confirmedMM["Cases"][-1:])
recovered_last = int(recoveredMM["Cases"][-1:])
death_last = int(deathMM["Cases"][-1:])

wave_seperator = confirmedMM[confirmedMM["Date"] == "16/08/20"].index.values.astype(int)[0]
first_wave_confirmed = confirmedMM[:wave_seperator]
second_wave_confirmed = confirmedMM[wave_seperator:]
first_wave_recovered = recoveredMM[:wave_seperator]
second_wave_recovered = recoveredMM[wave_seperator:]
first_wave_death = deathMM[:wave_seperator]
second_wave_death = deathMM[wave_seperator:]

first_wave_last_confirmed = int(first_wave_confirmed["Cases"][-1:])
first_wave_last_recovered = int(first_wave_recovered["Cases"][-1:])
first_wave_last_death = int(first_wave_death["Cases"][-1:])

second_wave_last_confirmed = (int(second_wave_confirmed["Cases"][-1:])-first_wave_last_confirmed)
second_wave_last_recovered = int(second_wave_recovered["Cases"][-1:])-first_wave_last_recovered
second_wave_last_death = int(second_wave_death["Cases"][-1:])-first_wave_last_death

#for MOTHER RUSSIA!!! I mean for Staticstical graphs :3
contents=["First wave confirmed","Second wave confirmed", "First wave recovered","Second wave recovered","First wave death", "Second wave death"]
counts = [first_wave_last_confirmed, second_wave_last_confirmed,
          first_wave_last_recovered, second_wave_last_recovered,
          first_wave_last_death, second_wave_last_death]

#for mobile graph pies except general
def abs_value(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:d}\n{:.1f}%".format(absolute, pct)

#select statistics graph
graph_select = st.selectbox("Graph:",["General","Total Cases", "Daily Cases", "Recovered", "Death"])

#Here we go, another fucking repeatitive shit. I'm a bad coder, duh.
if graph_select == "Total Cases":
    if pc_user==True:
        total_cases_fig = make_subplots(rows=4, cols=4, subplot_titles=("Total cases all time", "Last 15 days"),
                                    specs=[[{"rowspan": 2, "colspan": 4, "type": "xy"}, None, None, None],
                                           [None, None, None, None],
                                           [{"rowspan": 2, "colspan": 3, "type": "xy"}, None, None, {"rowspan":2,"type":"pie"}],
                                           [None, None, None, None]])
        total_cases_fig.add_trace(
            go.Scatter(x=confirmedMM["Date"], y=confirmedMM["Cases"], showlegend=False),
            row=1,
            col=1
        )
        total_cases_fig.add_trace(
            go.Bar(x=confirmedMM["Date"][-15:], y=confirmedMM["Cases"][-15:], marker_color="teal",
                   text=confirmedMM["Cases"][-15:], textposition="auto",showlegend=False),
            row=3,
            col=1
        )
        total_cases_fig.add_trace(
            go.Pie(values=[first_wave_last_confirmed, second_wave_last_confirmed], labels=["First wave", "Second wave"], name="Total cases",
                   textinfo="percent+value", hole=.7, showlegend=True, marker_colors=["mediumturquoise", "teal"], title="Total"),
            row=3,
            col=4
        )


        total_cases_fig.update_xaxes(nticks=1)
        total_cases_fig.update_layout(
                height=600,width=700,legend=dict(orientation="h", yanchor="bottom", xanchor='right', x=1.2)
           )
        st.text("Last updated: "+ (confirmedMM["Date"][-1:].to_string(index = False)))
        st.plotly_chart(total_cases_fig,use_container_width=False)

    elif pc_user==False:
        #Mobile
        total_subplot = gridspec.GridSpec(4,4)
        all = plt.subplot(total_subplot[:2,:])
        days_ago = plt.subplot(total_subplot[2:,:3])
        pie = plt.subplot(total_subplot[2:,3:])
        all.plot(confirmedMM["Date"], confirmedMM["Cases"], color="royalblue")
        all.set_xticks(ticks=[])
        all.set_title("Total cases all time", size=9)
        days_ago.bar(confirmedMM["Date"][-15:], confirmedMM["Cases"][-15:], color="steelblue")
        days_ago.tick_params(axis="x", labelsize=7)
        days_ago.set_xticklabels(confirmedMM["Date"][-15:], rotation=90)
        for index,value in enumerate(confirmedMM["Cases"][-15:]):
            days_ago.text(index-0.225, value, str(value), color="white",va="top", rotation=90, size=8)
        days_ago.set_title("Last 15 days", size=8, pad=0)
        pie.pie(x=[first_wave_last_confirmed,second_wave_last_confirmed], labels=["First wave", "Second wave"],
                autopct= lambda pct: abs_value(pct, [first_wave_last_confirmed,second_wave_last_confirmed]), labeldistance=1.2, startangle=90, textprops={'fontsize':8},
                colors= ["mediumturquoise","steelblue"])
        pie.set_title("Total", size=9, pad=10)
        st.text("Last updated: " + (confirmedMM["Date"][-1:].to_string(index=False)))
        st.pyplot()

elif graph_select == "Daily Cases":
    new_cases = confirmedMM["Cases"].diff()
    st.text("Last updated: " + (confirmedMM["Date"][-1:].to_string(index=False)))
    days_ago = st.slider("Days ago", 0, 60)
    if pc_user==True:
        if days_ago==0: title=" (All time)"
        else: title="("+str(days_ago)+" days ago)"
        new_cases_fig = go.Figure()
        if days_ago>30 or days_ago==0:
                new_cases_fig.add_trace(
                go.Bar(x=confirmedMM["Date"][-1*days_ago:], y=new_cases[-1*days_ago:], showlegend=False, name="New case"),
            )
        else:
                new_cases_fig.add_trace(
                go.Bar(x=confirmedMM["Date"][-1*days_ago:], y=new_cases[-1*days_ago:], name="Last "+str(days_ago)+" days new cases",
                       text=new_cases[-1*days_ago:], textposition="auto", showlegend=False),
            )

        new_cases_fig.update_xaxes(nticks=15)

        st.write(new_cases_fig)

    elif pc_user==False:
        #Mobile
        if days_ago==0: title=" (All time)"
        else: title="("+str(days_ago)+" days ago)"
        if days_ago==0:
            plt.bar(confirmedMM["Date"][-1*days_ago:], new_cases[-1*days_ago:], color="darkgoldenrod")
            plt.xticks([], rotation=90, fontsize=8)
        else:
            plt.bar(confirmedMM["Date"][-1*days_ago:], new_cases[-1*days_ago:], color="darkgoldenrod")
            plt.title("Daily Cases "+"("+str(days_ago)+" days ago)", fontdict={'fontsize':9})
            plt.xticks(confirmedMM["Date"][-1 * days_ago:], rotation=90, fontsize=5.5)
            for index, value in enumerate(new_cases[-1*days_ago:]):
                plt.text(index-(days_ago/150), value, str(int(value)), color="white", va="top", rotation=90, size=11-((days_ago/10)+0.5))
        st.pyplot()

elif graph_select == "Recovered":
    if pc_user==True:
        recovered_cases_fig = make_subplots(rows=4, cols=4, subplot_titles=("Recovered cases all time", "Last 15 days"),
                                        specs=[[{"rowspan": 2, "colspan": 4, "type": "xy"}, None, None, None],
                                               [None, None, None, None],
                                               [{"rowspan": 2, "colspan": 3, "type": "xy"}, None, None,
                                                {"rowspan": 2, "type": "pie"}],
                                               [None, None, None, None]])
        recovered_cases_fig.add_trace(
            go.Scatter(x=recoveredMM["Date"], y=recoveredMM["Cases"], showlegend=False, marker_color="forestgreen"),
            row=1,
            col=1
        )
        recovered_cases_fig.add_trace(
            go.Bar(x=recoveredMM["Date"][-15:], y=recoveredMM["Cases"][-15:], marker_color="seagreen", name="Last 15 days",
                   text=recoveredMM["Cases"][-15:], textposition="auto", showlegend=False),
            row=3,
            col=1
        )
        recovered_cases_fig.add_trace(
            go.Pie(values=[first_wave_last_recovered, second_wave_last_recovered], labels=["First wave", "Second wave"],
                   name="Total recovered", textposition="outside",
                   textinfo="percent+value", hole=0.7, showlegend=True, marker_colors=["springgreen", "seagreen"],
                   title="Recovered"),
            row=3,
            col=4
        )

        recovered_cases_fig.update_xaxes(nticks=1)
        recovered_cases_fig.update_layout(
            height=600, width=700, legend=dict(orientation="h", yanchor="bottom", xanchor='right', x=1.2)
        )
        st.text("Last updated: " + (recoveredMM["Date"][-1:].to_string(index=False)))
        st.write(recovered_cases_fig)

    elif pc_user==False:
        #Mobile
        recovered_subplot = gridspec.GridSpec(4, 4)
        all = plt.subplot(recovered_subplot[:2, :])
        days_ago = plt.subplot(recovered_subplot[2:, :3])
        pie = plt.subplot(recovered_subplot[2:, 3:])
        all.plot(recoveredMM["Date"], recoveredMM["Cases"], color="forestgreen")
        all.set_xticks(ticks=[])
        all.set_title("Recovered", size=9)
        days_ago.bar(recoveredMM["Date"][-15:], recoveredMM["Cases"][-15:], color="seagreen")
        days_ago.tick_params(axis="x", labelsize=7)
        days_ago.set_xticklabels(recoveredMM["Date"][-15:], rotation=90)
        for index, value in enumerate(recoveredMM["Cases"][-15:]):
            days_ago.text(index - 0.225, value, str(value), color="white", va="top", rotation=90, size=8)
        days_ago.set_title("Last 15 days", size=8, pad=0)
        pie.pie(x=[first_wave_last_recovered, second_wave_last_recovered], labels=["First wave", "Second wave"],
                autopct=lambda pct: abs_value(pct, [first_wave_last_recovered,second_wave_last_recovered]), labeldistance=1.2, startangle=50, textprops={'fontsize': 8},
                colors=["springgreen", "seagreen"])
        pie.set_title("Recovered", size=9, pad=10)
        st.text("Last updated: " + (recoveredMM["Date"][-1:].to_string(index=False)))
        st.pyplot()


elif graph_select == "Death":
    if pc_user==True:
        death_cases_fig = make_subplots(rows=4, cols=4, subplot_titles=("Death cases all time", "Last 15 days"),
                                            specs=[[{"rowspan": 2, "colspan": 4, "type": "xy"}, None, None, None],
                                                   [None, None, None, None],
                                                   [{"rowspan": 2, "colspan": 3, "type": "xy"}, None, None,
                                                    {"rowspan": 2, "type": "pie"}],
                                                   [None, None, None, None]])
        death_cases_fig.add_trace(
            go.Scatter(x=deathMM["Date"], y=deathMM["Cases"], showlegend=False, marker_color="firebrick"),
            row=1,
            col=1
        )
        death_cases_fig.add_trace(
            go.Bar(x=deathMM["Date"][-15:], y=deathMM["Cases"][-15:], marker_color="brown", name="Last 15 days",
                   text=deathMM["Cases"][-15:], textposition="auto", showlegend=False),
            row=3,
            col=1
        )
        death_cases_fig.add_trace(
            go.Pie(values=[first_wave_last_death, second_wave_last_death], labels=["First wave", "Second wave"],
                   name="Total death", textposition="outside",
                   textinfo="percent+value", hole=0.7, showlegend=True, marker_colors=["indianred", "brown"],
                   title="Death"),
            row=3,
            col=4
        )

        death_cases_fig.update_xaxes(nticks=1)
        death_cases_fig.update_layout(
            height=600, width=700, legend=dict(orientation="h", yanchor="bottom", xanchor='right', x=1.2)
        )
        st.text("Last updated: " + (deathMM["Date"][-1:].to_string(index=False)))
        st.write(death_cases_fig)

    elif pc_user==False:
        #Mobile
        death_subplot = gridspec.GridSpec(4, 4)
        all = plt.subplot(death_subplot[:2, :])
        days_ago = plt.subplot(death_subplot[2:, :3])
        pie = plt.subplot(death_subplot[2:, 3:])
        all.plot(deathMM["Date"], deathMM["Cases"], color="firebrick")
        all.set_xticks(ticks=[])
        all.set_title("Death", size=9)
        days_ago.bar(deathMM["Date"][-15:], deathMM["Cases"][-15:], color="brown")
        days_ago.tick_params(axis="x", labelsize=7)
        days_ago.set_xticklabels(deathMM["Date"][-15:], rotation=90)
        for index, value in enumerate(deathMM["Cases"][-15:]):
            days_ago.text(index - 0.225, value, str(value), color="white", va="top", rotation=90, size=8)
        days_ago.set_title("Last 15 days", size=8, pad=0)
        pie.pie(x=[first_wave_last_death, second_wave_last_death], labels=["First wave", "Second wave"],
                autopct=lambda pct: abs_value(pct, [first_wave_last_death, second_wave_last_death]),
                labeldistance=1.2, startangle=80, textprops={'fontsize': 8, 'color':'white'},
                colors=["indianred", "brown"])
        pie.set_title("Death", size=9, pad=10)
        st.text("Last updated: " + (deathMM["Date"][-1:].to_string(index=False)))
        st.pyplot()

elif graph_select == "General":
        if pc_user==True:
            general_fig = make_subplots(rows=4, cols=4,
                                      specs=[[{"rowspan":4, "colspan":4, "type":"pie"}, None, None, None],
                                             [None, None, None, None],
                                             [None, None, None, None],
                                             [None, None,None,None]])

            general_fig.add_trace(
                go.Pie(values=counts,labels=contents, hole=0.6, name="Total", textinfo="percent",insidetextorientation='radial', title="Total", textposition="outside",
                       marker_colors=["cornflowerblue","lightskyblue","mediumspringgreen","lightgreen","red","indianred"]),
                row=1,
                col=1
            )

            #general_fig.add_trace(
            #    go.Bar(y=["Second wave total", "First wave total"],
            #           x=[second_wave_last_confirmed-(second_wave_last_recovered+second_wave_last_death),
            #             first_wave_last_confirmed-(first_wave_last_recovered+first_wave_last_death)], orientation="h",
            #            marker_color="dodgerblue",showlegend=False),
            #            row=4,
            #            col=1,)
            #general_fig.add_trace(
             #   go.Bar(y=["Second wave total", "First wave total"],
              #         x=[second_wave_last_recovered,
            #           first_wave_last_recovered],
            #           orientation="h", marker_color="rgb(58,190,80)",
            #           showlegend=False),
            #            row=4,
            #            col=1,)
            #general_fig.add_trace(
            #    go.Bar(y=["Second wave total", "First wave total"],
            #           x=[second_wave_last_death,
            #              first_wave_last_death],
            #           orientation="h", marker_color="indianred",
            #           showlegend=False),
            #            row=4,
            #            col=1,)


            #general_fig.update_layout(barmode="relative", showlegend=False)
            #general_fig.update_xaxes(tickfont=dict(size=10), showgrid=False,nticks=10, tickangle=90)
            #general_fig.update_yaxes(showgrid=False)
            st.text("Last updated: "+ (confirmedMM["Date"][-1:].to_string(index = False)))
            st.plotly_chart(general_fig, use_container_width=True)

        elif pc_user==False:
            #Mobile
            general_subplot = gridspec.GridSpec(3,3)
            wave_pie = plt.subplot(general_subplot[:,:])
            #wave_bar = plt.subplot(general_subplot[3:,:])
            #wave_pie = plt.subplot(general_subplot[2:,:1])
            #all_wave = plt.subplot(general_subplot[2:,1:])

            #region_pie_df = cov.groupby("Features Attributes Sr").sum()
            #region_pie_df.reset_index(inplace=True)
            #wedges, text = region_pie.pie(region_pie_df["Features Attributes Confirmed"], wedgeprops=dict(width=0.5), startangle=60, pctdistance=0.2)

            #region_pie.legend(region_pie_df["Features Attributes Sr"], loc=2)
            #plt.tight_layout()
            wave_pie.pie(x=counts, labels=contents,colors=["lightskyblue","cornflowerblue","mediumspringgreen","lightgreen","red","indianred"], textprops={'fontsize':'7.5'},
                         wedgeprops=dict(width=0.5),explode=[0,0,0,0,0.4,0.2],rotatelabels=False ,startangle=-45,autopct="%1.2f%%", pctdistance=0.83, labeldistance=0.95)
            #all_wave.plot(confirmedMM["Date"], confirmedMM["Cases"])
            #all_wave.plot(recoveredMM["Date"], recoveredMM["Cases"])
            #all_wave.plot(deathMM["Date"], deathMM["Cases"])
            st.text("Last updated: " + (confirmedMM["Date"][-1:].to_string(index=False)))
            st.pyplot()


#Analysis & Correlations

#gotta read these again fuck
covid_global = pd.read_csv(confirmed_url)
covid_global_grouped = covid_global.groupby("Country/Region").sum()
death_global = pd.read_csv(death_url)
death_global_grouped = death_global.groupby("Country/Region").sum()

#happiness report cleaing
happy = pd.read_csv("World Happiness Report 2020.csv")
droplist = ["Ladder score", "Standard error of ladder score", "upperwhisker",
            "lowerwhisker", "Dystopia + residual"]
happy.drop(droplist, axis=1, inplace=True)
happiness = happy.groupby("Country name").sum()

#countries list
countries = list(covid_global_grouped.index)
d_countries = list(death_global_grouped.index)

#get ready for incoming list of infection rate
max_infection_rates = []
max_death_rates = []

#fill those empty list! haha
for c in countries:
    max_infection_rates.append(covid_global_grouped.loc[c].diff().max())
for d in d_countries:
    max_death_rates.append(death_global_grouped.loc[d].diff().max())
    
#add list values to another column of dataframe
covid_global_grouped["Max infection rates"] = max_infection_rates
death_global_grouped["Max death rates"] = max_death_rates

#make simple dataframe, get rid of other columns
covid_max_infect = pd.DataFrame(covid_global_grouped["Max infection rates"])
covid_max_death = pd.DataFrame(death_global_grouped["Max death rates"])

#now kiss! i mean join two dataframes
corr_df = covid_max_infect.join(happiness, how="inner")
death_corr_df = covid_max_death.join(happiness, how="inner")

#rename for comfort
corr_df.rename(columns={"Logged GDP per capita":"GDP per capita(Economic output per person)"}, inplace=True)

#Let's gooooooo
st.header("Analysis & Correlations")
xaxis_select = st.selectbox("Choose: ", ["GDP per capita(Economic output per person)", "GDP per capita and Death rate", "Social support", "Healthy life expectancy","Generosity", "Conflict cases and Covid-19"])
if xaxis_select == "Conflict cases and Covid-19":
    conflict = pd.read_csv("conflict_data_mmr.csv")
    cc = conflict["event_date"].value_counts()
    cc = cc.to_frame(name="counts")
    cc.reset_index(inplace=True)
    cc.rename(columns={"index": "Date"}, inplace=True)
    cc.sort_values(by="Date", axis=0, inplace=True, ascending=False)
    cc = cc[:-1]
    cc["Date"] = pd.to_datetime(cc["Date"])
    confirmedMM["Date"] = pd.to_datetime(confirmedMM["Date"])
    conflict_cases = pd.merge(confirmedMM, cc, on="Date")
    conflict_cases["Date"] = conflict_cases["Date"].dt.strftime("%d/%m/%y")
    if pc_user==True:
        conflict_cases_fig = go.Figure()
        conflict_cases_fig.add_trace(
            go.Line(x=conflict_cases["Date"], y=np.log(conflict_cases["Cases"].diff()), name="Daily Covid-19 cases(Logged) "))
        conflict_cases_fig.add_trace(
            go.Line(x=conflict_cases["Date"], y=np.log(conflict_cases["counts"]), name="Daily conflict cases  "))
        conflict_cases_fig.layout.xaxis.fixedrange = True
        conflict_cases_fig.layout.yaxis.fixedrange = True
        conflict_cases_fig.update_xaxes(nticks=10, tickangle=45)
        conflict_cases_fig.update_yaxes(automargin=True)
        conflict_cases_fig.update_layout(legend=dict(orientation="h", yanchor="top", xanchor='center', x=0.5, y=1))

        st.write(conflict_cases_fig)

    elif pc_user==False:
    #Mobile
        conflict_cases_fig = plt.plot(conflict_cases["Date"], np.log(conflict_cases["Cases"].diff()), color="royalblue")
        conflict_cases_fig = plt.plot(conflict_cases["Date"], np.log(conflict_cases["counts"]), color="red")
        plt.xticks(ticks=conflict_cases["Date"][::20], rotation="vertical")
        #conflict_cases_fig.set_xticklabels(conflict_cases["Date"], size=6, rotation=90)
        plt.legend(["Daily Covid-19 cases(Logged)", "Daily conflict cases"])
        st.pyplot()

    st.markdown("#### According to the figure,")
    st.markdown("Generally, conflict rate stays the same regardless of Covid-19 infection rate.")
elif xaxis_select == "GDP per capita and Death rate":
    death_gdp_fig = sns.regplot(y=np.log(death_corr_df["Max death rates"]), x=death_corr_df["Logged GDP per capita"], scatter_kws={'alpha':0.5})
    death_gdp_fig.set_xlabel("GDP per capita(Economic output per person)", fontsize=9)
    death_gdp_fig.set_ylabel("Max death rates of countries", fontsize=9)
    st.markdown("Countries with higher GDP (More developed countries) have higher death rate due to Covid-19.")
    st.pyplot()
else:
    corr_fig = sns.regplot(y=np.log(corr_df["Max infection rates"]), x=corr_df[xaxis_select], scatter_kws={'alpha':0.5})
    corr_fig.set_xlabel(xaxis_select,fontsize=9)
    corr_fig.set_ylabel("Max infection rates of countries", fontsize=9)
    st.pyplot()
    st.markdown("#### According to the figure,")
    if xaxis_select=="GDP per capita(Economic output per person)":
        st.markdown("Countries with higher GDP (More developed countries) are more vulnerable to Covid-19.")
    elif xaxis_select=="Generosity":
        st.markdown("More generous countries are less vulnerable to Covid-19.")
    else:
        st.markdown("Countries with higher "+xaxis_select+" are more vulnerable to Covid-19.")


#function to set wide screen mode default
def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
#_max_width_()

port = int(os.environ.get("PORT", 5000))
app.run(debug=True, host='0.0.0.0', port=port)
