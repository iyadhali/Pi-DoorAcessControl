import sqlite3
import uuid

conn = sqlite3.connect('eve.db')
conn.execute("PRAGMA foreign_keys = ON")


def intiate():

    conn.execute('''CREATE TABLE IF NOT EXISTS USERS
             (PID TEXT PRIMARY KEY     NOT NULL,
             FIRST_NAME            TEXT,
             LAST_NAME        TEXT,
             USERNAME         TEXT);''')

    conn.execute('''CREATE TABLE IF NOT EXISTS ADMINS
             (PID TEXT PRIMARY KEY     NOT NULL,
             FIRST_NAME            TEXT,
             LAST_NAME        TEXT,
             USERNAME         TEXT);''')

    conn.execute('''CREATE TABLE IF NOT EXISTS DELIVERY
             (DELIVERY_ID TEXT PRIMARY KEY     NOT NULL,
             ATTENDING         TEXT);''')

    conn.execute('''CREATE TABLE IF NOT EXISTS DELIVERY_MSG
             (DELIVERY_ID TEXT NOT NULL,
             PID            TEXT,
             MSG_ID         TEXT,
             FOREIGN KEY (delivery_id) REFERENCES delivery (delivery_id) ON DELETE CASCADE);''')

    return "Tables Created"


intiate()

# -------------Users----------------
def add_user(pid, f_name, l_name, username):
    params = (pid, f_name, l_name, username)
    conn.execute("INSERT INTO USERS (PID,FIRST_NAME,LAST_NAME, USERNAME) \
      VALUES (?, ?, ?, ?)", params);

    conn.commit()


def delete_user(pid):
    conn.execute("DELETE from USERS where pid = ?", (pid,));
    conn.commit()


def get_users():
    cur = conn.execute("SELECT pid, first_name, last_name, username from USERS")
    cur_result = cur.fetchall()
    return cur_result


def get_user(pid):
    cur = conn.execute("SELECT pid, first_name, last_name, username from USERS WHERE pid = ?", (pid,))
    cur_result = cur.fetchone()
    return cur_result


def validate_user(pid):
    cur = conn.execute("SELECT COUNT(pid) from USERS WHERE pid = ?", (pid,))
    cur_result = cur.fetchone()
    cur_result[0]
    return cur_result[0]


# ---------------Admins-------------

def add_admin(pid, f_name, l_name, username):
    params = (pid, f_name, l_name, username)
    conn.execute("INSERT INTO ADMINS (PID,FIRST_NAME,LAST_NAME, USERNAME) \
      VALUES (?, ?, ?, ?)", params);

    conn.commit()


def delete_admin(pid):
    conn.execute("DELETE from ADMINS where pid = ?", (pid,));
    conn.commit()


def get_admins():
    cur = conn.execute("SELECT pid, first_name, last_name, username from ADMINS")
    cur_result = cur.fetchall()
    return cur_result


def get_admin(pid):
    cur = conn.execute("SELECT pid, first_name, last_name, username from ADMINS WHERE pid = ?", (pid,))
    cur_result = cur.fetchone()
    return cur_result


def validate_admin(pid):
    cur = conn.execute("SELECT COUNT(pid) from ADMINS WHERE pid = ?", (pid,))
    cur_result = cur.fetchone()
    cur_result[0]
    return cur_result[0]


def add_delivery():
    delivery_id = uuid.uuid4().hex
    attending = None
    params = (delivery_id, attending)
    conn.execute("INSERT INTO DELIVERY (DELIVERY_ID,ATTENDING) \
      VALUES (?, ?)", params);
    conn.commit()
    return delivery_id


def delete_delivery(delivery_id):
    conn.execute("DELETE from DELIVERY where delivery_id = ?", (delivery_id,));
    conn.commit()


def add_delivery_msg(delivery_id, pid, msg_id):
    params = (delivery_id, pid, msg_id)
    conn.execute("INSERT INTO DELIVERY_MSG (DELIVERY_ID,PID,MSG_ID) \
      VALUES (?, ?, ?)", params);

    conn.commit()


def get_delivery_msg(deliver_id):
    cur = conn.execute("SELECT pid, msg_id from DELIVERY_MSG WHERE delivery_id = ?", (deliver_id,))
    cur_result = cur.fetchall()
    return cur_result


def get_delivery_id(pid, msg_id):
    params = (pid, msg_id)
    delivery_id = None
    cur = conn.execute("SELECT delivery_id from DELIVERY_MSG WHERE pid = ? AND msg_id = ?", params)
    cur_result = cur.fetchone()
    if cur_result:
        delivery_id = cur_result[0]
    return delivery_id


get_users()
get_delivery_msg("9bd553e35ad84f69bc3162d1b9a86a22")
get_delivery_id("123465599", "199")
