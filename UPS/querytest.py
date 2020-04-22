import psycopg2

def connectDB():
    conn = psycopg2.connect(database = 'cugnezod', user = 'cugnezod', password = 'WY3VYXBCtpI3WhLKNbL_tP1xcW1UGmya', host = 'drona.db.elephantsql.com', port = '5432')
    return conn

if __name__ == '__main__':
    conn=connectDB()
    cursor = conn.cursor()
    sql = "SELECT username FROM auth_user;"
    #sql = "UPDATE users_package SET x=1 WHERE name = 'qiaokeli';"   
    cursor.execute(sql)
    
    rows = cursor.fetchall()
    for row in rows:
        print ("ID = ", row[0])
        #print ("NAME = ", row[1])
    conn.commit()
    conn.close()
