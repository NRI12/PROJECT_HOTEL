from flask import Blueprint, render_template, request, session, jsonify

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
                         user_logged_in='user_id' in session)

@main_bp.route('/search')
def search_page():
    from app.controllers.search_controller import SearchController
    from app.controllers.main_controller import MainController
    
    city = request.args.get('city', '') or request.args.get('destination', '')
    checkin = request.args.get('checkin', '') or request.args.get('check_in', '')
    checkout = request.args.get('checkout', '') or request.args.get('check_out', '')
    guests = request.args.get('guests', '2') or request.args.get('num_guests', '2')
    page = request.args.get('page', 1, type=int)
    
    search_data = SearchController.search_for_web()
    all_amenities = MainController.get_all_amenities()
    
    return render_template('search/index.html',
                         hotels=search_data.get('hotels', []),
                         total=search_data.get('total', 0),
                         page=search_data.get('page', 1),
                         total_pages=search_data.get('total_pages', 1),
                         per_page=search_data.get('per_page', 10),
                         city=city,
                         checkin=checkin,
                         checkout=checkout,
                         guests=guests,
                         amenities=all_amenities,
                         user_logged_in='user_id' in session)

@main_bp.route('/api/search/suggestions')
def search_suggestions():
    from app.controllers.main_controller import MainController
    
    query_text = request.args.get('q', '')
    data = MainController.get_search_suggestions(query_text)
    
    return jsonify(data)

