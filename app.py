from flask import Flask, render_template, request, jsonify
import os
import json
import datetime


app = Flask(__name__)


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


@app.route('/sitemap.xml')
def sitemap():
    base_url = "https://crownbeeglobalservices.com"
    pages = [
        {"loc": "/", "priority": "1.0"},
        {"loc": "/about", "priority": "0.8"},
        {"loc": "/property", "priority": "0.9"},
        {"loc": "/gracefilled", "priority": "0.8"},
        {"loc": "/araoluwa", "priority": "0.8"},
        {"loc": "/audacity", "priority": "0.8"},
        {"loc": "/victory", "priority": "0.7"},
        {"loc": "/crownbee-prime", "priority": "0.7"},
        {"loc": "/amagee", "priority": "0.7"},
        {"loc": "/ayomide", "priority": "0.7"},
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += f'  <url>\n'
        xml += f'    <loc>{base_url}{page["loc"]}</loc>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'  </url>\n'
    xml += '</urlset>'

    return xml, 200, {'Content-Type': 'application/xml'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/property')
def properties():
    return render_template('properties.html')


@app.route('/service')
def services():
    return render_template('service.html')


# ============================================================
# INDIVIDUAL ESTATE PAGES
# ============================================================

@app.route('/gracefilled')
def gracefilled():
    return render_template('gracefilled.html')


@app.route('/araoluwa')
def araoluwa():
    return render_template('araoluwa.html')


@app.route('/audacity')
def audacity():
    return render_template('audacity.html')


@app.route('/victory')
def victory():
    return render_template('victory.html')


@app.route('/crownbee-prime')
def crownbee_prime():
    return render_template('crownbee-prime.html')


@app.route('/amagee')
def amagee():
    return render_template('amagee.html')


@app.route('/ayomide')
def ayomide():
    return render_template('ayomide.html')


if __name__ == '__main__':
    app.run(debug=True)