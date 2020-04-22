import psycopg2
from database import *


if __name__ == '__main__':
    db=connectDB()
    #getWhid(db,1)
    getPackageIDFromTruckid(db,1)



