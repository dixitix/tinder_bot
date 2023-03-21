import sqlite3 as sql


async def db_connect():
    global db, cursor
    db = sql.connect('tindor.db')
    cursor = db.cursor()
    query = "CREATE TABLE IF NOT EXISTS profiles(user_id TEXT PRIMARY KEY, name TEXT, gender TEXT, " \
            "birth_day INTEGER, birth_month INTEGER, birth_year INTEGER, birth_hour TEXT, birth_minute TEXT, " \
           "birth_city TEXT, city TEXT, preferences TEXT, photo TEXT, description TEXT) "
    query2 = "CREATE TABLE IF NOT EXISTS likes(user_id TEXT, match TEXT,  PRIMARY KEY (user_id, match))"
    query3 = "CREATE TABLE IF NOT EXISTS cities(city_id TEXT PRIMARY KEY, city_name TEXT, region TEXT)"
    query4 = "CREATE TABLE IF NOT EXISTS dislikes(user_id TEXT, mismatch TEXT, PRIMARY KEY (user_id, mismatch))"
    cursor.execute(query)
    cursor.execute(query2)
    cursor.execute(query3)
    cursor.execute(query4)
    db.commit()


async def create_profile(state, user_id):
    user = cursor.execute(
        "SELECT user_id FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()
    if not user:
        async with state.proxy() as data:
            cursor.execute(
                "INSERT INTO profiles (user_id, name, gender, birth_day, birth_month, birth_year, birth_hour, birth_minute, birth_city, city, preferences, photo, description, nickname_tg, frozen) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                (user_id, data['name'], data["gender"], data["birth_day"],
                 data["birth_month"], data["birth_year"], data["birth_hour"],
                 data["birth_minute"], data["birth_city"], data["city"],
                 data["preferences"], data["photo"], data["description"],
                 data['nickname_tg']))
            db.commit()
    else:
        await update_profile(state, user_id)


async def update_profile(state, user_id):
    async with state.proxy() as data:
        update_query = "UPDATE profiles  SET name ='{}', gender ='{}', birth_day ='{}', birth_month ='{}', birth_year = '{}', birth_hour ='{}', birth_minute ='{}', birth_city ='{}', city ='{}', preferences ='{}', photo='{}', description ='{}', nickname_tg='{}'  WHERE user_id=='{}'".format(
            data['name'], data["gender"], data["birth_day"],
            data["birth_month"], data["birth_year"], data["birth_hour"],
            data["birth_minute"], data["birth_city"], data["city"],
            data["preferences"], data["photo"], data["description"],
            data["nickname_tg"], user_id)
        cursor.execute(update_query)
        db.commit()


async def get_all_profiles():
    profiles = cursor.execute("SELECT * FROM profiles").fetchall()
    return profiles


