from __future__ import annotations

import random
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from .config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, RESULT_DIR, SECRET_KEY, UPLOAD_DIR
from .image_processing import VALID_ORDERS, is_allowed_filename, process_image


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    @app.get("/")
    def index():
        captcha_question = _refresh_captcha()
        return render_template(
            "index.html",
            result=None,
            orders=sorted(VALID_ORDERS),
            selected_order="bgr",
            captcha_question=captcha_question,
            suggested_timestamp=_default_timestamp(),
        )

    @app.post("/process")
    def process():
        order = request.form.get("order", "bgr").lower()
        captcha_answer = request.form.get("captcha", "").strip()
        timestamp_text = request.form.get("timestamp_text", "").strip()[:64]

        if captcha_answer != str(session.get("captcha_answer")):
            flash("Проверка не пройдена: решите пример CAPTCHA.", "error")
            return redirect(url_for("index"))

        if order not in VALID_ORDERS:
            flash("Выбран недопустимый порядок цветовых каналов.", "error")
            return redirect(url_for("index"))

        uploaded = request.files.get("image")
        if uploaded is None or not uploaded.filename:
            flash("Загрузите изображение для обработки.", "error")
            return redirect(url_for("index"))

        if not is_allowed_filename(uploaded.filename, ALLOWED_EXTENSIONS):
            flash("Поддерживаются форматы PNG, JPG, JPEG, BMP и WEBP.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(uploaded.filename)
        source = UPLOAD_DIR / filename
        uploaded.save(source)

        result = process_image(source, RESULT_DIR, order, timestamp_text)
        captcha_question = _refresh_captcha()
        flash("Изображение обработано успешно.", "success")
        return render_template(
            "index.html",
            result=result,
            orders=sorted(VALID_ORDERS),
            selected_order=order,
            captcha_question=captcha_question,
            suggested_timestamp=timestamp_text or _default_timestamp(),
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


def _default_timestamp() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def _refresh_captcha() -> str:
    left = random.randint(2, 9)
    right = random.randint(2, 9)
    session["captcha_answer"] = left + right
    return f"{left} + {right} = ?"
