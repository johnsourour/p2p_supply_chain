from app.configs import APPLICATION_PORT
from app.application import app

if __name__ == "__main__":
  app.run(debug=True, port=APPLICATION_PORT)
