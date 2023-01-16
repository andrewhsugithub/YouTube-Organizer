from tkinter import *
from tkinter import ttk
import re
import pandas as pd
from Google import Create_Service

CLIENT_SECRET_FILE = 'client_secret_youtube_api.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

root = Tk()
root.title('YouTube Helper')
root.geometry("1200x800")

your_pl, pl_vid = {}, []
pl_vid1 = {}
pl_titles, vid_titles = {}, {}
pl_title, pl_id = "", ""
vid_title, vid_id, pl_item_id = "", "", ""
add_pl_id_pl, add_pl_id_vid = "", ""
'''
your_pl = {
   'pl_id' = ['title','add pl id','pos','create pl title', 'remove','pl_url']
}
pl_vid indices: vidId, plItemid, title, url, duration, views, owner, published, likes

show[10(11)]: title, url, duration, views, owner, (owner_url), published, likes
'''


def get_user_playlist():
    response = service.playlists().list(
        part="snippet,contentDetails",
        maxResults=50,
        mine=True
    ).execute()

    channelItems_pl = response['items']
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            mine=True,
            pageToken=nextPageToken
        ).execute()

        channelItems_pl.extend(response['items'])
        nextPageToken = response.get('nextPageToken')

    your_pl.clear()
    for item in channelItems_pl:
        your_pl[item['id']] = [item['snippet']['title']]
        pl_titles[item['snippet']['title']] = item['id']


def get_playlist_vid(pl_id):
    response = service.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=pl_id,
        maxResults=50
    ).execute()
    playlistItems = response['items']
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=pl_id,
            maxResults=50,
            pageToken=nextPageToken
        ).execute()

        playlistItems.extend(response['items'])
        nextPageToken = response.get('nextPageToken')

    pl_vid.clear()

    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')

    for item in playlistItems:
        vidId = item['contentDetails'].get('videoId')
        pl_item_id = item['id']
        pos = item['snippet'].get('position')
        title = item['snippet'].get('title')
        url = f'https://youtu.be/{vidId}'
        published = item['contentDetails'].get('videoPublishedAt')
        owner = item['snippet'].get('videoOwnerChannelTitle')
        owner_url = item['snippet'].get('videoOwnerChannelId')

        vid_response = service.videos().list(
            part='contentDetails,statistics',
            id=vidId
        ).execute()
        vid_item = vid_response['items'][0]
        time = vid_item['contentDetails'].get('duration')
        hours = hours_pattern.search(time)
        minutes = minutes_pattern.search(time)
        seconds = seconds_pattern.search(time)
        hours = hours.group(1) if hours else "00"
        minutes = minutes.group(1) if minutes else "00"
        seconds = seconds.group(1) if seconds else "00"
        hours = hours if int(hours)//10 != 0 or hours == "00" else "0"+hours
        minutes = minutes if int(
            minutes)//10 != 0 or minutes == "00" else "0"+minutes
        seconds = seconds if int(
            seconds)//10 != 0 or seconds == "00" else "0"+seconds
        if hours == "00" and minutes == "00":
            time = f'{seconds}'
        elif hours == "00":
            time = f'{minutes}:{seconds}'
        else:
            time = f'{hours}:{minutes}:{seconds}'
        views = vid_item['statistics'].get('viewCount')
        views = f'{int(views):,}'
        likes = vid_item['statistics'].get('likeCount')
        likes = f'{int(likes):,}'
        pl_vid.append([vidId, pl_item_id, pos, title,
                      url, time, views, owner, published, likes])
        pl_vid1[vidId] = [title, pl_item_id, pos,
                          url, time, views, owner, published, likes]
        vid_titles[title] = [vidId, pl_item_id]


