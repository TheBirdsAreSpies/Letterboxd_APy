
# Letterboxd APy
Reimplementation of the private Letterboxd api in Python. This is based on website scraping so please, handle it with
care! This is **much slower and much less convenient** than native api calls.

This is still WIP and loads of functions are still missing - expect encountering lots of bugs.
There probably will also be changes in the methods signatures. 

Feel free to create a pull request if you like to participate.

## How to use
Login, this is needed to create a session to work with
```
login = Login('EMAIL', 'PASSWORD')
session = login.login()
```

Search for movies
```
search = Search()
found_movies = search.search('reservoir dogs', SearchType.FILMS)
movie = found_movies[0]
```

Load movie details
```
movie.load_detail()
```

Create movie log (diary entry)
```
movie.log(7, '2023-10-16', liked=True)
```

Get user information
```
user = User('USERNAME')
user.load_detail()
```

Export data
```
user.download_export_data()
```
