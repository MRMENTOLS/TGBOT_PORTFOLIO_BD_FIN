import sqlite3

DATABASE = 'projects.db'


class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.database)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
        return True

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __execute(self, sql):
        if not self.connect():
            return None
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error executing SQL: {e}")
            self.close()
            return None
        return True

    def __select_data(self, sql, data):
        if not self.connect():
            return None
        try:
            self.cursor.execute(sql, data)
            res = self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error selecting data: {e}")
            self.close()
            return None
        self.close()
        return res

    def __executemany(self, sql, data):
        if not self.connect():
            return None
        try:
            self.cursor.executemany(sql, data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error executing many SQL: {e}")
            self.close()
            return None
        self.close()
        return True

    def default_insert(self):
        self.__execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                user_password TEXT NOT NULL
                )""")

        self.__execute("""
                CREATE TABLE IF NOT EXISTS status (
                    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status_name TEXT NOT NULL
                    )""")

        self.__execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            project_name TEXT NOT NULL,
            description TEXT,
            url TEXT,
            status_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (status_id) REFERENCES status(status_id)
            )
            """)

        self.__execute("""
        CREATE TABLE IF NOT EXISTS skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL
        )""")

        self.__execute("""
        CREATE TABLE IF NOT EXISTS project_skills (
        project_id INTEGER,
        skill_id INTEGER,
        FOREIGN KEY (project_id) REFERENCES projects(project_id),
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )""")

        self.__executemany("INSERT INTO status(status_name) VALUES (?)", [('в планах',), ('в работе',), ('завершен',)])

    def create_user(self, user_name, user_password):
        sql = "INSERT INTO users (user_name, user_password) VALUES (?, ?)"
        return self.__executemany(sql, [(user_name, user_password)])

    def check_user(self, user_name, user_password):
        sql = "SELECT user_id from users WHERE user_name = ? AND user_password = ?"
        res = self.__select_data(sql=sql, data=(user_name, user_password))
        if res:
            return res[0][0]
        return False

    def create_project(self, user_id, project_name, description, url, status_id):
        sql = "INSERT INTO projects (user_id, project_name, description, url, status_id) VALUES (?, ?, ?, ?, ?)"
        return self.__executemany(sql, [(user_id, project_name, description, url, status_id)])

    def create_skill(self, skill_name):
        sql = "INSERT INTO skills (skill_name) VALUES (?)"
        return self.__executemany(sql, [(skill_name,)])

    def add_skill_to_project(self, project_id, skill_id):
        sql = "INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)"
        return self.__executemany(sql, [(project_id, skill_id)])

    def get_skills_for_project(self, project_id):
        sql = """
        SELECT s.skill_name FROM project_skills ps
        JOIN skills s ON s.skill_id = ps.skill_id
        WHERE ps.project_id = ?
        """
        res = self.__select_data(sql=sql, data=(project_id,))
        return [x[0] for x in res]

    def get_projects_for_user(self, user_id):
        sql = """
        SELECT project_id, project_name, description, url, status_name FROM projects 
        JOIN status ON
        status.status_id = projects.status_id
        WHERE user_id=?
        """
        res = self.__select_data(sql=sql, data=(user_id,))
        return [', '.join([str(y) for y in x]) for x in res]

    def get_project_info(self, user_id, project_name):
        sql = """
        SELECT project_name, description, url, status_name FROM projects 
        JOIN status ON
        status.status_id = projects.status_id
        WHERE project_name=? AND user_id=?
        """
        return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
        sql = f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [data])

    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?"
        self.__executemany(sql, [(skill_id, project_id)])

    def add_photo_column(self):
        """Adds a new column for storing photo paths to the projects table."""
        sql = "ALTER TABLE projects ADD COLUMN photo TEXT;"
        return self.__execute(sql)


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.default_insert()
    if manager.add_photo_column():
      print("Photo column added successfully")
    else:
      print("Error adding photo column")
