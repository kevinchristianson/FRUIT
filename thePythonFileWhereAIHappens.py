from pandas import read_csv
from json import dump, load
from pathlib import Path

movieDict = {}
userDict = {}
movieScores = {}
movieIdToTitle = {}

userTestDict = {}

def initializeTestData():
    USERTEST_FILE = "data/userTest_dict.txt"

    global userTestDict = {}

    if Path(USERTEST_FILE).is_file():
        userTestDict = load(open(USERTEST_FILE))
    else:
        data = read_csv("data/ml-20m/ratings.csv")
        for i in range(data.count()["userId"]):
            userId = str(data["userId"][i])
            movieId = str(data["movieId"][i])
            rating = float(data["rating"][i])
            if userId > 6408:
                if userId not in userTestDict:
                    # userNode = UserNode(userId)
                    userTestDict[userId] = {}
                if rating <= 2:
                    rating = -1
                elif rating >= 4:
                    rating = 1
                else:
                    rating = 0
                userTestDict[userId][movieId] = rating
                if userId in userDict:
                    del userDict[userId]

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

def calculateFinalScores(n):
    global movieScores
    totalScoreRanking = sorted(movieScores, key=getTotalScore)
    for i in range(len(totalScoreRanking)):
        movieScores[totalScoreRanking[i]]["final_score"] = i
    averageScoreRanking = sorted(movieScores, key=getAverageScore)
    for i in range(len(averageScoreRanking)):
        movieScores[averageScoreRanking[i]]["final_score"] += i * ((len(totalScoreRanking) - movieScores[averageScoreRanking[i]]["final_score"]) / len(totalScoreRanking)) * (1 + (1 / len(totalScoreRanking)))
    return sorted(movieScores, key=getFinalScore, reverse=True)[:n]

def findRecForUser(userId, n = 30):
    userFilms = userDict[userId]
    return findRecFromMovies(userFilms, n)

def getFinalScore(movie):
    return movieScores[movie]["final_score"]

def getTotalScore(movie):
    return movieScores[movie]["total"]

def getAverageScore(movie):
    return movieScores[movie]["score"]

def findRecFromMovies(userFilms, n = 30):
    global movieScores
    for key in userFilms:
        if userFilms[key] == 1:
            updateMovieScores(movieScores, key)
    for key in userFilms:
        if key in movieScores:
            del movieScores[key]
    createFinalScores(movieScores)
    return calculateFinalScores(n)

def createFinalScores(movieScores):
    for key in movieScores:
        currentMovie = movieScores[key]
        currentMovie["score"] = currentMovie["total"] / currentMovie["people"]

def updateMovieScores(movieScores, movieId):
    filmUsers = movieDict[movieId]
    for key in filmUsers:
        if filmUsers[key] == 1:
            addUserScores(movieScores, key)

def addUserScores(movieScores, userId):
    for key in userDict[userId]:
        if key in movieScores:
            movieScores[key]["total"] += userDict[userId][key]
            movieScores[key]["people"] += 1
        else:
            movieScores[key] = {}
            movieScores[key]["total"] = userDict[userId][key]
            movieScores[key]["people"] = 1

def movieFromId(movieId):
    return movieIdToTitle[movieId]

def main():
    initialize()
    initializeTestData()
    kevinDict = {"60126": 1, "110102" : 1, "117448" : 1, "8961" : 1, "106696" : 1, "899" : 1, "4963" : 1, "2501" : 1, "912" : 1}
    kevRecs = findRecFromMovies(kevinDict)
    # stanDict = {"110102": 1, "88140": 1, "86332": 1, "59315": 1, "89745": 1}
    # stanRecs = findRecFromMovies(stanDict)
    # user1Recs = findRecForUser("1")
    # for key in userDict["1"]:
    #     print(movieFromId(key) + ":" + str(userDict["1"][key]))
    print("================\n\n================")
    for filmId in kevRecs:
        print(movieFromId(filmId))
        # print(movieScores[filmId]["final_score"])
        # print(movieScores[filmId]["total"])
        # print(movieScores[filmId]["people"])
        # print(movieScores[filmId]["score"])
        # print()

if __name__== '__main__':
    main()
