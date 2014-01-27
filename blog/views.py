from urlparse import urljoin

from flask import render_template, request, flash, redirect, url_for, jsonify
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask_flatpages import FlatPages
from werkzeug.contrib.atom import AtomFeed

from blog import app
from forms import ContactForm

DELIMITER = '<p>&lt;---&gt;</p>'
ARTICLES_PER_PAGE = 10
ARTICLES_PER_FEED = 20
ME = "Ana Balica"

mail = Mail(app)
pages = FlatPages(app)


@app.route('/')
@app.route('/index/')
@app.route('/blog/')
@app.route('/blog/p/<int:page>')
def blog(page=1):
    latest = get_latest_articles(page, ARTICLES_PER_PAGE)

    if not latest:
        return redirect(url_for('blog'))

    for article in latest:
        article.date = article['published'].strftime("%d %b %Y")
        article.preview = extract_preview(article.html)
        article.full_body = article.html.replace(DELIMITER, '')

    total = get_articles_total()
    end = page * ARTICLES_PER_PAGE
    future, past = set_pagination(page, total, end)
    previous_page = page + 1
    next_page = page - 1

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    ajax = True if is_ajax else False
    template = render_template('index.html', articles=latest, future=future,
                               past=past, previous_page=previous_page,
                               next_page=next_page, ajax=ajax)
    return jsonify({'data': template, 'title': 'Code Speculations'}) \
        if is_ajax else template


@app.route('/blog/a/<article_name>')
def article(article_name):
    articles = (p for p in pages if 'published' in p.meta)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    ajax = True if is_ajax else False

    for article in articles:
        if article['url'] == article_name:
            article.date = article['published'].strftime("%d %b %Y")
            article.full_body = article.html.replace(DELIMITER, '')

            template = render_template('article.html', article=article,
                                       ajax=ajax)
            return jsonify({'data': template,
                            'title': 'Code Speculations - ' + article['title']}) \
                if is_ajax else template


@app.route('/about')
def about():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    ajax = True if is_ajax else False
    template = render_template('about.html', ajax=ajax)
    return jsonify({'data': template, 'title': 'Code Speculations - About Ana'}) \
        if is_ajax else template


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        name, email, message = form.name.data, form.email.data, form.message.data
        message = format_mail(name, email, message)
        msg = Message('[Code Speculation] Contact',
                      sender="ana.balica@gmail.com",
                      recipients=["ana.balica@gmail.com"])
        msg.body = message
        mail.send(msg)
        form = ContactForm()
        flash('Thank you')
        return render_template('contact.html', form=form)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    ajax = True if is_ajax else False
    template = render_template('contact.html', form=form, ajax=ajax)
    return jsonify(
        {'data': template, 'title': 'Code Speculations - Contact Ana'}) \
        if is_ajax else template


@app.route('/atom.xml')
def feeds():
    latest = get_latest_articles(1, ARTICLES_PER_FEED)
    feed = AtomFeed('Code Speculations', feed_url=request.url,
                    url=request.url_root)

    for article in latest:
        summary = extract_preview(article.html)
        content = article.html.replace(DELIMITER, '')
        feed.add(article['title'],
                 summary=summary,
                 content=content,
                 content_type="html",
                 author=ME,
                 url=make_external(article['url']),
                 updated=article['published'],
        )
    return feed.get_response()


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def make_external(url):
    return urljoin(request.url_root, url_for('article', article_name=url))


def format_mail(name, email, message):
    data = 'Name:\t\t' + name + '\n\n'
    data += 'Email:\t\t' + email + '\n\n'
    data += 'Message body:\n\n' + message
    return data


def extract_preview(body):
    until = body.find(DELIMITER)
    return body[:until]


def get_latest_articles(page, nr_of_articles):
    articles = (p for p in pages if 'published' in p.meta)
    sorted_articles = sorted(articles, reverse=True,
                             key=lambda p: p.meta['published'])
    start = (page - 1) * nr_of_articles
    end = page * nr_of_articles
    latest = sorted_articles[start:end]
    return latest


def get_articles_total():
    articles = (p for p in pages if 'published' in p.meta)
    length = sum(1 for _ in articles)
    return length


def set_pagination(page, nr_of_articles, nr_of_articles_on_page):
    future = True
    past = True

    if page == 1:
        future = False

    if nr_of_articles < nr_of_articles_on_page + 1:
        past = False
    return (future, past)
