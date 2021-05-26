from flask import Flask, request, render_template
from data import get_data, get_stats

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        stats = get_stats()
        return render_template('interface.html', stats=stats)

    else:
        search = request.form.get('search')
        data = get_data(search)
        stats = get_stats()
        return render_template('interface.html', data=data, stats=stats)


if __name__ == "__main__":
    app.run()
