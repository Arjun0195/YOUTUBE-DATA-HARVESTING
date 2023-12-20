from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st


# In[5]:


def Api_connect():
    Api_Id="AIzaSyA-QJk_WiW7NwnETI4XQHSKHw3-GA4G6Bs"

    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube

youtube=Api_connect()


# In[6]:


def get_channel_info(channel_id):
    request=youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=channel_id
    )
    response=request.execute()

    for i in response['items']:
        data=dict(Channel_Name=i["snippet"]["title"],
                 Channel_Id=i["id"],
                 Subscribers=i["statistics"]["subscriberCount"],
                 Views=i["statistics"]["viewCount"],
                  Total_Videos=i["statistics"]["videoCount"],
                  Channel_Description=i["snippet"]["description"],
                  Playlist_Id=i["contentDetails"]["relatedPlaylists"]["uploads"])
    return data   

#90sGamerYT = UCumba4wLxQM6XWccbM_b9qg
#Harish hatricks = UCwFVXf0ymzz6QhlI-OeTBBA
#Hussain Manimegalai = UCQS9wN4pNfQ0VNHJRPqj2OQ
#Parattai Pugazh = UCjTlypR4Pu2SqLwYjxBO0Ug
#Kuraishi Vibes = UCJ6P61X1PyNHNEVJAib9O-w

# In[7]:

channel_details=get_channel_info("UCumba4wLxQM6XWccbM_b9qg")

# In[8]:


def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
                                    part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(
                                            part='snippet',
                                            playlistId=Playlist_Id,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

# In[9]:

video_ids=get_videos_ids('UCumba4wLxQM6XWccbM_b9qg')

# In[10]:

def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,ContentDetails,statistics",
            id=video_id
        )
        response=request.execute()

        for item in response["items"]:
            data=dict(Channel_Name=item['snippet']['channelTitle'],
                      channel_Id=item['snippet']['channelId'],
                      Video_Id=item['id'],
                      Title=item['snippet']['title'],
                      Tags=item['snippet'].get('tags'),
                      Thumbnail=item['snippet']['thumbnails']['default']['url'],
                      Description=item['snippet'].get('description'),
                      Published_date=item['snippet']['publishedAt'],
                      Duration=item['contentDetails']['duration'],
                      Views=item['statistics'].get('viewCount'),
                      Likes=item['statistics'].get('likeCount'),
                      Comments=item['statistics'].get('commentCount'),
                      Favorite_count=item['statistics']['favoriteCount'],
                      Definition=item['contentDetails']['definition'],
                      Caption_status=item['contentDetails']['caption']
                     )
            video_data.append(data)
    return video_data


video_details=get_video_info(video_ids)

# In[11]:


def get_comment_info(video_Ids):
    comment_data=[]
    try:
        for video_id in video_Ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId= video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(comment_Id=item['snippet']['topLevelComment']['id'],
                          video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                          Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                          Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                          Comment_published=item['snippet']['topLevelComment']['snippet']['publishedAt'])

                comment_data.append(data)

    except:
        pass
    return comment_data


comment_details=get_comment_info(video_ids)

# In[12]:


def get_playlist_details(channel_id):
        next_page_token=None
        All_data=[]
        while True:
                request=youtube.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()

                for item in response['items']:
                        data=dict(Playlist_Id=item['id'],
                                  Title=item['snippet']['title'],
                                  Channel_Id=item['snippet']['channelId'],
                                  Channel_Name=item['snippet']['channelTitle'],
                                  PublishedAt=item['snippet']['publishedAt'],
                                  Video_Count=item['contentDetails']['itemCount'])
                        All_data.append(data)

                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
        return All_data


playlist_details=get_playlist_details('UCumba4wLxQM6XWccbM_b9qg')    

# In[31]:


mongodb_url="mongodb://localhost:27017"
client=pymongo.MongoClient(mongodb_url)
db_name = "Youtube_Data" 
db = client[db_name]


# In[32]:


def channel_details(channel_id):
    ch_details=get_channel_info(channel_id)
    vi_ids=get_videos_ids(channel_id)
    vi_details=get_video_info(vi_ids)
    com_details=get_comment_info(vi_ids)
    pl_details=get_playlist_details(channel_id)
    
    
    coll1=db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,
                     "viedo_information":vi_details,"comment_information":com_details})
    
    return "upload completed successfully"

insert=channel_details("UCumba4wLxQM6XWccbM_b9qg")


# In[34]:


