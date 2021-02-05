from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask import request
from flask import flash
import datetime
import json
from module.dubert import DubertSearch


app = Flask(__name__)

now = datetime.datetime.now()
posts = [
    {
        'author': {
            'username': 'duoBert-User'
        },
        'title': 'Welcome to Duo Bert',
        'content': '*** POC 검색 테스트 페이지입니다.***',
        'date_posted': now.strftime('%Y-%m-%d %H:%M:%S')
    }
]

# home
@app.route('/')
def index():
    return render_template("index.html", posts=posts)

# search home
@app.route('/search/')
def search():
    return render_template("search.html", title = "검색")

# elasticSearch result
@app.route('/result', methods = ['POST','GET'])
def result():
    if request.method   ==  'POST':
        data = request.form
    else:
        data = {}

    searchText = request.form['searchText'].strip()
    searchSize = request.form['searchSize']

    if not searchText :
        # print("검색 문장을 입력해주세요.")
        flash("검색 문장을 입력해주세요.")
        return render_template("search.html", title = "검색", searchResult="")
    else:
        #class 
        dubert = DubertSearch()

        #inference server api
        vector_value = []
        vector_value = dubert.search_vector(searchText)

        #es similarity
        if len(vector_value) != 0 :
            print("vector_value length:",len(vector_value))
            result_list = dubert.search_list(vector_value, searchSize)
            return render_template("result.html", title = "검색결과", searchText= searchText, result_list = result_list)
        else:
            print("검색 결과가 없습니다.")
            flash("검색 결과가 없습니다.")
            return render_template("search.html", title = "검색", searchText= searchText, searchResult="N")
        # print( json.dumps(result_list, sort_keys=True, indent=4))

    

@app.route('/about')
def about():
  return render_template('about.html', title = "About")

#bootstrap 
@app.route('/bootstrap')
def bootstrap():
    return render_template("bootstrap.html")

if __name__ == '__main__':
    app.secret_key = 'duoBertSecretKey'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=5000,  debug=True)