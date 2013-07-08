import os, sys
from blog import app

extensions = os.path.join( os.path.abspath(os.path.dirname(__file__)), "extensions")
sys.path.append(os.path.join(extensions))

app.run()