def channels_table():
    mydb=psycopg2.connect(host="localhost",
                          user="postgres",
                          password="Arjun@18",
                          database="youtube_data",
                          port="5432")
    cursor=mydb.cursor()

    drop_query='''drop table if exists channels'''
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query='''create table if not exists channels(Channel_Name varchar(100),
                                                            Channel_Id varchar(80) primary key,
                                                            Subscribers bigint,
                                                            Views bigint,
                                                            Total_Videos int,
                                                            Channel_Description text,
                                                            Playlist_Id varchar(80))'''

        cursor.execute(create_query)
        mydb.commit()
    except:
        print("channels table already created")


    ch_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=pd.DataFrame(ch_list)   




    for index,row in df.iterrows():
        insert_query='''insert into channels(Channel_Name,
                                             Channel_Id,
                                             Subscribers,
                                             Views,
                                             Total_Videos,
                                             Channel_Description,
                                             Playlist_Id)

                                             values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Channel_Id'],
                row['Subscribers'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Playlist_Id'])

        try:
            cursor.execute(insert_query,values)
            mydb.commit()

        except:
            print("channels values are already inserted")


# In[35]:


def playlist_table():
    mydb=psycopg2.connect(host="localhost",
                          user="postgres",
                          password="Arjun@18",
                          database="youtube_data",
                          port="5432")
    cursor=mydb.cursor()

    drop_query='''drop table if exists playlists'''
    cursor.execute(drop_query)
    mydb.commit()


    create_query='''create table if not exists playlists(Playlist_Id varchar(100)primary key,
                                                            Title varchar(100),
                                                            Channel_Id varchar(100),
                                                            Channel_Name varchar(100),
                                                            PublishedAt timestamp,
                                                            Video_Count int)'''



    cursor.execute(create_query)
    mydb.commit()

    
    pl_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
            pl_list.append(pl_data["playlist_information"][i])
    df1=pd.DataFrame(pl_list)
    
    for index,row in df1.iterrows():
        insert_query='''insert into playlists(Playlist_Id,
                                             Title,
                                             Channel_Id,
                                             Channel_Name,
                                             PublishedAt,
                                             Video_Count
                                             )

                                             values(%s,%s,%s,%s,%s,%s)'''
        values=(row['Playlist_Id'],
                row['Title'],
                row['Channel_Id'],
                row['Channel_Name'],
                row['PublishedAt'],
                row['Video_Count'])
                

        
        cursor.execute(insert_query,values)
        mydb.commit()


# In[36]:


def videos_table():
    mydb=psycopg2.connect(host="localhost",
                          user="postgres",
                          password="Arjun@18",
                          database="youtube_data",
                          port="5432")
    cursor=mydb.cursor()

    drop_query='''drop table if exists videos'''
    cursor.execute(drop_query)
    mydb.commit()


    create_query='''create table if not exists videos(Channel_Name varchar(100),
                                                      channel_Id varchar(100),
                                                      Video_Id varchar(30) primary key,
                                                      Title varchar(150),
                                                      Tags text,
                                                      Thumbnail varchar(250),
                                                      Description text,
                                                      Published_date timestamp,
                                                      Duration interval,
                                                      Views bigint,
                                                      Likes bigint,
                                                      Comments int,
                                                      Favorite_count int,
                                                      Definition varchar(10),
                                                      Caption_status varchar(50)
                                                      )'''



    cursor.execute(create_query)
    mydb.commit()


    vi_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"viedo_information":1}):
        for i in range(len(vi_data["viedo_information"])):
            vi_list.append(vi_data["viedo_information"][i])
    df2=pd.DataFrame(vi_list)


    for index,row in df2.iterrows():
            insert_query='''insert into videos(Channel_Name,
                                                  channel_Id,
                                                  Video_Id,
                                                  Title,
                                                  Tags,
                                                  Thumbnail,
                                                  Description,
                                                  Published_date,
                                                  Duration,
                                                  Views,
                                                  Likes,
                                                  Comments,
                                                  Favorite_count,
                                                  Definition,
                                                  Caption_status
                                                 )

                                                 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            values=(row['Channel_Name'],
                    row['channel_Id'],
                    row['Video_Id'],
                    row['Title'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_count'],
                    row['Definition'],
                    row['Caption_status']
                   )



            cursor.execute(insert_query,values)
            mydb.commit()


# In[37]:


def comments_table():
    mydb=psycopg2.connect(host="localhost",
                          user="postgres",
                          password="Arjun@18",
                          database="youtube_data",
                          port="5432")
    cursor=mydb.cursor()

    drop_query='''drop table if exists comments'''
    cursor.execute(drop_query)
    mydb.commit()


    create_query='''create table if not exists comments(comment_Id varchar(100) primary key,
                                                        video_Id varchar(50),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_published timestamp
                                                        )'''



    cursor.execute(create_query)
    mydb.commit()


    com_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3=pd.DataFrame(com_list)


    for index,row in df3.iterrows():
            insert_query='''insert into comments(comment_Id,
                                                 video_Id,
                                                 Comment_Text,
                                                 Comment_Author,
                                                 Comment_published
                                                )

                                                 values(%s,%s,%s,%s,%s)'''
            values=(row['comment_Id'],
                    row['video_Id'],
                    row['Comment_Text'],
                    row['Comment_Author'],
                    row['Comment_published']
                   )



            cursor.execute(insert_query,values)
            mydb.commit()


# In[38]:


def tables():
    channels_table()
    playlist_table()
    videos_table()
    comments_table()
    
    return "Tables created successfully"


# In[39]:


Tables=tables()


# In[40]:


Tables


# In[41]:


def show_channels_table():
    ch_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)
    
    return df


