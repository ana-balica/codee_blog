from flask import render_template, request, flash
from flask.ext.mail import Mail
from flask.ext.mail import Message
from blog import app
from database import db_session
from models import Article
from forms import ContactForm

mail = Mail(app)


@app.route('/')
@app.route('/index/')
@app.route('/blog')
@app.route('/blog/<int:page>')
def blog():
  articles = []
  for article in db_session.query(Article).order_by(Article.date):
    article.date = article.date.strftime("%d %b %Y")
    articles.append(article)
  return render_template('index.html', articles=articles)


@app.route('/article/<int:id>')
def article(id):
  return render_template('article.html')


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


@app.teardown_request
def shutdown_session(exception=None):
  db_session.remove()


def format_mail(name, email, message):
  data = 'Name:\t\t' + name + '\n\n'
  data += 'Email:\t\t' + email + '\n\n'
  data += 'Message body:\n\n' + message
  return data


