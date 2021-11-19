from flask import Flask, request
import logging
import click


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho
app = Flask(__name__)



@app.route("/")
def home():
    return "<p>Welcome to the GitHub profile checker cli server!</p>"


@app.route("/cb")
def authorize():
    if request.args.get("error"):
        return "<h1>Authorization failed!</h1>"

    access_token = request.args.get("")
    return "<h1>Authorization completed successfully!</h1><p>You may now close this tab.</p>"