def select_record_pl(event):
    global pl_title, pl_id
    title_box.delete(0, END)
    url_box.delete(0, END)
    create_pl.delete(0, END)
    insert_pl.delete(0, END)
    remove_pl_var.set(0)
    clear_pl_var.set(0)
    selected = tree_pl.focus()
    values = tree_pl.item(selected, 'values')
    chooseTitle.set('Don\'t Add')
    pl_title = values[0]
    title_box.insert(0, values[0])
    url_box.insert(0, values[1])
    create_pl.insert(0, 'Enter Title')
    insert_pl.insert(
        0, 'Enter the playlist URL you want to add to your playlist')

    pl_id_pattern = re.compile(r'list=([^&]+)')
    pl_id = pl_id_pattern.search(values[1])
    pl_id = pl_id.group(0)[5:]
    get_playlist_vid(pl_id)

    hide_all_frames()

    global tree_vid
    tree_vid = ttk.Treeview(vid_frame, height=4)
    tree_vid.pack(fill='x')
    tree_vid['columns'] = ("Title", "URL", "Duration",
                           "Views", "Owner", "Published Date", "Likes")
    tree_vid['show'] = "headings"
    tree_vid.heading("Title", text="Title")
    tree_vid.heading("URL", text="URL")
    tree_vid.heading("Duration", text="Duration")
    tree_vid.heading("Views", text="Views")
    tree_vid.heading("Owner", text="Owner")
    tree_vid.heading("Published Date", text="Published Date")
    tree_vid.heading("Likes", text="Likes")

    vid_count = 0
    for record in pl_vid:
        tree_vid.insert(parent='', index='end', iid=vid_count, text="", values=(
            record[3], record[4], record[5], record[6], record[7], record[8], record[9]))
        vid_count += 1

    global vid_option_frame
    vid_option_frame = Frame(vid_frame)
    vid_option_frame.pack(pady=20)
    title_vid_lb = Label(vid_option_frame, text="Title")
    title_vid_lb.grid(row=0, column=0)
    url_vid_lb = Label(vid_option_frame, text="URL")
    url_vid_lb.grid(row=0, column=1, columnspan=2)
    title_vid_box = Entry(vid_option_frame, width=20)
    title_vid_box.grid(row=1, column=0)
    url_vid_box = Entry(vid_option_frame, width=50)
    url_vid_box.grid(row=1, column=1, columnspan=2)

    duration_lb = Label(vid_option_frame, text="Duration")
    duration_lb.grid(row=2, column=0)
    views_lb = Label(vid_option_frame, text="Views")
    views_lb.grid(row=2, column=1)
    likes_lb = Label(vid_option_frame, text="Likes")
    likes_lb.grid(row=2, column=2)
    duration_box = Entry(vid_option_frame, width=20)
    duration_box.grid(row=3, column=0)
    views_box = Entry(vid_option_frame, width=20)
    views_box.grid(row=3, column=1)
    likes_box = Entry(vid_option_frame, width=20)
    likes_box.grid(row=3, column=2)

    owner_lb = Label(vid_option_frame, text="Owner")
    owner_lb.grid(row=4, column=0)
    date_lb = Label(vid_option_frame, text="Published Date")
    date_lb.grid(row=4, column=1, columnspan=2)
    owner_box = Entry(vid_option_frame, width=20)
    owner_box.grid(row=5, column=0)
    date_box = Entry(vid_option_frame, width=50)
    date_box.grid(row=5, column=1, columnspan=2)

    # add to playlist
    add_to_lb = Label(vid_option_frame, text="Add current video to :",
                      font=("Times New Roman", 10)).grid(pady=10, row=6, column=0, columnspan=2)

    global choosePl
    choosePl = ttk.Combobox(
        vid_option_frame, state="readonly", postcommand=lambda: update_combobox(choosePl))
    choosePl.bind('<<ComboboxSelected>>', clicked_vid)
    choosePl.grid(pady=10, row=6, column=1, columnspan=2)
    # remove vid
    global remove_vid_var
    remove_vid_var = IntVar()
    remove_vid = Checkbutton(vid_option_frame, text='Remove Video',
                             variable=remove_vid_var).grid(row=7, column=0, columnspan=2)
    # remove dup
    global remove_dup_var
    remove_dup_var = IntVar()
    remove_dup = Checkbutton(vid_option_frame, text='Remove Duplicates',
                             variable=remove_dup_var).grid(row=7, column=1, columnspan=2)
    # insert video
    insert_vid_lb = Label(vid_option_frame, text="Insert video url :",
                          font=("Times New Roman", 10)).grid(row=8, column=0)
    insert_vid = Entry(vid_option_frame, width=50)
    insert_vid.grid(pady=10, row=8, column=1, columnspan=2)
    insert_vid.insert(
        0, 'Enter the video URL you want to add to your playlist')
    # move
    move_up = Button(vid_option_frame, text='Move Up', command=up).grid(
        pady=5, row=9, column=0, columnspan=2)
    move_down = Button(vid_option_frame, text='Move Down', command=down).grid(
        pady=5, row=9, column=1, columnspan=2)
    # search
    search_vid_lb = Label(vid_option_frame, text="Search / Find : ",
                          font=("Times New Roman", 10)).grid(pady=5, padx=5, row=10, column=0)
    search_vid = Entry(vid_option_frame, width=15)
    search_vid.grid(pady=5, row=10, column=1)
    search_vid.bind("<KeyRelease>", lambda event, x=search_vid,
                    tree=tree_vid, frame=vid_option_frame: search(event, x, tree, frame, 10, 2))
    # regex search
    research_vid_lb = Label(vid_option_frame, text="Regex Search : ",
                            font=("Times New Roman", 10)).grid(pady=5, padx=5, row=11, column=0)
    research_vid = Entry(vid_option_frame, width=15)
    research_vid.grid(row=11, column=1)
    research_vid.bind("<KeyRelease>", lambda event, x=research_vid,
                      tree=tree_vid, frame=vid_option_frame: re_search(event, x, tree, frame, 11, 2))
    # refresh
    refresh_v = Button(vid_option_frame, text='Refresh', command=refresh_vid).grid(pady=5,
                                                                                   row=12, columnspan=3)
    # save record
    save_action = Button(vid_option_frame, text='Save Changes and Update',
                         command=lambda k=insert_vid: update_vid(k)).grid(pady=5, row=13, columnspan=3)

    tree_vid.bind("<ButtonRelease-1>", lambda event, a=title_vid_box, b=url_vid_box, c=duration_box,
                  d=views_box, e=likes_box, f=owner_box, g=date_box, h=choosePl, k=insert_vid, l=search_vid, m=research_vid: select_record_vid(event, a, b, c, d, e, f, g, h, k, l, m))


