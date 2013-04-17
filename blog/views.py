from flask import render_template, request
from blog import app
from database import db_session
from models import Article
from forms import ContactForm


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
    print form.name.data
    return render_template('contact.html')
  return render_template('contact.html', form=form)

@app.errorhandler(404)
def page_not_found(error):
  return "404", 404

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
