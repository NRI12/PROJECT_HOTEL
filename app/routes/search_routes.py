from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.search_controller import SearchController

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        result = SearchController.search()
        return render_template('search/results.html', result=result)
    return render_template('search/form.html')

@search_bp.route('/advanced', methods=['GET', 'POST'])
def advanced_search():
    if request.method == 'POST':
        result = SearchController.advanced_search()
        return render_template('search/advanced_results.html', result=result)
    return render_template('search/advanced_form.html')

@search_bp.route('/suggestions', methods=['GET'])
def suggestions():
    return SearchController.get_suggestions()

@search_bp.route('/history', methods=['GET'])
def history():
    result = SearchController.get_search_history()
    return render_template('search/history.html', result=result)

@search_bp.route('/history/<int:search_id>/delete', methods=['POST'])
def delete_history(search_id):
    result = SearchController.delete_search_history(search_id)
    if result[1] == 200:
        flash('Xóa lịch sử tìm kiếm thành công', 'success')
    else:
        flash('Xóa lịch sử tìm kiếm thất bại', 'error')
    return redirect(url_for('search.history'))

@search_bp.route('/check-availability', methods=['GET', 'POST'])
def check_availability():
    if request.method == 'POST':
        result = SearchController.check_availability()
        return render_template('search/availability.html', result=result)
    return render_template('search/availability_form.html')