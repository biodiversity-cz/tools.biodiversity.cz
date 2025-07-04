from flask import Response, Flask, request, render_template, send_file, Blueprint, jsonify, current_app, url_for
from demusExporter.process_file import process_uploaded_file
from io import BytesIO
from barcode import Code39
from barcode.writer import ImageWriter
from PIL import Image
import os

herbarium_bp = Blueprint('herbarium', __name__)

@herbarium_bp.route("/demusConvertor", methods=["GET", "POST"])
def demus():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        output_filename = uploaded_file.filename.rsplit(".", 1)[0] + "_" + export_type + "output.xlsx"
        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)

        uploaded_file.save(input_path)
        process_uploaded_file(input_path, output_path, export_type)

        return send_file(output_path, as_attachment=True)

    return render_template("herbarium/demusConvertor.html")

@herbarium_bp.route("/barcodeGenerator", methods=["GET"])
def barcodeGenerator():
        title = request.args.get("title","")
        subtitle = request.args.get("subtitle","")
        prefix = request.args.get("prefix","")
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        query_params = {k: v for k, v in {
            "title": title,
            "subtitle": subtitle,
            "prefix": prefix,
            "start": start,
            "end": end
        }.items() if v is not None}

        values = []
        if start is not None and end is not None and prefix is not None:
            values = [f"{prefix} {i}" for i in range(start, end + 1)]

        return render_template(
            "herbarium/barcodeGenerator.html",
            title=title,
            subtitle=subtitle,
            prefix=prefix,
            start=start if start is not None else "",
            end=end if end is not None else "",
            queryParams=query_params,
            values=values)

@herbarium_bp.route("/barcode/<path:text>")
def barcode(text):
    if not text:
        img = Image.new("RGB", (1, 20), color=(255, 255, 255))
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "max-age=86400"})

    barcode = Code39(
        text,
        writer=ImageWriter(),
        add_checksum=False
    )

    options = {
        "module_width": 0.2,
        "module_height": 5.0,
        "write_text": False,
        "text_distance": 0,
        "quiet_zone": 0.8
    }

    buf = BytesIO()
    barcode.write(buf, options=options)
    buf.seek(0)

    return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "max-age=86400"})