# Safe City Prishtina

A simple website where the citizens of Prishtina can sign up, log in and report city problems (trash, damaged roads, broken streetlights and more) by placing a pin on the map.

Made with Python (Flask), SQLite, HTML, CSS, JavaScript and Leaflet with OpenStreetMap.

## How to run

1. Install Python 3.9 or newer.
2. Open a terminal inside the `safe-city-prishtina` folder.
3. (Optional but recommended) create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac / Linux: `python3 -m venv venv` then `source venv/bin/activate`
4. Install the requirement: `pip install -r requirements.txt`
5. Start the site: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

You need an internet connection, because the map tiles and the Leaflet library are loaded online.

The database file `safe_city.db` is created automatically the first time you start the site, together with a demo account and 8 demo reports in Prishtina.

Demo account: username `demo`, password `demo123`

## Open the database in DBeaver

1. In DBeaver click **Database > New Database Connection**.
2. Choose **SQLite** and click Next (DBeaver may download a small driver the first time).
3. Click **Browse** next to Path and select `safe_city.db` from the project folder.
4. Click Finish. Open **Tables** to see `users` and `reports`.

You can run queries there, for example:

```sql
SELECT r.title, r.category, r.status, u.username
FROM reports r
JOIN users u ON u.id = r.user_id
ORDER BY r.created_at DESC;
```

The table definitions are in `schema.sql`. To start again with a fresh database, stop the site, delete `safe_city.db` and start it again.

## Project structure

```
safe-city-prishtina/
    app.py              Flask server: pages, login, register and the API
    database.py         creates the database and the demo data
    schema.sql          the two tables: users and reports
    requirements.txt    Flask
    templates/          HTML pages (base layout, home, map, reports, login, register, about)
    static/css/         style.css (all the styling)
    static/js/          main.js, map-common.js, map.js, report.js
```

## How it works

- **Register / Login:** the password is never saved as plain text. `generate_password_hash` saves a hash and `check_password_hash` checks it at login. The logged-in user id is kept in the Flask session.
- **Report a problem:** only logged-in users can open the report page. The user clicks on the map, a draggable pin appears, and the form is sent to the server as JSON. The server checks everything again (title, category, description and that the pin is inside Prishtina) before saving it in the `reports` table.
- **Map:** `map.js` asks `/api/reports` for all reports and draws one pin per report. The pin color shows the category and a faded pin means the problem is resolved. Clicking a pin shows the details.
- **Reports page:** a list of all reports with filters. The owner of a report can mark it as resolved (or reopen it) and delete it.

## Database

| Table | Columns |
|-------|---------|
| users | id, username, email, password_hash, created_at |
| reports | id, user_id, title, category, description, latitude, longitude, status, created_at |

Each report belongs to one user (`reports.user_id` points to `users.id`).
