from flask import Blueprint, render_template, request

review_bp = Blueprint('review', __name__, url_prefix='/review')

@review_bp.route('/', methods=['GET'])
def list_reviews():
    return render_template('review/list.html')

@review_bp.route('/create', methods=['GET', 'POST'])
def create_review():
    if request.method == 'POST':
        pass
    return render_template('review/create.html')

@review_bp.route('/<int:review_id>', methods=['GET'])
def review_detail(review_id):
    return render_template('review/detail.html', review_id=review_id)

