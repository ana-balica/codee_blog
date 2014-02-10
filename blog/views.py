import os
from urlparse import urljoin

from flask import render_template, request, redirect, url_for, jsonify, abort
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask_flatpages import FlatPages
from werkzeug.contrib.atom import AtomFeed

from blog import app
from forms import ContactForm
from blog.constants import *


mail = Mail(app)
pages = FlatPages(app)


@app.route('/')
@app.route('/index/')
@app.route('/blog/')
@app.route('/blog/p/<int:page>')
def blog(page=1):
    """ Blog page with latest previews of articles displayed, also considered an
    index page

    :param page: integer that represents the number of the page to be displayed,
                 lower the number - most recent
    :return: json object with template data or rendered template
    """
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
    template = render_template('index.html', articles=latest, future=future,
                               past=past, previous_page=previous_page,
                               next_page=next_page, ajax=is_ajax)
    return jsonify({'data': template, 'title': 'Code Speculations'}) \
        if is_ajax else template


@app.route('/blog/a/<article_name>')
def article(article_name):
    """ Page with a single full text article displayed

    :param article_name: name of the article as in URL
    :return: json object with template data or rendered template
    """
    articles = (p for p in pages if 'published' in p.meta)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    for article in articles:
        if article['url'] == article_name:
            article.date = article['published'].strftime("%d %b %Y")
            article.full_body = article.html.replace(DELIMITER, '')

            template = render_template('article.html', article=article,
                                       ajax=is_ajax)
            return jsonify({'data': template,
                            'title': 'Code Speculations - ' + article['title']}) \
                if is_ajax else template
    abort(404)


@app.route('/about')
def about():
    """ About me page

    :return: json object with template data or rendered template
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # ajax = True if is_ajax else False
    template = render_template('about.html', ajax=is_ajax)
    return jsonify({'data': template, 'title': 'Code Speculations - About Ana'}) \
        if is_ajax else template


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """ Page with a simple contact form

    :return: json object with template data or rendered template
    """
    form = ContactForm(request.form)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        if form.validate():
            name, email, message = form.name.data, form.email.data, form.message.data
            message = format_mail(name, email, message)
            msg = Message('[Code Speculation] Contact',
                          sender="ana.balica@gmail.com",
                          recipients=["ana.balica@gmail.com"])
            msg.body = message
            mail.send(msg)
            form = ContactForm()
            flash_msg = 'Thank you'
            template = render_template('contact.html', form=form, ajax=is_ajax, flash_msg=flash_msg)
            return jsonify({'flash_msg': flash_msg}) if is_ajax else template
        else:
            template = render_template('contact.html', form=form, ajax_errors=is_ajax, ajax=is_ajax)
            return jsonify({'errors': template}) if is_ajax else template

    template = render_template('contact.html', form=form, ajax=is_ajax)
    return jsonify(
        {'data': template, 'title': 'Code Speculations - Contact Ana'}) \
        if is_ajax else template


@app.route('/atom.xml')
def feeds():
    """ Atom feed of latest articles

    :return: response object for the feed
    """
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


@app.template_filter('autoversion')
def autoversion_filter(filename):
    """ Modify the asset's filename by appending a version query to it, in order
    to avoid caching as the file itself is being modified

    :param filename: string filename of the asset
    :return: filename with a version query appended
    """
    fullpath = os.path.join('blog/', filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?v={1}".format(filename, timestamp)
    return newfilename


@app.errorhandler(404)
def page_not_found(error):
    """ Not found error

    :return: rendered template
    """
    return render_template('404.html'), 404


def make_external(url):
    """ Make absolute URL for articles

    :param url: relative string URL
    :return: absolute URL
    """
    return urljoin(request.url_root, url_for('article', article_name=url))


def format_mail(name, email, message):
    """ Simple formatting of a mail

    :param name: sender name
    :param email: sender email
    :param message: sender message body
    :return:
    """
    data = 'Name:\t\t' + name + '\n\n'
    data += 'Email:\t\t' + email + '\n\n'
    data += 'Message body:\n\n' + message
    return data


def extract_preview(body):
    """ Exctract article preview from a full text of an article

    :param body: full text body of an article
    :return: preview of an article
    """
    until = body.find(DELIMITER)
    return body[:until]


def get_latest_articles(page, nr_of_articles):
    """ Get the sorted articles

    :param page: page number
    :param nr_of_articles: number of articles to extract
    :return: list of latest articles
    """
    articles = (p for p in pages if 'published' in p.meta)
    sorted_articles = sorted(articles, reverse=True,
                             key=lambda p: p.meta['published'])
    start = (page - 1) * nr_of_articles
    end = page * nr_of_articles
    latest = sorted_articles[start:end]
    return latest


def get_articles_total():
    """ Get the total number of articles

    :return: total number of articles
    """
    articles = (p for p in pages if 'published' in p.meta)
    length = sum(1 for _ in articles)
    return length


def set_pagination(page, nr_of_articles, nr_of_articles_on_page):
    """ Decide if pagination is required

    :param page: page number
    :param nr_of_articles: number of articles available
    :param nr_of_articles_on_page: number of articles on a page
    :return: tuple of 2 bool values, the first one shows if pagination is required
             for the future, the second - for the past
    """
    future = True
    past = True

    if page == 1:
        future = False

    if nr_of_articles < nr_of_articles_on_page + 1:
        past = False
    return (future, past)
