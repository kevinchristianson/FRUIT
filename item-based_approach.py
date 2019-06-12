from pandas import read_csv
from pickle import dump, load
from pathlib import Path
from math import sqrt
from heapq import heappush, heappushpop

# STATIC VARIABLES
DATA_FILE = 'data/ml-20m/ratings.csv'
SIMILARITY_FILE = 'data/similarities.pkl'
TEST_FILE = 'data/test.csv'
USER_FILE = 'data/users.pkl'
FILM_FILE = 'data/films.pkl'
NUM_SIMILARITIES = 200 # for each film, track the top 200 most similar

class User:

    def __init__(self):
        self.num_ratings = 0
        self.ratings = {}
        self.total_rating_value = 0


    def add_rating(self, film, score):
        self.ratings[film] = score
        self.total_rating_value += score
        self.num_ratings += 1

    def get_ratings(self):
        return self.ratings

    def get_avg_rating(self):
        return self.total_rating_value / self.num_ratings

users = {}
films = {}
similarities = {}

# initializes above dictionaries based on data
def initialize():
    global users
    global films
    global similarities

    # load data from binary file if computed earlier
    if Path(USER_FILE).is_file() and Path(FILM_FILE).is_file():
        with open(USER_FILE, 'rb') as file:
            users = load(file)
        with open(FILM_FILE, 'rb') as file:
            films = load(file)
    else:
        data = read_csv(DATA_FILE)
        n = len(data)
        n = n - int(n * .10) # save last 10% of file for testing
        data[n:].to_csv(TEST_FILE, encoding='utf-8', index=False)
        data = data[:n]
        n = len(data)
        for index, row in data.iterrows():
            user_id, movie_id, rating = row[:3]
            if user_id not in users:
                users[user_id] = User()
            users[user_id].add_rating(movie_id, rating)
            if movie_id not in films:
                films[movie_id] = {}
            films[movie_id][users[user_id]] = rating
            index = index / n
            print("\rReading Data: [%-20s] %d%%" % ('=' * int(20 * index), 100 * index), end = '')
        print("\rReading Data: [%-20s] %d%%" % ('=' * 20, 100))

        # save to binary files so no need to recompute
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

# returns top num_results movies based on user_id
def recommend(user_id, num_results = 25):
    # TODO: ensure unique results. replace existing (or additive?) if higher, else pass
    if user_id not in users:
        return []
    reviewed = users[user_id].get_ratings()
    results = []
    for movie_id in reviewed:
        for sim1, potential_recommendation in similarities[movie_id]:
            numerator = 0 # score a movie by sum of user's ratings for movies similar to it
            denom = 0
            for sim2, similar_movie in similarities[potential_recommendation]:
                numerator += sim2 * reviewed[similar_movie] if similar_movie in reviewed else 0
                denom += sim2
            # make numerator negative to make min heap behave like max heap
            if len(results) < num_results:
                heappush(results, (-1 * (numerator / denom), potential_recommendation))
            else:
                heappushpop(results, (-1 * (numerator / denom), potential_recommendation))
    return results

def custom_recommend(user_id, num_results = 25):
    if user_id not in users:
        return []
    reviewed = users[user_id].get_ratings()
    results = {}
    for movie_id in reviewed:
        for sim, id in similarities[movie_id]:
            if id in results:
                results[id] += sim
            else:
                results[id] = sim
    return sorted(results.items(), key=lambda x: x[1])[:num_results]

# computes the MAE test by comparing expected values to actual
def test():
    data = read_csv(TEST_FILE)
    numerator = 0
    for index, row in data.iterrows():
        user_id, movie_id = [int(x) for x in row[:2]]
        rating = row[2]
        for score, id in recommend(user_id):
            if movie_id == id:
                numerator += abs(rating - score)
                break
    return numerator / len(data)

def custom_test():
    data = read_csv(TEST_FILE)
    # numerator = 0 #number of recommendations that are bad (movie not returned when should, or movie returned when shouldn't)
    false_pos = 0
    false_neg = 0
    seen = {}
    for index, row in data.iterrows():
        user_id, movie_id = [int(x) for x in row[:2]]
        rating = row[2]
        if movie_id in films:
            if user_id not in seen:
                seen[user_id] = custom_recommend(user_id, None)
            if movie_id in seen[user_id]:
                if rating < 2.5:
                    # numerator += 1
                    false_pos += 1
            elif rating > 2.5:
                    # numerator += 1
                    false_neg += 1
    print('false_pos:', false_pos, 'false_neg:', false_neg)
    return (false_pos + false_neg) / len(data)



def main():
    initialize()
    print('MAE =', custom_test())

if __name__ == '__main__':
    main()
