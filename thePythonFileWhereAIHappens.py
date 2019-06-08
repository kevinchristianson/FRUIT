from pandas import read_csv
from json import dump, load
from pathlib import Path

movieDict = {}
userDict = {}
movieIdToTitle = {}

def initialize():
    MOVIE_FILE = "data/movie_dict.txt"
    USER_FILE = "data/user_dict.txt"
    MOVIETITLES_FILE = "data/movietitles_dict.txt"

    global movieDict
    global userDict
    global movieIdToTitle

    if Path(MOVIETITLES_FILE).is_file():
        movieIdToTitle = load(open(MOVIETITLES_FILE))
    else:
        movieData = read_csv("data/ml-20m/movies.csv")
        for i in range(movieData.count()["movieId"]):
            movieId = str(movieData["movieId"][i])
            title = str(movieData["title"][i])
            movieIdToTitle[movieId] = title
        with open(MOVIETITLES_FILE, "w") as file:
            dump(movieIdToTitle, file, ensure_ascii=False)

    if Path(MOVIE_FILE).is_file() and Path(USER_FILE).is_file():
        movieDict = load(open(MOVIE_FILE))
        userDict = load(open(USER_FILE))
        # for key in movieDict:
        #     if len(movieDict[key]) > 1:
        #         break
    else:
        data = read_csv("data/ml-20m/ratings.csv")
        for i in range(data.count()["userId"]):
            userId = str(data["userId"][i])
            movieId = str(data["movieId"][i])
            rating = float(data["rating"][i])
            if userId not in userDict:
                # userNode = UserNode(userId)
                userDict[userId] = {}
            if movieId not in movieDict:
                # movieNode = MovieNode(movieId)
                movieDict[movieId] = {}
            if rating <= 2:
                rating = -1
            elif rating >= 4:
                rating = 1
            else:
                rating = 0
            movieDict[movieId][userId] = rating
            userDict[userId][movieId] = rating

        with open(MOVIE_FILE, "w") as file:
            dump(movieDict, file, ensure_ascii=False)
        with open(USER_FILE, "w") as file:
            dump(userDict, file, ensure_ascii=False)

def findRecForUser(userId, n = 10):
    userFilms = userDict[userId]
    return findRecFromMovies(userFilms, n)

def findRecFromMovies(userFilms, n = 10):
    movieScores = {}
    for key in userFilms:
        if userFilms[key] == 1:
            movieScores = updateMovieScores(movieScores, key)
    for key in userFilms:
        if key in movieScores:
            del movieScores[key]
    return sorted(movieScores, key=movieScores.get)[:n]

def updateMovieScores(movieScores, movieId):
    filmUsers = movieDict[movieId]
    for key in filmUsers:
        if filmUsers[key] == 1:
            movieScores = addUserScores(movieScores, key)
    return movieScores

def addUserScores(movieScores, userId):
    for key in userDict[userId]:
        if key in movieScores:
            movieScores[key] += userDict[userId][key]
        else:
            movieScores[key] = userDict[userId][key]
    return movieScores

def movieFromId(movieId):
    return movieIdToTitle[movieId]

def main():
    initialize()
    # kevinDict = {"60126": 1, "110102" : 1, "117448" : 1, "8961" : 1, "106696" : 1, "899" : 1, "4963" : 1, "2501" : 1, "912" : 1}
    # kevRecs = findRecFromMovies(kevinDict)
    # stanDict = {"110102": 1, "88140": 1, "86332": 1, "59315": 1, "89745": 1}
    # stanRecs = findRecFromMovies(stanDict)
    user1Recs = findRecForUser("1")
    for key in userDict["1"]:
        print(movieFromId(key))
    print("================ \n \n ================")
    for filmId in user1Recs:
        print(movieFromId(filmId))

if __name__== '__main__':
    main()
