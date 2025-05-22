from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from collections import Counter

app = Flask(__name__)
DB_PATH = 'hok.db'

# -----------------------------
# DB初期化
# -----------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                hero TEXT NOT NULL,
                result TEXT NOT NULL,
                kda TEXT,
                build TEXT,
                notes TEXT,
                ally_tank INTEGER,
                ally_mage INTEGER,
                ally_assassin INTEGER,
                ally_fighter INTEGER,
                ally_marksman INTEGER,
                enemy_tank INTEGER,
                enemy_mage INTEGER,
                enemy_assassin INTEGER,
                enemy_fighter INTEGER,
                enemy_marksman INTEGER
            );
        ''')
        conn.commit()

# -----------------------------
# ホーム画面 + 検索機能 + おすすめビルド
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    query = "SELECT * FROM match_record"
    filters = []
    params = []

    if request.method == 'POST':
        hero = request.form.get('hero')
        result = request.form.get('result')

        if hero:
            filters.append("hero LIKE ?")
            params.append(f"%{hero}%")
        if result:
            filters.append("result = ?")
            params.append(result)

        if filters:
            query += " WHERE " + " AND ".join(filters)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        records = cursor.fetchall()

        # ビルドおすすめ情報集計
        cursor.execute("SELECT hero, build FROM match_record WHERE build IS NOT NULL")
        all_builds = cursor.fetchall()
        build_map = {}
        for hero, build in all_builds:
            if hero not in build_map:
                build_map[hero] = []
            build_map[hero].append(build)

        suggested_builds = {
            hero: Counter(builds).most_common(1)[0][0]
            for hero, builds in build_map.items() if builds
        }

    return render_template('index.html', records=records, suggested_builds=suggested_builds)

# -----------------------------
# 戦績登録
# -----------------------------
@app.route('/add', methods=['POST'])
def add_record():
    data = (
        request.form['date'],
        request.form['hero'],
        request.form['result'],
        request.form['kda'],
        request.form['build'],
        request.form['notes'],
        request.form.get('ally_tank', 0),
        request.form.get('ally_mage', 0),
        request.form.get('ally_assassin', 0),
        request.form.get('ally_fighter', 0),
        request.form.get('ally_marksman', 0),
        request.form.get('enemy_tank', 0),
        request.form.get('enemy_mage', 0),
        request.form.get('enemy_assassin', 0),
        request.form.get('enemy_fighter', 0),
        request.form.get('enemy_marksman', 0)
    )
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO match_record (
                date, hero, result, kda, build, notes,
                ally_tank, ally_mage, ally_assassin, ally_fighter, ally_marksman,
                enemy_tank, enemy_mage, enemy_assassin, enemy_fighter, enemy_marksman
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