def select_record_vid(event, title_vid_box, url_vid_box, duration_box, views_box, likes_box, owner_box, date_box, choosePl, insert_vid, search_vid, research_vid):
    global vid_curr_pos, vid_id
    title_vid_box.delete(0, END)
    url_vid_box.delete(0, END)
    duration_box.delete(0, END)
    views_box.delete(0, END)
    likes_box.delete(0, END)
    owner_box.delete(0, END)
    date_box.delete(0, END)
    insert_vid.delete(0, END)
    search_vid.delete(0, END)
    research_vid.delete(0, END)
    remove_vid_var.set(0)
    remove_dup_var.set(0)
    choosePl.set('Don\'t Add')

    selected = tree_vid.focus()
    val = tree_vid.item(selected, 'values')

    vid_curr_pos = val[0]
    title_vid_box.insert(0, val[0])
    url_vid_box.insert(0, val[1])
    duration_box.insert(0, val[2])
    views_box.insert(0, val[3])
    owner_box.insert(0, val[4])
    date_box.insert(0, val[5])
    likes_box.insert(0, val[6])
    insert_vid.insert(
        0, 'Enter the video URL you want to add to your playlist')

    vid_id_pattern = re.compile(r'be/([^&]+)')
    vid_id = vid_id_pattern.search(val[1])
    vid_id = vid_id.group(0)[3:]


def hide_all_frames():
    for widget in vid_frame.winfo_children():
        widget.destroy()
    # vid_frame.pack_forget()


def clicked_pl(event):  # click combobox
    global add_pl_id_pl
    add_pl_title = event.widget.get()
    if add_pl_title == "Don\'t Add":
        add_pl_id_pl = ""
        return
    add_pl_id_pl = pl_titles[add_pl_title]


def clicked_vid(event):  # click combobox
    global add_pl_id_vid
    add_pl_title = event.widget.get()
    if add_pl_title == "Don\'t Add":
        add_pl_id_vid = ""
        return
    add_pl_id_vid = pl_titles[add_pl_title]


