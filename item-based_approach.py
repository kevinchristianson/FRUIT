from pandas import read_csv
from pickle import dump, load
from pathlib import Path
from math import sqrt
from heapq import heappush, heappushpop

class User:

    def __init__(self):
        self.num_ratings = 0
        self.total_rating_value = 0


    def add_rating(self, rating):
        self.total_rating_value += rating[1]
        self.num_ratings += 1

    def get_avg_rating(self):
        return self.total_rating_value / self.num_ratings

users = {}
films = {}
similarities = {}
def initialize():
    DATA_FILE = 'data/ml-20m/ratings.csv'
    SIMILARITY_FILE = 'data/similarities_temp.pkl'
    TEST_FILE = 'data/test_temp.csv'
    USER_FILE = 'data/users_temp.pkl'
    FILM_FILE = 'data/films_temp.pkl'
    NUM_SIMILARITIES = 200 # for each film, track the top 200 most similar

    if Path(USER_FILE).is_file() and Path(FILM_FILE).is_file():
        with open(USER_FILE, 'rb') as file:
            users = load(file)
        with open(FILM_FILE, 'rb') as file:
            films = load(file)
    else:
        data = read_csv(DATA_FILE)
        n = len(data)
        n = n - int(n * .90) # save last 10% of file for testing
        data[n:].to_csv(TEST_FILE, encoding='utf-8', index=False)
        data = data[:n]
        n = len(data)
        for index, row in data.iterrows():
            user_id, movie_id, rating = row[:3]
            if user_id not in users:
                users[user_id] = User()
            users[user_id].add_rating( (movie_id, rating) )
            if movie_id not in films:
                films[movie_id] = {}
            films[movie_id][users[user_id]] = rating
            index = index / n
            print("\rReading Data: [%-20s] %d%%" % ('=' * int(20 * index), 100 * index), end = '')
        print("\rReading Data: [%-20s] %d%%" % ('=' * 20, 100))

        with open(USER_FILE, 'wb') as file:
            dump(users, file, 2)
        with open(FILM_FILE, 'wb') as file:
            dump(films, file, 2)

    if Path(SIMILARITY_FILE).is_file():
        with open(SIMILARITY_FILE, 'rb') as file:
            print('loading similarities from file', end = '')
            similarities = load(file)
            print('\rloaded similarities from file ')
    else:
        computed = {}
        n = len(films)
        i = 0
        for k1 in films.keys():
            k1 = int(k1)
            similarities[k1] = [(1,1)]
            f1 = films[k1]
            i += 1
            print("\rCalculating Similarities: [%-20s] %d%%" % ('=' * int(20 * i / n), 100 * i / n), end = '')
            for k2 in films.keys():
                k2 = int(k2)
                if k1 != k2:
                    if k2 in similarities:
                        if len(similarities[k1]) < NUM_SIMILARITIES:
                            heappush(similarities[k1], (computed[k1][k2], k2))
                        else:
                            heappushpop(similarities[k1], (computed[k1][k2], k2))
                        del computed[k1][k2]
                    else:
                        f2 = films[k2]
                        numerator = 0
                        left_denom = 0
                        right_denom = 0
                        for user in f1.keys():
                            # calculate adjusted cosine similarity
                            if user in f2:
                                a = f1[user] - user.get_avg_rating()
                                b = f2[user] - user.get_avg_rating()
                                numerator += a * b
                                left_denom += a * a
                                right_denom += b * b
                        # this is combined denominator. Used one variable for efficiency
                        left_denom = sqrt(left_denom) * sqrt(right_denom)
                        # calculate value to be small to big since heapq uses min heap and want max heap
                        left_denom = 1 - (numerator / left_denom if left_denom != 0 else 1)
                        if k2 not in similarities:
                            if k2 not in computed:
                                computed[k2] = { k1: left_denom }
                            else:
                                computed[k2][k1] = left_denom
                        if len(similarities[k1]) < NUM_SIMILARITIES:
                            heappush(similarities[k1], (left_denom, k2))
                        else:
                            heappushpop(similarities[k1], (left_denom, k2))
        print("\rCalculating Similarities: [%-20s] %d%%" % ('=' * 20, 100))

        with open(SIMILARITY_FILE, 'wb') as file:
            dump(similarities, file, 2)

def main():
    initialize()

if __name__ == '__main__':
    main()
