from flask import jsonify
import requests
from .app import rq


@rq.job
def submit_form(form, user, callback_url):
    status = form.submit(user)

    if form.__class__.__name__ is 'VoteDotOrg':
        # create new job for pdf check
        # TODO delay a few seconds?
        # TODO retry automatically if failed?
        get_pdf.queue(form, user, callback_url)


    # TODO
    # log form.browser final state, so we can determine sucess or error strings
    # send to votebot-api database, for simplicity

    if callback_url:
        requests.post(callback_url, jsonify(status))
    return jsonify(status)


@rq.job
def get_pdf(form, user, callback_url):
    status = form.get_download(user)
    if callback_url:
        requests.post(callback_url, jsonify(status))
    return jsonify(status)