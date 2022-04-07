import mysql.connector

class Initial():
    def __init__(self):
        self.conn = mysql.connector.connect(user='root', password='root',
                                    host='127.0.0.1',
                                    port=3306,
                                    database='streamapp')
        self.initial_database()



    def checkTableExists(self, tablename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return True

        cursor.close()
        return False

    def initial_database(self):
        exist = self.checkTableExists('files') 

        if not exist:
            qs = ["""
            CREATE TABLE users (
                id int not null AUTO_INCREMENT,
                name varchar(25) not null,
                email varchar(50) not null,
                last_name varchar(50) not null,
                birth_date datetime not null,
                genre varchar(2) not null,
                approved bit, 
                role varchar(10),        
                password varchar(25) not null,  
                token varchar(60), 
                PRIMARY KEY(id)
            )
            """,
            """
             CREATE TABLE files (
                id int not null AUTO_INCREMENT,
                id_user int not null,
                name varchar(25) not null,
                ext varchar(50) not null,
                size_file_kb int not null,
                public bit not null,
                base64 BLOB,
                FOREIGN KEY (id_user) REFERENCES users(id),
                PRIMARY KEY(id)                
            )
            """,
            """
             CREATE TABLE file_share (
                id int not null AUTO_INCREMENT,
                id_user_share int not null,
                id_user_shared int not null,
                id_file int not null,
                date datetime not null,   
                FOREIGN KEY (id_file) REFERENCES files(id),
                FOREIGN KEY (id_user_share) REFERENCES users(id),
                FOREIGN KEY (id_user_shared) REFERENCES users(id),             
                PRIMARY KEY(id)
            )  
            """,
            """
             CREATE TABLE logs (
                id int not null AUTO_INCREMENT,
                date_start datetime not null,
                date_end datetime not null,
                status varchar(10) not null,
                conteudo varchar(200),                           
                PRIMARY KEY(id)
            )  
            """]

            cursor = self.conn.cursor()
            for q in qs:            
                cursor.execute(q)
            self.conn.close()

