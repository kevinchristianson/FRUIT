from pandas import read_csv
from json import dump, load
from pathlib import Path

movieDict = {}
userDict = {}

def initialize():
    MOVIE_FILE = "data/movie_dict.txt"
    USER_FILE = "data/user_dict.txt"

    global movieDict
    global userDict

    if Path(MOVIE_FILE).is_file() and Path(USER_FILE).is_file():
        movieDict = load(open(MOVIE_FILE))
        userDict = load(open(USER_FILE))
        for key in movieDict:
            if len(movieDict[key]) > 1:
                break
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

def main():
    initialize()

if __name__== '__main__':
    main()
