from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.review_controller import ReviewController
from app.utils.decorators import login_required, role_required

review_bp = Blueprint('review', __name__, url_prefix='/review')

@review_bp.route('/', methods=['GET'])
def list_reviews():
    result = ReviewController.list_reviews()
    return render_template('review/list.html', result=result)

@review_bp.route('/<int:review_id>', methods=['GET'])
def review_detail(review_id):
    result = ReviewController.get_review(review_id)
    return render_template('review/detail.html', review_id=review_id, result=result)

@review_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_review():
    if request.method == 'POST':
        result = ReviewController.create_review()
        if result[1] == 201:
            flash('Tạo review thành công', 'success')
            review_id = result[0].get_json()['data']['review']['review_id']
            return redirect(url_for('review.review_detail', review_id=review_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Tạo review thất bại')
            except:
                error_message = 'Tạo review thất bại'
            # Lấy lại thông tin booking nếu có booking_id
            booking_id = request.form.get('booking_id', type=int) or request.args.get('booking_id', type=int)
            booking_data = None
            if booking_id:
                from app.controllers.booking_controller import BookingController
                booking_result = BookingController.get_booking(booking_id)
                if booking_result[1] == 200:
                    booking_data = booking_result[0].get_json().get('data', {}).get('booking')
            return render_template('review/create.html', error=error_message, booking=booking_data)
    
    # GET request - lấy thông tin booking nếu có booking_id
    booking_id = request.args.get('booking_id', type=int)
    booking_data = None
    if booking_id:
        from app.controllers.booking_controller import BookingController
        booking_result = BookingController.get_booking(booking_id)
        if booking_result[1] == 200:
            booking_data = booking_result[0].get_json().get('data', {}).get('booking')
    
    return render_template('review/create.html', booking=booking_data)

@review_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    if request.method == 'POST':
        result = ReviewController.update_review(review_id)
        if result[1] == 200:
            flash('Cập nhật review thành công', 'success')
            return redirect(url_for('review.review_detail', review_id=review_id))
        else:
            try:
                error_data = result[0].get_json()
                error_message = error_data.get('message', 'Cập nhật review thất bại')
            except:
                error_message = 'Cập nhật review thất bại'
            result = ReviewController.get_review(review_id)
            return render_template('review/edit.html', review_id=review_id, result=result, error=error_message)
    
    result = ReviewController.get_review(review_id)
    return render_template('review/edit.html', review_id=review_id, result=result)

@review_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    result = ReviewController.delete_review(review_id)
    if result[1] == 200:
        flash('Xóa review thành công', 'success')
    else:
        flash('Xóa review thất bại', 'error')
    return redirect(url_for('review.list_reviews'))

@review_bp.route('/<int:review_id>/response', methods=['POST'])
@role_required('admin', 'hotel_owner')
def add_response(review_id):
    result = ReviewController.add_response(review_id)
    if result[1] == 200:
        flash('Phản hồi review thành công', 'success')
    else:
        flash('Phản hồi review thất bại', 'error')
    return redirect(url_for('review.review_detail', review_id=review_id))

@review_bp.route('/<int:review_id>/response/update', methods=['POST'])
@role_required('admin', 'hotel_owner')
def update_response(review_id):
    result = ReviewController.update_response(review_id)
    if result[1] == 200:
        flash('Cập nhật phản hồi thành công', 'success')
    else:
        flash('Cập nhật phản hồi thất bại', 'error')
    return redirect(url_for('review.review_detail', review_id=review_id))

@review_bp.route('/<int:review_id>/report', methods=['POST'])
@login_required
def report_review(review_id):
    result = ReviewController.report_review(review_id)
    if result[1] == 200:
        flash('Báo cáo review thành công', 'success')
    else:
        flash('Báo cáo review thất bại', 'error')
    return redirect(url_for('review.review_detail', review_id=review_id))

@review_bp.route('/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_helpful(review_id):
    result = ReviewController.mark_helpful(review_id)
    if result[1] == 200:
        flash('Đánh dấu hữu ích thành công', 'success')
    else:
        flash('Thao tác thất bại', 'error')
    return redirect(url_for('review.review_detail', review_id=review_id))