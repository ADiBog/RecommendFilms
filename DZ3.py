import cmath
import pandas as pd
import requests

user_id = 3
data_file_path = 'data.csv'
context_file_path = 'context.csv'

def avg_rate(u, data):
    avg = 0; cnt = 0
    for rate in data.iloc[u]:
        if rate != -1:
            avg += rate
            cnt += 1
    return avg/cnt


def sim(u, v, data):
    user1 = data.iloc[u]
    user2 = data.iloc[v]
    uv_sum = 0
    u_sum = 0
    v_sum = 0

    for i in range(0, len(user1)):
        if user1[i] != -1 and user2[i] != -1:
            uv_sum += user1[i]*user2[i]
            u_sum += user1[i]**2
            v_sum += user2[i]**2

    return uv_sum / (cmath.sqrt(u_sum) * cmath.sqrt(v_sum))


def get_rate(u, i, data, sims):
    sum_1 = 0;sum_2 = 0
    for v in sims:
        v_rate = data.iloc[v, i]
        if v != u and v_rate != -1:
            sum_1 += sims[v] * (v_rate - avg_rate(v, data))
            sum_2 += abs(sims[v])
    return avg_rate(u, data) + sum_1 / sum_2


def get_film_rates(u, data):
    rates = {}; sims = {}
    for v in range(0, len(data.axes[0])):
        if v != u:
            sims[v] = sim(u, v, data)
    sims = dict(sorted(sims.items(), key=lambda x: x[1], reverse=True)[:5])

    for i in range(0, len(data.axes[1])):
        if data.iloc[u, i] == -1:
            rates[data.axes[1][i]] = get_rate(u, i, data, sims)
    return rates

def filter_rates(u, data, context):
    result = data.copy()
    for u_id in range(0, len(context.axes[0])):
        if u_id != u:
            for movie_id in range(0, len(context.axes[1])):
                day = context.iloc[u_id, movie_id].lower()
                if day == 'sun' or day == 'sat':
                    result.iloc[u_id, movie_id] = -1
    return result


def get_film(u, data, context):
    filtered_data = filter_rates(u, data, context)
    movies_rates = get_film_rates(u, filtered_data)
    movies_rates = sorted(movies_rates.items(), key=lambda x: x[1], reverse=True)
    return movies_rates[0]

data_frame = pd.read_csv(data_file_path, index_col=0, sep=', ')
context_frame = pd.read_csv(context_file_path, index_col=0, sep=', ')

film_rates = get_film_rates(user_id - 1, data_frame)
film = get_film(user_id - 1, data_frame, context_frame)

answer = {
    'user': user_id,
    '1': {}
}

for (movie_name, movie_rating) in film_rates.items():
    answer['1'][movie_name.lower()] = movie_rating.real

if film:
    answer['2'] = {}
    answer['2'][film[0].lower()] = film[1].real

req = requests.post('https://cit-home1.herokuapp.com/api/rs_homework_1', json=answer)

print(req.text)