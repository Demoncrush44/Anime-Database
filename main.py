import os
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests


app = Flask(__name__)

# graphql request format for pagination
url = 'https://graphql.anilist.co'
query = '''
    query ($page: Int, $perPage: Int) { # Define which variables will be used in the query (id)
        Page (page: $page, perPage: $perPage) {
            pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
        media (format: TV, sort: POPULARITY_DESC) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
            title {
                romaji
                english
                native
                }
            genres
            status
            episodes
            coverImage {
            extraLarge
            large
            medium
            color
            }
        }
    }
}

'''
youtube = build('youtube', 'v3',
                developerKey='API KEY GOES HERE')


@app.route("/")
def popular_shows():
    # Displays 40 anime titles per page with a limit of 120 shows
    for i in range(1):
        variables = {'page': i + 1, 'perPage': 48}
        response = requests.post(
            url, json={'query': query, 'variables': variables})

    r = response.json()

    data = r['data']['Page']['media']

    show_list = []
    for show in data:
        show_dict = {
            'title': show['title']['romaji'],
            'cover_image': show['coverImage']['large']
        }
        show_list.append(show_dict)

    return render_template("page1.html", shows=show_list)

# pulls the second page of top animes


@app.route("/page2")
def popular_shows2():
    # Displays 40 anime titles per page with a limit of 120 shows
    for i in range(2):
        variables = {'page': i + 1, 'perPage': 48}
        response = requests.post(
            url, json={'query': query, 'variables': variables})

    r = response.json()

    data = r['data']['Page']['media']

    romaji = []
    for i in data:
        romaji.append(i["title"]['romaji'])

    large = []
    for i in data:
        large.append(i['coverImage']['large'])

    anime = zip(large, romaji)

    return render_template("page1.html", data=data,
                           anime=anime)


@app.route("/page3")
def popular_shows3():
    # Displays 40 anime titles per page with a limit of 120 shows
    for i in range(3):
        variables = {'page': i + 1, 'perPage': 48}
    response = requests.post(
        url, json={'query': query, 'variables': variables})

    r = response.json()

    data = r['data']['Page']['media']

    romaji = []
    for i in data:
        romaji.append(i["title"]['romaji'])

    large = []
    for i in data:
        large.append(i['coverImage']['large'])

    anime = zip(large, romaji)

    return render_template("page1.html", data=data,
                           anime=anime)


@app.route('/details')
# individual show detail page
def show_details():
    title = request.args.get('title')
    # graphql setup for individual titles
    query = '''
        query ($search: String) {
            Media (search: $search) {
                title {
                    romaji
                }
                coverImage {
                    extraLarge
                    large
                }
                status
                description
                genres
                # Add any additional fields you want to retrieve
            }
        }
    '''
    variables = {'search': title}
    response = requests.post(
        url, json={'query': query, 'variables': variables})
    r = response.json()
    show_data = r['data']['Media']

    # Extract the relevant information, including the images
    show_title = show_data['title']['romaji']
    show_cover_image = show_data['coverImage']['large']
    show_banner_image = show_data['coverImage']['extraLarge']
    show_description = show_data['description']
    show_status = show_data['status']
    show_genres = show_data['genres']

    # Add any additional fields you retrieved from the API

    video_id = get_youtube_trailer(title)

    return render_template('show.html', title=show_title, cover_image=show_cover_image, description=show_description, status=show_status,
                           genres=show_genres, banner_image=show_banner_image, video_id=video_id)


def get_youtube_trailer(title):
    try:
        # Perform a search for the show's title and append "trailer" to the search query
        search_response = youtube.search().list(
            q=title + ' pv',
            part='id',
            maxResults=1,
            type='video'
        ).execute()

        # Retrieve the video ID of the first search result
        video_id = search_response['items'][0]['id']['videoId']

        return video_id

    except HttpError as e:
        print(f'An error occurred: {e}')
        return None


app.run(host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True)
