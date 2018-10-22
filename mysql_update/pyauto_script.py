import argparse
import os
import mysql.connector as db
from mysql.connector import errorcode

#Function definition
def run_scripts(directory, db_user, db_host, db_name, db_password, db_port=3306):
    #Try to find directory
    if os.path.isdir(directory) and os.path.exists(directory):
        try:
            #Try to connect to database
            conn = db.connect(host=db_host,database=db_name, password=db_password, user=db_user, 
                                auth_plugin='mysql_native_password')
            print conn
        # Analyze error
        except db.Error, e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print "Access denied"
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print "Database doesn't exist"
            else:
                print e
        else:
            #Create cursor: def helps us to read write data from and to database
            cursor = conn.cursor(buffered=True)
            # take the version and convert it to int to be compared
            cursor.execute("SELECT version from versionTable")
            # cursor.fetchone returns (045,) and we access it by index [0]
            version = (cursor.fetchone()[0])
            print version
            #take all scripts from Directory
            sql_scripts = os.listdir(directory)
            print sql_scripts
            #Traverse the list
            for s in sql_scripts:
                # 045.createtables.sql or 045createtables.sql traverse them and take only the digits
                print s
                v = str("".join([d for d in s if d.isdigit()]))
                print v
                if v > version:
                    #take the full path
                    file_path = os.path.join(directory, s)
                    print file_path
                    #check if is fully qualified file
                    if os.path.isfile(file_path):
                        try:
                            #open file
                            f = open(file_path, 'r')
                            #read query
                            sql_query = f.read()
                            #execute query
                            cursor.execute(sql_query)
                            #update version
                            sql_str = str("UPDATE versionTable SET version='%s'" % str(v))
                            sql_str1 = "UPDATE VersionTable SET version = LPAD( version, 3, '0')"
                            cursor.execute(sql_str)
                            cursor.execute(sql_str1)
                            #commit changes
                            conn.commit()                            
                        finally:
                            #close connection
                            f.close()
    else:
        print "Directory %s does not exits or is a file" % directory

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str,
                        help='Directory path which contains the scripts to be run.')
    parser.add_argument('-u', '--user', type=str,
                        help='Username of the database admin')
    parser.add_argument('--host', type=str,
                        help='Host on which database is running')
    parser.add_argument('-n', '--name', type=str,
                        help='Name of database')
    parser.add_argument('-p', '--password', type=str,
                        help='Password of the user')
    args = parser.parse_args()
    run_scripts(args.directory, args.user, args.host, args.name, args.password)
    