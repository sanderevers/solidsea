from website.app import create_app
import os

app = create_app('solidsea.cfg') # instance relative

@app.cli.command()
def initdb():
    from website.models import db
    db.create_all()

# for running in PyCharm debugger
if __name__=='__main__':
    os.environ['AUTHLIB_INSECURE_TRANSPORT']='1'
    app.run(debug=True, use_debugger=False, use_reloader=False)