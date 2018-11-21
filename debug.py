from solidsea.app import create_app
import os

# for running in PyCharm debugger
if __name__=='__main__':
    os.environ['AUTHLIB_INSECURE_TRANSPORT']='1'
    os.environ['FLASK_ENV']='development'

# for running in uwsgi without installing the package
app = create_app()

# for running in PyCharm debugger
if __name__=='__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, port=app.config['PORT'])