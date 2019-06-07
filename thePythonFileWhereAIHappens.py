import pandas
import json

# class MovieNode():
#     def __init__(self, movieID):
#         self.movieID = movieID
#         self.users = {}
#
# class UserNode():
#     def __init__(self, userID):
#         self.userID = userID
#         self.movies = {}

movieDict = {}
userDict = {}

def initialize():
    data = pandas.read_csv("./data/ml-20m/ratings.csv")
    for i in range(data.count()["userId"]):
        userId = data["userId"][i]
        movieId = data["movieId"][i]
        rating = float(data["rating"][i])
        if userId not in userDict:
            # userNode = UserNode(userId)
            userDict[str(userId)] = {}
        if movieId not in movieDict:
            # movieNode = MovieNode(movieId)
            movieDict[str(movieId)] = {}
        if rating <= 2:
            rating = -1
        elif rating >= 4:
            rating = 1
        else:
            rating = 0
        movieDict[str(movieId)][str(userId)] = rating
        userDict[str(userId)][str(movieId)] = rating

    file = open("./data/movie_dict.txt", "w")
    json.dump(movieDict, file, ensure_ascii=False)
    file.close()
    file = open("./data/user_dict.txt", "w")
    json.dump(userDict, file, ensure_ascii=False)
    file.close()





def main():
    initialize()

if __name__== '__main__':
    main()
