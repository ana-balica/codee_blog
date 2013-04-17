from flask import Flask, render_template, request
from database import db_session
from models import Article

# from datetime import date

app = Flask(__name__)


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
  if request.method == 'POST':
    return render_template('contaact.html')
  else:
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(error):
  return "404", 404

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
  app.debug = True
  app.run()