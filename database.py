import sqlite3
from random import choice

con = sqlite3.connect('database(2).db')

cursorObj = con.cursor()


def set_using_bot(user_id, num):
    cursorObj.execute(f'UPDATE user_info SET "using" = {num} where "id" = {user_id}')
    con.commit()


def get(user_id, part, table):
    return cursorObj.execute(f'SELECT "{part}" FROM "{table}" WHERE "id" = {user_id}').fetchall()[0][0]


def set(user_id, part, table, new):
    cursorObj.execute(f'UPDATE "{table}" SET "{part}" = "{new}" WHERE "id" = {user_id}')
    con.commit()


def set_post(user_id, text, type):
    post_id = cursorObj.execute(f"SELECT id FROM {type}").fetchall()[-1][0] + 1
    print(cursorObj.execute(f"SELECT id FROM {type}").fetchall())
    cursorObj.execute(f'INSERT INTO {type}(id, text) VALUES{(post_id, text)}')
    cursorObj.execute(f'UPDATE "user_info" SET "post_id" = {post_id} WHERE id = {user_id}')
    con.commit()

    return post_id


def get_raffles(table):
    return cursorObj.execute(f'SELECT * FROM "{table}" WHERE "end" IS NOT NULL').fetchall()


def all_chanels():
    return [i[0] for i in
            cursorObj.execute('SELECT "channel" FROM active_spons_raffle WHERE "moder" IS NOT NULL').fetchall()]


def back(user_id, using):
    post = get(user_id, 'post_id', 'user_info')
    set_using_bot(user_id, 0)
    cursorObj.execute(f"UPDATE user_info SET post_id = NULL WHERE id = {user_id}")
    con.commit()
    cursorObj.execute(f"DELETE FROM {using} WHERE id = {post} AND WHERE moder IS NULL")
    con.commit()


def get_post(post_id, table):
    return cursorObj.execute(f'SELECT * FROM {table} WHERE id = {post_id}').fetchall()[0]


def start_raffle(id, table):
    print(id)
    post = cursorObj.execute(f'SELECT * FROM {table} WHERE id = "{id}"').fetchall()[0]
    print(post)
    cursorObj.execute(f"DELETE FROM {table} WHERE id = {post[0]}")
    con.commit()
    cursorObj.execute(f'INSERT INTO "active_{table}"(id, text, begin, end, channel, moder) VALUES{post}')
    con.commit()

    cursorObj.execute(f'CREATE TABLE "{table[0]}{post[0]}" ('
                      '"id"	INTEGER,'
                      '"username"	TEXT'
                      ');')
    con.commit()


def all_tables():
    return [i[0] for i in cursorObj.execute('SELECT tbl_name FROM sqlite_master WHERE type = "table"').fetchall()]


def new_member(id, username, table):
    temp = cursorObj.execute(f"SELECT id FROM {table} WHERE id = {id}").fetchall()
    if temp:
        return False
    cursorObj.execute(f"INSERT INTO {table}(id, username) VALUES{(id, username)}")
    con.commit()
    return True


def start_command(id, username):
    temp = cursorObj.execute(f"SELECT refer FROM user_info WHERE id = {id}").fetchall()
    if temp:
        if temp[0][0] >= 2:
            return True
        return False
    cursorObj.execute(f"INSERT INTO 'user_info'('id', 'username', 'using', 'refer') VALUES({id}, '{username}', 0, 0)")
    con.commit()
    return False


def new_refer(id):
    now = cursorObj.execute(f"SELECT refer FROM user_info WHERE id = {id}").fetchall()[0][0]
    print(now)
    cursorObj.execute(f"UPDATE user_info SET refer = {now + 1} WHERE id = {id}")
    con.commit()


def end_raffle(id, table):
    post = cursorObj.execute(f'SELECT * FROM active_{table} WHERE id = {id}').fetchall()[0]
    members = cursorObj.execute(f"SELECT * FROM {table[0]}{id}").fetchall()
    try:
        winner = choice(members)
    except IndexError:
        winner = (445, 'ds')
    cursorObj.execute(f'DROP TABLE {table[0]}{id}')
    cursorObj.execute(f"DELETE FROM active_{table} WHERE id = {id}")
    cursorObj.execute(
        f"INSERT INTO 'ended_raffle'('id', 'type', 'text', 'moder', 'winner_id', 'winner_username') VALUES{(id, table, post[1], post[5], winner[0], winner[1])}")
    con.commit()
    return id, table, post[1], post[5], winner[0], winner[1]


def check_win():
    pass


def check_moder(username):
    return cursorObj.execute(f"SELECT id FROM user_info WHERE username IS '{username}'").fetchall()


def get_end_raffle(id, type):
    return cursorObj.execute(f'SELECT * FROM ended_raffle WHERE "id" = {id} AND "type" = "{type}"').fetchall()


def full_end(id, type):
    cursorObj.execute(f"DELETE FROM 'ended_raffle'WHERE type IS '{type}' AND id IS '{id}'")
    con.commit()


if __name__ == "__main__":
    full_end(1, 'spons_raffle')
