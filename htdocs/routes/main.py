from flask import Response, Flask, request, render_template, send_file, Blueprint, jsonify, current_app, url_for
from demusExporter.process_file import process_uploaded_file
from io import BytesIO
from barcode import Code39
from barcode.writer import ImageWriter
from PIL import Image
import os

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")