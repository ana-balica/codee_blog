from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/')
@app.route('/index/')
@app.route('/blog')
@app.route('/blog/<int:page>')
def index():
  return render_template('index.html')

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


if __name__ == '__main__':
  app.debug = True
  app.run()