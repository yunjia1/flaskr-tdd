# create_db.py
from project.app import app, db

with app.app_context():
    # create the database and the db table
    # looks at all models (Post in this case) and generates the corresponding tables in the database if they do not already exist.
    db.create_all()

    # commit the changes
    db.session.commit()    
    # now, the database (flaskr.db) is created with the necessary tables.
    