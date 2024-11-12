from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    alert_days = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# Create the database
with app.app_context():
    db.create_all()


# Route for the main dashboard
@app.route('/')
def index():
    return render_template('dashboard.html')


# Route for products page
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        # Get data from form
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        alert_days = int(request.form['alert_days'])

        # Create new product
        new_product = Product(name=name, category=category, quantity=quantity, expiry_date=expiry_date, alert_days=alert_days)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products'))  # Redirect to refresh the page

    products = Product.query.all()  # Get all products from database
    return render_template('products.html', products=products)
    

# Helper function to get current time (to be used in Jinja templates)
@app.context_processor
def inject_now():
    return {'now': datetime.now}


# Route for the Alert Center page
@app.route('/alert_center')
def alert_center():
    products = Product.query.all()
    return render_template('alert_center.html', products=products, datetime=datetime)
    

# Route for the Notification page
@app.route('/notifications')
def notifications():
    notifications = get_notifications()
    return render_template('notifications.html', notifications=notifications)


# Assume this function fetches notification data from the database
# Function to fetch notifications
def get_notifications():
    # Fetch products near expiry (e.g., within the next 10 days)
    today = datetime.now().date()
    upcoming_alerts = Product.query.filter(
        Product.expiry_date <= today + timedelta(days=30),
        Product.expiry_date > today
    ).all()

    # Format notifications
    notifications = []
    for product in upcoming_alerts:
        days_left = (product.expiry_date - today).days
        notifications.append({
            "product_name": product.name,
            "expiry_date": product.expiry_date,
            "days_left": days_left,
            "message": f"{product.name} expires on {product.expiry_date}."
        })

    return notifications



# Route for the Settings page
#@app.route('/settings')
#def settings():
    #return render_template('settings.html')

# Route for the Logout functionality
#@app.route('/logout')
#def logout():
    # For now, just render a simple message or redirect to login page
    #return render_template('logout.html')  # You can adjust this as needed

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

