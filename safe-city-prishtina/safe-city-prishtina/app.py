import os
from functools import wraps

from flask import (Flask, abort, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from database import connect, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "safe-city-prishtina-dev-key")

CATEGORIES = {
    "trash": "Trash / Garbage",
    "road": "Damaged road / Pothole",
    "light": "Broken streetlight",
    "water": "Water / Sewage problem",
    "traffic": "Traffic / Parking problem",
    "other": "Other",
}

STATUSES = {"open": "Open", "resolved": "Resolved"}

LAT_MIN, LAT_MAX = 42.55, 42.75
LNG_MIN, LNG_MAX = 21.00, 21.30


def get_db():
    if "db" not in g:
        g.db = connect()
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def load_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()


@app.context_processor
def inject_globals():
    return {"categories": CATEGORIES, "statuses": STATUSES, "current_user": g.get("user")}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                return jsonify({"error": "You need to log in first."}), 401
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def report_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row["category"],
        "category_label": CATEGORIES.get(row["category"], "Other"),
        "description": row["description"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "status": row["status"],
        "created_at": row["created_at"][:10],
        "username": row["username"],
        "can_edit": g.user is not None and g.user["id"] == row["user_id"],
    }


def fetch_reports(category=None, status=None, limit=None):
    sql = ("SELECT r.*, u.username FROM reports r "
           "JOIN users u ON u.id = r.user_id")
    conditions = []
    params = []
    if category in CATEGORIES:
        conditions.append("r.category = ?")
        params.append(category)
    if status in STATUSES:
        conditions.append("r.status = ?")
        params.append(status)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY r.created_at DESC, r.id DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(limit)
    rows = get_db().execute(sql, params).fetchall()
    return [report_to_dict(row) for row in rows]


def get_report_row(report_id):
    return get_db().execute(
        "SELECT r.*, u.username FROM reports r JOIN users u ON u.id = r.user_id WHERE r.id = ?",
        (report_id,),
    ).fetchone()


def validate_report(data):
    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
    except (TypeError, ValueError):
        return None, "Please click on the map to place a pin."
    if len(title) < 3 or len(title) > 80:
        return None, "The title must have between 3 and 80 characters."
    if category not in CATEGORIES:
        return None, "Please choose a category."
    if len(description) < 10 or len(description) > 600:
        return None, "The description must have between 10 and 600 characters."
    if not (LAT_MIN <= latitude <= LAT_MAX and LNG_MIN <= longitude <= LNG_MAX):
        return None, "The pin must be placed inside Prishtina."
    return {
        "title": title,
        "category": category,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
    }, None


def is_safe_next(target):
    return bool(target) and target.startswith("/") and not target.startswith("//")


@app.route("/")
def index():
    db = get_db()
    stats = {
        "total": db.execute("SELECT COUNT(*) FROM reports").fetchone()[0],
        "open": db.execute("SELECT COUNT(*) FROM reports WHERE status = 'open'").fetchone()[0],
        "resolved": db.execute("SELECT COUNT(*) FROM reports WHERE status = 'resolved'").fetchone()[0],
        "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
    }
    return render_template("index.html", stats=stats, latest=fetch_reports(limit=3))


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/reports")
def reports_page():
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    return render_template(
        "reports.html",
        reports=fetch_reports(category or None, status or None),
        selected_category=category,
        selected_status=status,
    )


@app.route("/report/new")
@login_required
def new_report():
    return render_template("report_new.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        error = None
        if len(username) < 3 or len(username) > 30:
            error = "The username must have between 3 and 30 characters."
        elif "@" not in email or "." not in email:
            error = "Please enter a valid email address."
        elif len(password) < 6:
            error = "The password must have at least 6 characters."
        elif password != confirm:
            error = "The passwords do not match."
        else:
            exists = get_db().execute(
                "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
            ).fetchone()
            if exists:
                error = "That username or email is already registered."
        if error:
            flash(error, "error")
            return render_template("register.html", username=username, email=email)
        cursor = get_db().execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password)),
        )
        get_db().commit()
        session.clear()
        session["user_id"] = cursor.lastrowid
        flash("Welcome to Safe City Prishtina, " + username + "!", "success")
        return redirect(url_for("index"))
    return render_template("register.html", username="", email="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (username, username.lower())
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Wrong username or password.", "error")
            return render_template("login.html", username=username)
        session.clear()
        session["user_id"] = user["id"]
        flash("You are logged in.", "success")
        target = request.args.get("next", "")
        return redirect(target if is_safe_next(target) else url_for("index"))
    return render_template("login.html", username="")


@app.route("/logout")
def logout():
    session.clear()
    flash("You are logged out.", "success")
    return redirect(url_for("index"))


@app.route("/api/reports", methods=["GET"])
def api_reports():
    return jsonify(fetch_reports(request.args.get("category"), request.args.get("status")))


@app.route("/api/reports", methods=["POST"])
@login_required
def api_create_report():
    data = request.get_json(silent=True) or {}
    clean, error = validate_report(data)
    if error:
        return jsonify({"error": error}), 400
    cursor = get_db().execute(
        "INSERT INTO reports (user_id, title, category, description, latitude, longitude) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (g.user["id"], clean["title"], clean["category"], clean["description"],
         clean["latitude"], clean["longitude"]),
    )
    get_db().commit()
    return jsonify({"id": cursor.lastrowid}), 201


@app.route("/api/reports/<int:report_id>/resolve", methods=["POST"])
@login_required
def api_resolve_report(report_id):
    row = get_report_row(report_id)
    if row is None:
        abort(404)
    if row["user_id"] != g.user["id"]:
        return jsonify({"error": "You can only change your own reports."}), 403
    new_status = "open" if row["status"] == "resolved" else "resolved"
    get_db().execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    get_db().commit()
    return jsonify({"status": new_status})


@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
@login_required
def api_delete_report(report_id):
    row = get_report_row(report_id)
    if row is None:
        abort(404)
    if row["user_id"] != g.user["id"]:
        return jsonify({"error": "You can only delete your own reports."}), 403
    get_db().execute("DELETE FROM reports WHERE id = ?", (report_id,))
    get_db().commit()
    return jsonify({"deleted": True})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
