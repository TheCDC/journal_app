The contents of the webapp package.

# api.py
Moduel that handles generating data structures from database records.

# app_init.py

Routines that instantiate the Flask app object and configure it.

# config.py

Variables that last the entire runtime of the application. Database location, log file location, etc.

# flask_app.py

Manages url endpoints and views for the app.

# forms.py

Contains wtforms class definitions. These forms handle input validation and can be easily rendered to HTML.

# models.py

SQLALchemy ORM database model definitions.

# views.py

Classes defining contexts and html rendering that are mapped to url endpoints.