async def user_exists(user_id):
    user = cursor.execute(
        "SELECT user_id FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()
    if not user:
        return False
    return True


async def delete_profile(user_id):
    cursor.execute(
        "DELETE FROM profiles WHERE user_id == '{key}'".format(key=user_id))
    cursor.execute(
        "DELETE FROM likes WHERE user_id == '{key}'".format(key=user_id))
    cursor.execute(
        "DELETE FROM likes WHERE match == '{key}'".format(key=user_id))
    cursor.execute(
        "DELETE FROM dislikes WHERE user_id == '{key}'".format(key=user_id))
    db.commit()
    cursor.execute(
        "DELETE FROM dislikes WHERE mismatch == '{key}'".format(key=user_id))
    db.commit()


async def edit_description(new_description, user_id):
    cursor.execute(
        "UPDATE profiles SET description = '{}' WHERE user_id = '{}'".format(
            new_description, user_id))
    db.commit()


async def get_name(user_id):
    name = cursor.execute(
        "SELECT name FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return name


async def get_gender(user_id):
    gender = cursor.execute(
        "SELECT gender FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return gender


async def get_birth_day(user_id):
    birth_day = cursor.execute(
        "SELECT birth_day FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_day


async def get_birth_month(user_id):
    birth_month = cursor.execute(
        "SELECT birth_month FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_month


async def get_birth_year(user_id):
    birth_year = cursor.execute(
        "SELECT birth_year FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_year


async def get_birth_minute(user_id):
    birth_minute = cursor.execute(
        "SELECT birth_minute FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_minute


async def get_birth_hour(user_id):
    birth_hour = cursor.execute(
        "SELECT birth_hour FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_hour


async def get_birth_city(user_id):
    birth_city = cursor.execute(
        "SELECT birth_city FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return birth_city


async def get_city(user_id):
    city = cursor.execute(
        "SELECT city FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return city


async def get_preferences(user_id):
    preferences = cursor.execute(
        "SELECT preferences FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return preferences


async def get_photo(user_id):
    photo = cursor.execute(
        "SELECT photo FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return photo


async def get_description(user_id):
    description = cursor.execute(
        "SELECT description FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return description


async def get_username(user_id):
    username = cursor.execute(
        "SELECT nickname_tg FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()[0]
    return username


def select_city(city):
    cities_found = cursor.execute(
        "SELECT city_name FROM cities WHERE city_name == '{key}'".format(
            key=city)).fetchall()
    return cities_found


async def get_map_fields(user_id):
    if await user_exists(user_id=user_id):
        query = "SELECT birth_day, birth_month, birth_year, birth_hour, birth_minute, birth_city FROM profiles WHERE " \
                "user_id == '{key}'".format(key=user_id)
        user_data = cursor.execute(query).fetchone()
        city_query = "SELECT city_id FROM cities WHERE city_name = '{}'".format(
            user_data[5])
        user_data = user_data[:5]
        user_data += cursor.execute(city_query).fetchone()
        user_data = user_data[:6]
        return user_data


async def get_profile(user_id):
    user = cursor.execute(
        "SELECT * FROM profiles WHERE user_id == '{key}'".format(
            key=user_id)).fetchone()
    return user


def get_nickname(nickname):
    city_name = cursor.execute(
        "SELECT name FROM nicknames WHERE nickname = '{}'".format(
            nickname)).fetchone()[0]
    return city_name


def fill_planets(user_id, planets_list):
    set_planets = "UPDATE profiles  SET sun ='{}', moon ='{}', mercury ='{}', venus ='{}', mars = '{}', jupiter ='{}', saturn ='{}', uranus ='{}', neptune ='{}', plyto ='{}' WHERE user_id=='{}'".format(
        planets_list[0], planets_list[1], planets_list[2], planets_list[3],
        planets_list[4], planets_list[5], planets_list[6], planets_list[7],
        planets_list[8], planets_list[9], user_id)
    cursor.execute(set_planets)
    db.commit()


def return_planets(user_id):
    planets = cursor.execute(
        "SELECT sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, plyto, user_id FROM profiles WHERE user_id = '{}'"
        .format(user_id)).fetchone()[:11]
    return planets


def choose_match(user_id):
    param = cursor.execute(
        "SELECT city, preferences, gender FROM profiles WHERE user_id == '{key}'"
        .format(key=user_id)).fetchone()[:3]
    antipreferences = {'Мужчина': "женщин", "Женщина": "мужчин"}
    if param[2] == "Do not give a fuck":
        candidates = cursor.execute(
            "SELECT sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, plyto, user_id FROM profiles p LEFT JOIN (SELECT DISTINCT match FROM (SELECT user_id, match  FROM likes l UNION ALL SELECT * FROM dislikes d) WHERE user_id = '{}') t ON p.user_id = t.match WHERE t.match is NULL and user_id <> '{}' and city = '{}' and preferences ='не важно' and frozen <> '1'"
            .format(user_id, user_id, param[0])).fetchall()
    elif param[1] == "женщин":
        candidates = cursor.execute(
            "SELECT sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, plyto, user_id FROM profiles p LEFT JOIN (SELECT DISTINCT match FROM (SELECT user_id, match  FROM likes l UNION ALL SELECT * FROM dislikes d) WHERE user_id = '{}') t ON p.user_id = t.match WHERE t.match is NULL and user_id <> '{}' and gender = 'Женщина' and city = '{}' and preferences <> '{}' and frozen != 1"
            .format(user_id, user_id, param[0],
                    antipreferences[param[2]])).fetchall()
    elif param[1] == "мужчин":
        candidates = cursor.execute(
            "SELECT sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, plyto, user_id FROM profiles p LEFT JOIN (SELECT DISTINCT match FROM (SELECT user_id, match  FROM likes l UNION ALL SELECT * FROM dislikes d) WHERE user_id = '{}') t ON p.user_id = t.match WHERE t.match is NULL and user_id <> '{}' and gender = 'Мужчина' and city = '{}' and preferences <> '{}' and frozen <> 1 "
            .format(user_id, user_id, param[0],
                    antipreferences[param[2]])).fetchall()
    else:
        candidates = cursor.execute(
            "SELECT sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, plyto, user_id FROM profiles p LEFT JOIN (SELECT DISTINCT match FROM (SELECT user_id, match FROM likes l UNION ALL SELECT * FROM dislikes d) WHERE user_id = '{}') t ON p.user_id = t.match WHERE t.match is NULL and user_id <> '{}' and city = '{}' and preferences <> '{}' and frozen <> 1"
            .format(user_id, user_id, param[0],
                    antipreferences[param[2]])).fetchall()
    return candidates


async def add_like(user_id, match_id):
    cursor.execute("INSERT INTO likes (user_id, match, seen) VALUES(?, ?, ?)",
                   (user_id, match_id, 0))
    db.commit()


async def add_dislike(user_id, mismatch_id):
    cursor.execute("INSERT INTO dislikes (user_id, mismatch) VALUES(?, ?)",
                   (user_id, mismatch_id))
    db.commit()


def get_matches(user_id):
    candidates = cursor.execute(
        "SELECT match from likes WHERE user_id = '{key}' and seen !='1'".
        format(key=user_id)).fetchall()
    matches = []
    for candidate in candidates:
        match = cursor.execute(
            "SELECT user_id from likes WHERE user_id = '{}' AND match = '{}' ".
            format(candidate[0], user_id)).fetchone()
        frozen = cursor.execute("SELECT frozen from profiles WHERE user_id = '{}'".
            format(candidate[0])).fetchone()[0]
        if match and not frozen:
            matches += candidate
    return matches


def mark_seen(user_id, match_id):
    cursor.execute(
        "UPDATE likes SET seen = '1' WHERE user_id = '{}'AND match = '{}'".
        format(user_id, match_id))
    db.commit()


def check_like(user_id, match_id):
    match = cursor.execute(
        "SELECT user_id from likes WHERE user_id = '{}' AND match = '{}'".
        format(match_id, user_id)).fetchone()
    return match


def freeze_user(user_id):
    cursor.execute(
        "UPDATE profiles SET frozen = 1 WHERE user_id = '{}'".format(
            user_id))
    db.commit()


def unfreeze_user(user_id):
    cursor.execute(
        "UPDATE profiles SET frozen = 0 WHERE user_id = '{}'".format(
            user_id))
    db.commit()


def check_user(user_id):
    status = cursor.execute(
        "SELECT frozen FROM profiles WHERE user_id = '{}'".format(
            user_id)).fetchone()
    return status[0]

def check_match(user_id, candidate_id):
    user_like = check_like(user_id, candidate_id)
    candidate_like = check_like(candidate_id, user_id)
    if user_like and candidate_like:
        return 1
    return 0