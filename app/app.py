from flask import Flask, make_response
from flask_rq2 import RQ

import logging

app = Flask('app')
app.config.from_object('app.config')

rq = RQ(async=app.config.get('DEBUG', False))
rq.init_app(app)

if app.config.get('DEBUG'):
    loglevel = logging.DEBUG
    from httplib import HTTPConnection
    HTTPConnection.debuglevel = 2
else:
    loglevel = logging.WARNING
logging.basicConfig(level=loglevel)

# votebot views depend on rq & db for jobs, import after we've created them
from views import votebot
app.register_blueprint(votebot)


@app.route('/')
def index():
    return make_response('hello from votebot')


# Add the cli commands to the app
@app.cli.command()
def generate_ma_data():
    import json
    from scripts import ma_data
    print "generating MA data"
    d = ma_data.get_archaic()
    json.dump(d, open('app/ovr_forms/massachusetts_data.json', 'w'), indent=2)
    print "wrote %d archaic community names" % len(d['archaic'])
    print "unable to match %d to city or town" % len(d['unmatched'])


@app.cli.command()
def update_s3_urls():
    import db
    print "updating form urls with signatures"
    db.update_form_urls()
    print "done"

