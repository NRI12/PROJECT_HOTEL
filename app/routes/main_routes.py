from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from urllib.parse import urlencode

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    from app.controllers.main_controller import MainController
    
    data = MainController.get_home_data()
    
    return render_template('main/index.html',
                         featured_hotels=data.get('featured_hotels', []),
                         popular_cities=data.get('popular_cities', []),
                         promotions=data.get('active_promotions', []),
                         total_promotions_count=data.get('total_promotions_count', 0),
                         user_logged_in='user_id' in session)

@main_bp.route('/search')
def search_page():
    from app.controllers.search_controller import SearchController
    from app.controllers.main_controller import MainController
    
    city = request.args.get('city', '') or request.args.get('destination', '')
    checkin = request.args.get('checkin', '') or request.args.get('check_in', '')
    checkout = request.args.get('checkout', '') or request.args.get('check_out', '')
    guests_raw = request.args.get('guests', '2') or request.args.get('num_guests', '2')
    guests = str(guests_raw).split()[0] if isinstance(guests_raw, str) else str(guests_raw)
    rooms_raw = request.args.get('rooms', '1')
    rooms = str(rooms_raw).split()[0] if isinstance(rooms_raw, str) else str(rooms_raw)
    page = request.args.get('page', 1, type=int)
    sort_option = request.args.get('sort', '')
    
    selected_stars = request.args.getlist('star_rating')
    selected_amenities = request.args.getlist('amenity')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    def is_checked(param):
        value = request.args.get(param)
        if value is None:
            return False
        return str(value).lower() in ('1', 'true', 'on', 'yes')
    
    filter_state = {
        'stars': selected_stars,
        'amenities': selected_amenities,
        'min_price': min_price,
        'max_price': max_price,
        'free_cancel': is_checked('free_cancel'),
        'has_promotion': is_checked('has_promotion'),
        'is_featured': is_checked('is_featured')
    }
    
    base_filters = request.args.to_dict(flat=False)
    
    def build_query(**overrides):
        params = {k: list(v) for k, v in base_filters.items()}
        for key, value in overrides.items():
            if value is None:
                params.pop(key, None)
            else:
                params[key] = value if isinstance(value, list) else [str(value)]
        return urlencode(params, doseq=True)
    
    search_data = SearchController.search_for_web()
    all_amenities = MainController.get_all_amenities()
    
    return render_template('search/index.html',
                         hotels=search_data.get('data', []),
                         total=search_data.get('total', 0),
                         page=search_data.get('page', 1),
                         total_pages=search_data.get('total_pages', 1),
                         per_page=search_data.get('per_page', 10),
                         city=city,
                         checkin=checkin,
                         checkout=checkout,
                         guests=guests,
                         rooms=rooms,
                         sort_option=sort_option,
                         filter_state=filter_state,
                         build_query=build_query,
                         amenities=all_amenities,
                         user_logged_in='user_id' in session)
@main_bp.route('/api/search/suggestions')
def search_suggestions():
    from app.controllers.main_controller import MainController
    
    query_text = request.args.get('q', '')
    data = MainController.get_search_suggestions(query_text)
    
    return jsonify(data)

@main_bp.route('/promotions')
def promotions():
    from app.controllers.main_controller import MainController
    
    data = MainController.get_promotions_data()
    
    return render_template('main/promotions.html',
                         promotions=data.get('promotions', []),
                         user_logged_in='user_id' in session)

@main_bp.route('/about')
def about():
    return render_template('main/about.html',
                         user_logged_in='user_id' in session)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # TODO: Implement email sending or save to database
        # For now, just show success message
        flash('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html',
                         user_logged_in='user_id' in session)

