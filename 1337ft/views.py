from flask import Blueprint
from flask import render_template
from flask import render_template_string
from flask import request

from .bypass import bypass_paywall


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                content = bypass_paywall(url)
                return render_template_string(content)
            except Exception as e:
                return str(e)

    return render_template("index.html")