# In[42]:


def show_playlist_table():
    pl_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
            pl_list.append(pl_data["playlist_information"][i])
    df1=st.dataframe(pl_list)
    
    return df1


# In[43]:


def show_videos_table(): 
    vi_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"viedo_information":1}):
        for i in range(len(vi_data["viedo_information"])):
            vi_list.append(vi_data["viedo_information"][i])
    df2=st.dataframe(vi_list)
    
    return df2


# In[44]:


def show_comments_table():
    com_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3=st.dataframe(com_list)
    
    return df3


# In[46]:


with st.sidebar:
    st.title(":purple[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("Skill Take Away")
    st.caption("Python Scripting")
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("API Intergration")
    st.caption("Data Management using MongoDB and SQL")
    
channel_id=st.text_input("Enter the channel ID")    

if st.button("collect and store data"):
    ch_ids=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])
        
    if channel_id in ch_ids:
        st.success("Channel Details of the given channel id already exists")
        
    else:
        insert=channel_details(channel_id)
        st.success(insert)
        
if st.button("Migrate to sql"):
    Table=tables()
    st.success(Table)
    
show_table=st.radio("SELECT THE TABLE FOR VIEW",("CHANNELS","PLAYLISTS","VIDEOS","COMMENTS"))

if show_table=="CHANNELS":
    show_channels_table()
    
elif show_table=="PLAYLISTS":    
    show_playlist_table() 
    
elif show_table=="VIDEOS":    
    show_videos_table()    

elif show_table=="COMMENTS":    
    show_comments_table()


# In[47]:


mydb=psycopg2.connect(host="localhost",
                      user="postgres",
                      password="Arjun@18",
                      database="youtube_data",
                      port="5432")
cursor=mydb.cursor()

question=st.selectbox("Select your question",("1. What are the names of all the videos and their corresponding channels",
                                              "2. Which channels have the most number of videos, and how many videos dothey have",
                                              "3. What are the top 10 most viewed videos and their respective channels",
                                              "4. How many comments were made on each video, and what are their corresponding video names",
                                              "5. Which videos have the highest number of likes, and what are their corresponding channel names",
                                              "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names",
                                              "7. What is the total number of views for each channel, and what are their corresponding channel names", 
                                              "8. What are the names of all the channels that have published videos in the year 2022",
                                              "9. What is the average duration of all videos in each channel, and what are their corresponding channel names", 
                                              "10. Which videos have the highest number of comments, and what are their corresponding channel names")) 

if question=="1. What are the names of all the videos and their corresponding channels":
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=["video title","channel name"])
    st.write(df)
    
    
elif question=="2. Which channels have the most number of videos, and how many videos dothey have":
    query2='''select channel_name as channelname,total_videos as no_videos from channels
                order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of videos"])
    st.write(df2)
    
elif question=="3. What are the top 10 most viewed videos and their respective channels":
    query3='''select views as views,channel_name as channelname,title as videotitle from videos
                where views is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    st.write(df3)
    
elif question=="4. How many comments were made on each video, and what are their corresponding video names":
    query4='''select comments as no_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no comments","videotitle"])
    st.write(df4)
    
elif question=="5. Which videos have the highest number of likes, and what are their corresponding channel names":
    query5='''select title as videotitle,channel_name as channelname,Likes as likecount
                from videos where likes is not null order by Likes desc'''
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","channelname","likecount"])
    st.write(df5)   
    
elif question=="6. What is the total number of likes and dislikes for each video, and what are their corresponding video names":
    query6='''select Likes as likecount,title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    st.write(df6)
    
elif question=="7. What is the total number of views for each channel, and what are their corresponding channel names":
    query7='''select channel_name as channel name ,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["channel name","totalviews"])
    st.write(df7)
    
elif question=="8. What are the names of all the channels that have published videos in the year 2022":
    query8='''select title as video_title , published_date as videorelease ,channel_name as channlname from videos'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["videotitle","published_date","channelname"])
    st.write(df8)
    
elif question=="9. What is the average duration of all videos in each channel, and what are their corresponding channel names":
    query9='''select channel_name as channelname ,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration",])
    T9=[]
    for index,row in df9.iterrows():
        channel_title=row["channelname"]
        average_duration=row["averageduration"]
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle=channel_title, avgduration=average_duration_str))
    df9=pd.DataFrame(T9)
    st.write(df9)
    
elif question=="10. Which videos have the highest number of comments, and what are their corresponding channel names":
    query10='''select title as video_title ,channel_name as channlname ,comments as comments from videos
                where comments is not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["videotitle","channelname","comments"])
    st.write(df10)

