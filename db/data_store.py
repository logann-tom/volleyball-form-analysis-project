import sqlite3
def get_player(name, conn : sqlite3.Connection):
    cursor = conn.cursor()
    player = cursor.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
    if(player is None):
        return None
    return player

def create_player(name, gender, conn : sqlite3.Connection):
    cursor = conn.cursor()
    gender = gender.lower()
    if(gender not in('male', 'female')):
        raise ValueError("Gender must be male or female")
    new_id = cursor.execute('INSERT into users (name, gender) VALUES (?, ?)', (name, gender),).lastrowid
    user = cursor.execute('SELECT * FROM users where id = ?', (new_id,)).fetchone()
    conn.commit()
    return user