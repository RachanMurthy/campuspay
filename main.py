from webapp import app, w3
import eth_connect
from webapp.models import User


if __name__ == "__main__":
    app.run(debug=True)