def up():
    global pl_id, vid_id
    service.playlistItems().update(
        part="snippet",
        body={
            "id": pl_vid1[vid_id][1],
            "snippet": {
                "playlistId": pl_id,
                "position": pl_vid1[vid_id][2]-1,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": vid_id
                }
            }
        }
    ).execute()
    row = tree_vid.focus()
    tree_vid.move(row, tree_vid.parent(row), tree_vid.index(row)-1)


def down():
    global pl_id, vid_id
    service.playlistItems().update(
        part="snippet",
        body={
            "id": pl_vid1[vid_id][1],
            "snippet": {
                "playlistId": pl_id,
                "position": pl_vid1[vid_id][2]+1,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": vid_id
                }
            }
        }
    ).execute()
    row = tree_vid.focus()
    tree_vid.move(row, tree_vid.parent(row), tree_vid.index(row)+1)


def search(event, search, tree, frame, r, c):
    string = search.get()
    tree.tag_configure('found', background='#FFFBCC')
    flag = False
    found = 0
    for child in tree.get_children():
        for val in tree.item(child)["values"]:
            if string.lower() in str(val).lower() and string.strip() != "":
                flag = True
                break
        if flag:
            tree.item(child, tags=('found'))
            found += 1
            flag = False
        else:
            tree.item(child, tags=())
    Label(frame, text="Found : "+str(found)).grid(row=r, column=c)


def re_search(event, pattern, tree, frame, r, c):
    pattern = pattern.get().strip()
    try:
        regex_pattern = re.compile(fr'{pattern}')
    except re.error:
        return
    tree.tag_configure('found', background='lightblue')
    flag = False
    found = 0
    for child in tree.get_children():
        for val in tree.item(child)["values"]:
            if regex_pattern.search(str(val)) and pattern != "":
                flag = True
                break
        if flag:
            tree.item(child, tags=('found'))
            found += 1
            flag = False
        else:
            tree.item(child, tags=())
    Label(frame, text="Found : "+str(found)).grid(row=r, column=c)


def refresh_pl():
    get_user_playlist()
    tree_pl.delete(*tree_pl.get_children())
    pl_count = 0
    for record in your_pl:
        tree_pl.insert(parent='', index='end', iid=pl_count, text="", values=(
            your_pl[record][0], f'https://www.youtube.com/playlist?list={record}'))
        pl_count += 1
    refresh = Label(pl_option_frame, text='Refreshed/Updated')
    refresh.grid(row=10, columnspan=3)
    pl_option_frame.after(2000, refresh.destroy)


def refresh_vid():
    global pl_id
    get_playlist_vid(pl_id)
    tree_vid.delete(*tree_vid.get_children())
    vid_count = 0
    for record in pl_vid:
        tree_vid.insert(parent='', index='end', iid=vid_count, text="", values=(
            record[3], record[4], record[5], record[6], record[7], record[8], record[9]))
        vid_count += 1
    refresh = Label(vid_option_frame, text='Refreshed/Updated')
    refresh.grid(row=14, columnspan=3)
    vid_option_frame.after(2000, refresh.destroy)

    for child in vid_option_frame.winfo_children():
        if child.winfo_class() == 'Entry':
            child.delete(0, END)
        elif child.winfo_class() == 'ComboBox':
            child.set('Don\'t Add')
    remove_vid_var.set(0)
    remove_dup_var.set(0)


