"""
* Author  : pk
* Use     : A simple python script to show streams available from r/soccerstreams subreddit

Ref links :
1 https://stackoverflow.com/questions/15705745/how-to-fit-tkinter-listbox-to-contents

"""
import json
import re
import time
import webbrowser
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import font
import threading

import requests

# tkinter setup
root = Tk()
font_fam='Verdana'
root.option_add("*Label.Font", font_fam+" 11")
root.option_add("*Button.Font", font_fam+" 10")
root.title('Watch Soccer')
root.iconbitmap("soccer.ico")
root.geometry("600x500")
medium_font = font.Font(size=10, family=font_fam)

# function to open a particular stream
def open_stream(stream):
    open_link_incognito(stream)


def get_match_streams(match):
    match_url = match['data']['url']
    match_url = match_url[:-1]+'.json'  # adding .json to get back json response

    response = get_json_response(match_url)

    comments = response[1]
    comments = comments['data']['children']
    streams = {}
    for comment in comments:
        comment_body = comment['data']['body']
        link_names = re.findall('\[.*?]\(', comment_body)
        links = re.findall('\(.*?\) ', comment_body)
        for link, link_name in zip(links, link_names):
            streams[link_name[1:-2]] = link[1:-2]

    return streams


def on_stream_select(event):
    # print('match selected')
    w = event.widget
    index = int(w.curselection()[0])
    stream = w.get(index)
    # print('You selected item %d: "%s"' % (index, stream))
    open_link_incognito(streams[stream])


def update_streams_thread(match):
    time.sleep(5)
    global streams
    streams = get_match_streams(match)


# function to show streams available for a match after user selects a match
def show_match_streams(selected_match):
    global streams
    clear_root()  # removing earlier widgets, to display match streams

    p = Progressbar(root, orient=HORIZONTAL, length=200, mode="indeterminate")
    p.place(relx=0.5, rely=0.5, anchor=CENTER)
    p.pack()
    p.start(interval=10)

    # finding the user selected match from list of matches
    for post in posts:
        if selected_match == post['data']['title']:
            match = post
            break

    # update_streams_thread(match)

    thread = threading.Thread(target=update_streams_thread(match), args=())
    # thread.daemon = True  # Allow the program to terminate without waiting for the thread to finish.
    thread.start()

    while thread.isAlive():
        print('hi')

    p.stop()
    p.destroy()

    label = Label(root, text=match['data']['title'] + '\n Click on any stream to watch')
    label.pack()

    list_box = Listbox(root, selectmode=SINGLE)
    list_box.bind(sequence="<<ListboxSelect>>", func=on_stream_select)

    scrollbar = Scrollbar(root, orient="vertical")
    scrollbar.config(command=list_box.yview)
    scrollbar.pack(side="right", fill="y")
    list_box.config(yscrollcommand=scrollbar.set, font=medium_font)

    index = 0
    for key, val in streams.items():
        list_box.insert(index, key)
        index += 1

    list_box.pack(fill=BOTH, expand=1, pady=8, padx=8, anchor=CENTER)
    list_box.config(width=0)  # ref 1

    bottom_frame = Frame(root)
    bottom_frame.pack(side=BOTTOM)

    back_button = Button(bottom_frame, text='Back')
    back_button.pack(side=LEFT, pady=8, padx=8)
    back_button.bind(sequence='<Button-1>', func=back)


def clear_root():
    # removing all widgets from root
    widgets = root.winfo_children()
    for widget in widgets:
        widget.destroy()


def back(event):
    # remove all widgets from root
    clear_root()
    show_current_matches()


# function which is called when user clicks on a  match
def on_match_select(event):
    # print('match selected')
    w = event.widget
    index = int(w.curselection()[0])
    match = w.get(index)
    # print('You selected item %d: "%s"' % (index, match))
    show_match_streams(match)


# show matches available in a ListBox
def show_current_matches():
    list_box = Listbox(root, selectmode=SINGLE)
    list_box.bind(sequence="<<ListboxSelect>>", func=on_match_select)

    index = 0
    flag = 0
    for post in posts:
        if 'vs' in post['data']['title'] or ' v ' in post['data']['title']:
            list_box.insert(index, post['data']['title'])
            index += 1
            flag = 1

    if not flag:
        show_error('Info', 'Currently there are no match streams available!')

    label = Label(root, text='Showing currently available streams')
    label.pack()

    scrollbar = Scrollbar(root, orient="vertical")
    scrollbar.config(command=list_box.yview)
    scrollbar.pack(side="right", fill="y")

    list_box.pack(fill=BOTH, expand=1, pady=8, padx=8, anchor=CENTER)
    list_box.config(yscrollcommand=scrollbar.set, width=0, font=medium_font)  # ref 1

    bottom_frame = Frame(root)
    bottom_frame.pack(side=BOTTOM)

    refresh_button = Button(bottom_frame, text='Refresh Matches')
    refresh_button.pack(side=LEFT, pady=8, padx=8)
    refresh_button.bind(sequence='<Button-1>', func=refresh)

    exit_button = Button(bottom_frame, text='Exit')
    exit_button.pack(side=LEFT, pady=8, padx=8)
    exit_button.bind(sequence="<Button-1>", func=close_program)

    help_button = Button(bottom_frame, text='Help & FAQ')
    help_button.pack(side=RIGHT, pady=8, padx=8)
    help_button.bind(sequence="<Button-1>", func=help)
    root.mainloop()


def refresh(event):
    clear_root()
    show_current_matches()


def help(event):
    webbrowser.open('https://gist.github.com/prasanna189/2fec24583dac6f05e65c91f2d3795000')


# shows a given message in a MessageBox
def show_error(info, msg):
    messagebox._show(info, msg)


# destroy tkinter root window
def close_program(event):
    root.destroy()

# used for opening the match stream in an incognito window.
# incognito is used because the streams usually contain ads and malicious cookies or scripts
def open_link_incognito(url):
    try:
        browser_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s --incognito'
        webbrowser.get(browser_path).open_new(url)
    except:
        show_error('Error with browser', 'Try changing the browser path in open_link_incognito() function.')


# gets matches as json from given url and stores it in a file
def get_json_response(url):
    response=''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        }
        response = requests.get(url=url, headers=headers).json()
    except Exception as e:
        show_error('Exception occurred!',e)
    return response


if __name__ == '__main__':
    streams = {}
    url = 'https://www.reddit.com/r/soccerstreams.json'
    response = get_json_response(url)

    try:
        posts = response['data']['children']
        show_current_matches()

    except Exception as e:
        # print(e)
        show_error('Some error occurred!', 'Please try again.')
        # print(response)