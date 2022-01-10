#!/usr/bin/python3
from dataclasses import dataclass

import argparse
import json
import os
import sys

import requests

TMDB_BASE_URL = 'https://www.themoviedb.org'
TMDB_API_BASE_URL = 'https://api.themoviedb.org'
TMDB_API_VERSION = 3
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_MOVIE_URL = TMDB_BASE_URL + '/movie/{id}/'


@dataclass
class AlfredSuggestion:
    """Class for keeping track of an Alfred suggestion item."""
    # pylint: disable=too-many-arguments
    title: str
    arg: str
    subtitle: str = ""
    valid: bool = True
    variables: dict = None


class GenericSerializer(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def tmdb_api_request(endpoint, data=None):
    endpoint = endpoint.lstrip('/')
    headers = {
        'Authorization': f"Bearer {TMDB_API_KEY}",
        'Content-Type': 'application/json;charset=utf-8'
    }

    return requests.get(
        f"{TMDB_API_BASE_URL}/{TMDB_API_VERSION}/{endpoint}",
        headers=headers,
        params=data
    ).json()


def search_movies(query):
    response = tmdb_api_request(
        endpoint='/search/movie',
        data={
            'query': query
        }
    )
    return response['results']


def get_movie_details(tmdb_id):
    response = tmdb_api_request(
        endpoint=f"/movie/{tmdb_id}"
    )
    return response


def get_imdb_id(tmdb_id):
    details = get_movie_details(tmdb_id)
    return details['imdb_id']


def get_alfred_suggestions(search_term):
    suggestions = []

    tmdb_movies = search_movies(search_term)

    if len(tmdb_movies) > 0:
        for tmdb_movie in tmdb_movies:
            # print(tmdb_movies)
            suggestions.append(
                AlfredSuggestion(
                    title=f"{tmdb_movie['title']} ({tmdb_movie['release_date']})",
                    subtitle=tmdb_movie['original_title'],
                    arg=TMDB_MOVIE_URL.format(id=tmdb_movie['id']),
                    variables={
                        'id': tmdb_movie['id']
                    }
                )
            )
    else:
        suggestions = [
            AlfredSuggestion(
                title=f"No results for search term \"{search_term}\"",
                arg=None
            )
        ]

    response = json.dumps(
        {
            "items": suggestions
        },
        cls=GenericSerializer
    )

    return response


def validate_preconditions():
    if not TMDB_API_KEY:
        sys.exit('No TMDB API key set.')


def main():
    validate_preconditions()
    parser = argparse.ArgumentParser(description="TMDB Alfred interface.")
    parser.add_argument(
        "--action",
        help="The action to perform.",
        choices=['search', 'imdbId'],
        default='search'
    )
    parser.add_argument(
        "--query",
        help="The query to pass in to the action.",
        required=True
    )
    args = parser.parse_args()

    if args.action == 'search':
        print(get_alfred_suggestions(args.query))
    elif args.action == 'imdbId':
        print(get_imdb_id(args.query))


if __name__ == '__main__':
    main()