def update_pl():
    global pl_id, pl_title, add_pl_id_pl
    add_pl = add_pl_id_pl
    if add_pl != "":
        response = service.playlistItems().list(part='contentDetails',
                                                playlistId=pl_id, maxResults=50).execute()

        playlistItems = response['items']
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.playlistItems().list(part='contentDetails',
                                                    playlistId=pl_id, maxResults=50, pageToken=nextPageToken).execute()
            playlistItems.extend(response['items'])
            nextPageToken = response.get('nextPageToken')

        for video in playlistItems:
            request_body = {
                'snippet': {
                    'playlistId': add_pl,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video['contentDetails']['videoId']
                    }
                }
            }

            service.playlistItems().insert(
                part='snippet',
                body=request_body
            ).execute()
            add_pl_id_pl = ""
    create_pl_title = create_pl.get()
    if create_pl_title != "Enter Title":
        response = service.playlists().insert(
            part='snippet',
            body={
                "snippet": {
                    "title": create_pl_title
                }
            }
        ).execute()
    remove_flag = remove_pl_var.get()
    if remove_flag == 1:
        service.playlists().delete(id=pl_id).execute()
    clear_flag = clear_pl_var.get()
    if clear_flag == 1:
        response = service.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=pl_id,
            maxResults=50
        ).execute()

        playlistItems = response['items']
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=pl_id,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()

            playlistItems.extend(response['items'])
            nextPageToken = response.get('nextPageToken')

        for item in playlistItems:
            service.playlistItems().delete(id=item['id']).execute()
    insert_pl_url = insert_pl.get()
    if insert_pl_url != "Enter the playlist URL you want to add to your playlist":
        url_id_pattern = re.compile(r'list=([^&]+)')
        url_id = url_id_pattern.search(insert_pl_url)
        url_id = url_id.group(0)[5:]

        response = service.playlistItems().list(part='contentDetails',
                                                playlistId=url_id, maxResults=50).execute()

        playlistItems = response['items']
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.playlistItems().list(part='contentDetails',
                                                    playlistId=url_id, maxResults=50, pageToken=nextPageToken).execute()
            playlistItems.extend(response['items'])
            nextPageToken = response.get('nextPageToken')

        for video in playlistItems:
            request_body = {
                'snippet': {
                    'playlistId': pl_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video['contentDetails']['videoId']
                    }
                }
            }

            service.playlistItems().insert(
                part='snippet',
                body=request_body
            ).execute()

    refresh_pl()


def update_vid(insert_vid):
    global add_pl_id_vid, vid_id, pl_id
    add_pl = add_pl_id_vid
    if add_pl != "":
        request_body = {
            'snippet': {
                'playlistId': add_pl,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': vid_id
                }
            }
        }

        service.playlistItems().insert(
            part='snippet',
            body=request_body
        ).execute()
        add_pl_id_vid = ""
    remove_flag = remove_vid_var.get()
    if remove_flag == 1:
        service.playlistItems().delete(id=pl_vid1[vid_id][1]).execute()
    dup_flag = remove_dup_var.get()
    if dup_flag == 1:
        response = service.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=pl_id,
            maxResults=50
        ).execute()

        playlistItems = response['items']
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=pl_id,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()

            playlistItems.extend(response['items'])
            nextPageToken = response.get('nextPageToken')

        df_playlistItems = pd.DataFrame(playlistItems)
        df_contentDetails = df_playlistItems['contentDetails'].apply(pd.Series)

        for videoItem in df_playlistItems[df_contentDetails.duplicated()].iterrows():
            service.playlistItems().delete(id=videoItem[1]['id']).execute()
    insert_vid_url = insert_vid.get()
    if insert_vid_url != "Enter the video URL you want to add to your playlist":
        url_id_pattern = re.compile(r'be/([^&]+)')
        url_id = url_id_pattern.search(insert_vid_url)
        url_id = url_id.group(0)[3:]
        request_body = {
            'snippet': {
                'playlistId': pl_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': url_id
                }
            }
        }

        service.playlistItems().insert(
            part='snippet',
            body=request_body
        ).execute()

    refresh_vid()


def update_combobox(box):
    value_pl = [your_pl[key][0] for key in list(your_pl.keys())]
    value_pl.append('Don\'t Add')
    box['values'] = value_pl
    box.current(len(value_pl)-1)


get_user_playlist()

pl_frame = LabelFrame(root, text='Your Playlists')
pl_frame.pack(fill='both', padx=20, pady=10, side=LEFT)
tree_pl = ttk.Treeview(pl_frame)
tree_pl.pack(fill='x')
tree_pl['columns'] = ("Title", "URL")
tree_pl['show'] = "headings"
tree_pl.column("Title", anchor=CENTER, width=50)
tree_pl.column("URL", width=200)
tree_pl.heading("Title", text="Title", anchor=CENTER)
tree_pl.heading("URL", text="URL")
tree_pl.bind("<ButtonRelease-1>", select_record_pl)

