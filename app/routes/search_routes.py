from flask import Blueprint, render_template, request

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')
    return render_template('search/results.html', query=query)

