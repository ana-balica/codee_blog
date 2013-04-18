from flask import render_template, request, flash
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask_flatpages import FlatPages
from blog import app
from forms import ContactForm

DELIMITER = '<p>&lt;---&gt;</p>'

mail = Mail(app)
pages = FlatPages(app)

@app.route('/')
@app.route('/index/')
@app.route('/blog')
@app.route('/blog/<int:page>')
def blog():
  articles = (p for p in pages if 'published' in p.meta)
  latest = sorted(articles, reverse=True,
                    key=lambda p: p.meta['published'])
  for article in latest:
    article.date = article['published'].strftime("%d %b %Y")
    article.preview = extract_preview(latest[0].html)
    article.full_body = article.html.replace(DELIMITER, '')
  return render_template('index.html', articles=latest[:10])


@app.route('/blog/a/<article_name>')
def article(article_name):
  articles = (p for p in pages if 'published' in p.meta)
  for article in articles:
    if article['url'] == article_name:
      article.date = article['published'].strftime("%d %b %Y")
      article.full_body = article.html.replace(DELIMITER, '')
      return render_template('article.html', article=article)


@app.route('/about')
def about():
  return render_template('about.html')


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
  return render_template('contact.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
  return "404", 404


def format_mail(name, email, message):
  data = 'Name:\t\t' + name + '\n\n'
  data += 'Email:\t\t' + email + '\n\n'
  data += 'Message body:\n\n' + message
  return data

def extract_preview(body):
  until = body.find(DELIMITER)
  return body[:until]