pl_count = 0
for record in your_pl:
    tree_pl.insert(parent='', index='end', iid=pl_count, text="", values=(
        your_pl[record][0], f'https://www.youtube.com/playlist?list={record}'))
    pl_count += 1

# show selected
pl_option_frame = Frame(pl_frame)
pl_option_frame.pack(pady=20)
title_lb = Label(pl_option_frame, text="Title")
title_lb.grid(row=0, column=0)
url_lb = Label(pl_option_frame, text="URL")
url_lb.grid(row=0, column=1, columnspan=2)
title_box = Entry(pl_option_frame, width=20)
title_box.grid(row=1, column=0)
url_box = Entry(pl_option_frame, width=50)
url_box.grid(row=1, column=1, columnspan=2)
# add to playlist
add_to_lb = Label(pl_option_frame, text="Add current playlist to :",
                  font=("Times New Roman", 10)).grid(row=2, column=0)

chooseTitle = ttk.Combobox(
    pl_option_frame, state="readonly", postcommand=lambda: update_combobox(chooseTitle))
# value_pl = [your_pl[key][0] for key in list(your_pl.keys())]
# value_pl.append('Don\'t Add')
# chooseTitle['values'] = value_pl
# chooseTitle.current(len(value_pl)-1)
chooseTitle.bind('<<ComboboxSelected>>', clicked_pl)
chooseTitle.grid(pady=10, row=2, column=1)
# create a new playlist
create_pl_lb = Label(pl_option_frame, text="Create playlist :",
                     font=("Times New Roman", 10)).grid(pady=10, row=3, column=0)
create_pl = Entry(pl_option_frame, width=50)
create_pl.grid(pady=10, row=3, column=1, columnspan=2)
create_pl.insert(0, 'Enter Title')
# remove playlist
remove_pl_var = IntVar()
remove_pl = Checkbutton(pl_option_frame, text='Remove Playlist',
                        variable=remove_pl_var).grid(row=4, column=0, columnspan=2)
# clear playlist
clear_pl_var = IntVar()
clear_pl = Checkbutton(pl_option_frame, text='Clear Playlist',
                       variable=clear_pl_var).grid(row=4, column=1, columnspan=2)
# insert playlist
insert_pl_lb = Label(pl_option_frame, text="Insert playlist url :",
                     font=("Times New Roman", 10)).grid(pady=10, row=5, column=0)
insert_pl = Entry(pl_option_frame, width=50)
insert_pl.grid(pady=10, row=5, column=1, columnspan=2)
insert_pl.insert(
    0, 'Enter the playlist URL you want to add to your playlist')
# search
search_vid_lb = Label(pl_option_frame, text="Search / Find : ",
                      font=("Times New Roman", 10)).grid(pady=5, padx=5, row=6, column=0)
search_vid = Entry(pl_option_frame, width=15)
search_vid.grid(pady=5, row=6, column=1)
search_vid.bind("<KeyRelease>", lambda event, x=search_vid,
                tree=tree_pl, frame=pl_option_frame: search(event, x, tree, frame, 6, 2))
# regex search
research_vid_lb = Label(pl_option_frame, text="Regex Search : ",
                        font=("Times New Roman", 10)).grid(pady=5, padx=5, row=7, column=0)
research_vid = Entry(pl_option_frame, width=15)
research_vid.grid(row=7, column=1)
research_vid.bind("<KeyRelease>", lambda event, x=research_vid,
                  tree=tree_pl, frame=pl_option_frame: re_search(event, x, tree, frame, 7, 2))
# refresh
refresh_action = Button(
    pl_option_frame, text='Refresh', command=refresh_pl).grid(pady=5, row=8, columnspan=3)
# save record
save_action = Button(
    pl_option_frame, text='Save Changes and Update', command=update_pl).grid(pady=5, row=9, columnspan=3)
vid_frame = LabelFrame(root, text='Videos in playlist')
vid_frame.pack(fill='both', expand=1, padx=20, pady=10, side=LEFT)
root.mainloop()
