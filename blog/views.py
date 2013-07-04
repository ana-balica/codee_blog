from flask import render_template, request, flash, redirect, url_for, jsonify
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask_flatpages import FlatPages
from blog import app
from forms import ContactForm

DELIMITER = '<p>&lt;---&gt;</p>'
ARTICLES_PER_PAGE = 10

mail = Mail(app)
pages = FlatPages(app)


@app.route('/')
@app.route('/index/')
@app.route('/blog/')
@app.route('/blog/p/<int:page>')
def blog(page=1):
  articles = (p for p in pages if 'published' in p.meta)
  sorted_articles = sorted(articles, reverse=True,
                           key=lambda p: p.meta['published'])
  start = (page - 1) * ARTICLES_PER_PAGE
  end = page * ARTICLES_PER_PAGE
  latest = sorted_articles[start:end]

  if not latest:
    return redirect(url_for('blog'))

  for article in latest:
    article.date = article['published'].strftime("%d %b %Y")
    article.preview = extract_preview(article.html)
    article.full_body = article.html.replace(DELIMITER, '')

  future, past = set_pagination(page, len(sorted_articles), end)
  previous_page = page + 1
  next_page = page - 1

  template = render_template('index.html', articles=latest, future=future,
                            past=past, previous_page=previous_page, next_page=next_page)
  if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return jsonify({'data': template, 'title': 'Code Speculations'})
  return template


@app.route('/blog/a/<article_name>')
def article(article_name):
  articles = (p for p in pages if 'published' in p.meta)

  for article in articles:
    if article['url'] == article_name:
      article.date = article['published'].strftime("%d %b %Y")
      article.full_body = article.html.replace(DELIMITER, '')
      template = render_template('article.html', article=article)
      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'data': template, 'title': 'Code Speculations - ' + article['title']})
      return template


@app.route('/about')
def about():
  template = render_template('about.html')
  if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return jsonify({'data': template, 'title': 'Code Speculations - About Ana'})
  return template


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

  template = render_template('contact.html', form=form)
  if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return jsonify({'data': template, 'title': 'Code Speculations - Contact Ana'})
  return template


@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html'), 404


def format_mail(name, email, message):
  data = 'Name:\t\t' + name + '\n\n'
  data += 'Email:\t\t' + email + '\n\n'
  data += 'Message body:\n\n' + message
  return data


def extract_preview(body):
  until = body.find(DELIMITER)
  return body[:until]


def set_pagination(page, nr_of_articles, nr_of_articles_on_page):
  future = True
  past = True

  if page == 1:
    future = False

  if nr_of_articles < nr_of_articles_on_page + 1:
    past = False

  return (future, past)
