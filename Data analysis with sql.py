#!/usr/bin/env python
# coding: utf-8

# # SQL(Structured Query Language) for Data analysis using python

# The logic behind SQL is similar to any other tool or language that used for data analysis(excel,Pandas)and for those that used for work with data,should be very intuitive.

# In[1]:


# Importing necessary libraries


# In[1]:


import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


# In[2]:


conn = sqlite3.connect(r'C:\Users\hello\Desktop\db\database.sqlite')


# # First we see the tables we have

# In[3]:


df = pd.read_sql_query("SELECT *FROM Country",conn)


# In[4]:


df


# In[5]:


tables = pd.read_sql("SELECT * FROM sqlite_master WHERE type = 'table';",conn)


# In[6]:


tables


# # List of leagues and their country

# In[7]:


leagues = pd.read_sql('SELECT * FROM League',conn)


# In[8]:


leagues


# In[9]:


teams = pd.read_sql('select * from Team',conn)


# In[10]:


teams


# In[11]:


leagues = pd.read_sql('select * from league join Country ON Country.id = League.Country_id',conn)


# In[12]:


leagues


# # List of teams

# In[13]:


teams = pd.read_sql("""
                        select *
                        from Team 
                        order by team_long_name
                        LIMIT 10;""",conn)
teams


# # List of matches

# In[17]:


detailed_matches = pd.read_sql(""" SELECT Match.id,
                                    Country.name AS Country_name,
                                    League.name AS League_name,
                                    season,
                                    stage,
                                    date,
                                    HT.team_long_name AS home_team,
                                    AT.team_long_name AS away_team,
                                    home_team_goal,
                                    away_team_goal
                                FROM Match
                                JOIN Country on Country.id = Match.country_id
                                JOIN League on League.id = Match.league_id
                                LEFT JOIN Team AS HT ON HT.team_api_id = Match.home_team_api_id
                                LEFT JOIN Team AS AT ON HT.team_api_id = Match.away_team_api_id
                                WHERE country_name = 'Spain'
                                ORDER BY date
                                LIMIT 10;""",conn)


# In[18]:


detailed_matches


# # Now GROUP BY, that comes between the WHERE and ORDER BY
# 
# - Metrics -  all the metrics have to be aggregated using functions.The common functions are: sum(),count(),count(distinct),avg(),min(),max().

# In[26]:


leagues_by_season = pd.read_sql("""SELECT Country.name AS country_name,
                                    League.name AS league_name,
                                    season,
                                    count(distinct stage) AS number_of_stages,
                                    count(distinct HT.team_long_name) AS number_of_teams,
                                    avg(home_team_goal) AS avg_home_team_scores,
                                    avg(away_team_goal)AS avg_away_team_goals,
                                    avg(home_team_goal-away_team_goal) AS avg_goal_dif,
                                    avg(home_team_goal+away_team_goal) AS avg_goals,
                                    sum(home_team_goal+away_team_goal) AS total_goals
                                    FROM Match
                                    JOIN Country on Country.id = Match.country_id
                                    JOIN League on League.id = Match.League_id
                                    LEFT JOIN Team AS HT ON HT.team_api_id = Match.home_team_api_id
                                    LEFT JOIN Team AS AT ON AT.team_api_id = Match.away_team_api_id
                                    WHERE country_name in ('Spain','Germany','France','Italy','England')
                                    GROUP BY Country.name,League.name,season 
                                    HAVING count(distinct stage)>10
                                    ORDER BY Country.name,League.name,season DESC;""",conn)


# In[28]:


leagues_by_season


# #### Average Goals per Game over Time

# In[29]:



df = pd.DataFrame(index = np.sort(leagues_by_season['season'].unique()),columns = leagues_by_season['country_name'].unique())


df.loc[:,'Germany'] = list(leagues_by_season.loc[leagues_by_season['country_name']=='Germany','avg_goals'])
df.loc[:,'Spain'] = list(leagues_by_season.loc[leagues_by_season['country_name']=='Spain','avg_goals'])
df.loc[:,'France'] = list(leagues_by_season.loc[leagues_by_season['country_name']=='France','avg_goals'])
df.loc[:,'Italy'] = list(leagues_by_season.loc[leagues_by_season['country_name']=='Italy','avg_goals'])
df.loc[:,'England'] = list(leagues_by_season.loc[leagues_by_season['country_name']=='England','avg_goals'])


df.plot(figsize = (12,5),title = 'Average Goals per Game over time')


# In[30]:


df = pd.DataFrame(index = np.sort(leagues_by_season['season'].unique()),columns = leagues_by_season['country_name'].unique())


df.loc[:,'Germany'] = list(leagues_by_season.loc[leagues_by_season['country_name'] == 'Germany','avg_goal_dif'])
df.loc[:,'spain'] = list(leagues_by_season.loc[leagues_by_season['country_name'] == 'Spain','avg_goal_dif'])
df.loc[:,'France'] = list(leagues_by_season.loc[leagues_by_season['country_name'] == 'France','avg_goal_dif'])
df.loc[:,'Italy'] = list(leagues_by_season.loc[leagues_by_season['country_name'] == 'Italy','avg_goal_dif'])
df.loc[:,'England'] = list(leagues_by_season.loc[leagues_by_season['country_name'] == 'England','avg_goal_dif'])


df.plot(figsize = (12,5),title = 'Average Goal Difference Home vs Out')


# **Sub Queries and Functions**

# In[35]:


players_height = pd.read_sql("""SELECT CASE
                                        WHEN ROUND(height)<165 then 165
                                        WHEN ROUND(height)>195 then 195
                                        ELSE ROUND(height)
                                        END AS calc_height, 
                                        COUNT(height) AS distribution, 
                                        (avg(PA_Grouped.avg_overall_rating)) AS avg_overall_rating,
                                        (avg(PA_Grouped.avg_potential)) AS avg_potential,
                                        AVG(weight) AS avg_weight 
                            FROM PLAYER
                            LEFT JOIN (SELECT Player_Attributes.player_api_id, 
                                        avg(Player_Attributes.overall_rating) AS avg_overall_rating,
                                        avg(Player_Attributes.potential) AS avg_potential  
                                        FROM Player_Attributes
                                        GROUP BY Player_Attributes.player_api_id) 
                                        AS PA_Grouped ON PLAYER.player_api_id = PA_Grouped.player_api_id
                            GROUP BY calc_height
                            ORDER BY calc_height
                                ;""", conn)
players_height


# In[44]:


players_height.plot(x=['calc_height'],y=['avg_overall_rating'],figsize=(12,5),title='Potential vs Height')

