
# Letterboxd APy
Reimplementation of the private Letterboxd api in Python.

This is still WIP and loads of functions are still missing - expect encountering lots of bugs.
There will also be changes in the methods signatures probably but feel free to create a pull request.

## How to use
Login, this is needed to create a session to work with
> login = Login('EMAIL', 'PASSWORD')
> session = login.login()

Search for movies
> search = Search(session)
> found_movies = search.search('reservoir dogs', SearchType.FILMS)
> movie = found_movies[0]

Load movie details
> movie.load_detail(session)

Create movie log
> movie.log(7, '2023-10-16', liked=True)

Get user information
> user = User('USERNAME')
> user.load_detail()

Export data
> user.download_export_data()
