### seed_data.py
from app import create_app, db
from app.models.role import Role

app = create_app('development')

def seed_roles():
    with app.app_context():
        roles_data = [
            {'role_name': 'admin', 'description': 'Administrator'},
            {'role_name': 'hotel_owner', 'description': 'Hotel Owner'},
            {'role_name': 'customer', 'description': 'Customer'}
        ]
        
        for role_data in roles_data:
            existing_role = Role.query.filter_by(role_name=role_data['role_name']).first()
            if not existing_role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"Created role: {role_data['role_name']}")
            else:
                print(f"Role already exists: {role_data['role_name']}")
        
        db.session.commit()
        print("Roles seeded successfully!")

if __name__ == '__main__':
    seed_roles()