from flask import Response, Flask, request, render_template, send_file, Blueprint, jsonify, current_app, url_for, redirect
from demusexporter.process_file import process_uploaded_file as demus_process
from museionexporter.process_file import process_uploaded_file as museion_process
from museionexporter.exportTypes import ExportTypes
from werkzeug.utils import secure_filename
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

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        name_part = filename.rsplit(".", 1)[0]
        output_filename = f"{name_part}_{export_type}_output"
        uploaded_file.save(input_path)

        if export_type == ExportTypes.DWC.value:
            output_filename += ".zip"
        else:
            output_filename += ".xlsx"
        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)

        try:
            demus_process(input_path, output_path, export_type)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            current_app.logger.exception("Chyba při zpracování souboru")
            return redirect(request.url)
        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_err:
                    current_app.logger.warning(f"Soubor {path} se nepodařilo smazat: {cleanup_err}")

    return render_template("herbarium/demusConvertor.html")

@herbarium_bp.route("/museionConvertor", methods=["GET", "POST"])
def museion():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        dwc_description = request.form["dwc_description"]
        dwc_rights = request.form["dwc_rights"]

        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        name_part = filename.rsplit(".", 1)[0]
        output_filename = f"{name_part}_{export_type}_output"
        uploaded_file.save(input_path)

        if export_type == ExportTypes.DWC.value:
            output_filename += ".zip"
        else:
            output_filename += ".xlsx"

        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)
        try:
            museion_process(input_path, output_path, export_type, dwc_description, '', '', dwc_rights)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            current_app.logger.exception("Chyba při zpracování souboru")
            return redirect(request.url)
        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_err:
                    current_app.logger.warning(f"Soubor {path} se nepodařilo smazat: {cleanup_err}")

    return render_template("herbarium/museionConvertor.html")

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