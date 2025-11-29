from dotenv import load_dotenv
load_dotenv()

from app import create_app
from config.config import config

app = create_app(config['development'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
