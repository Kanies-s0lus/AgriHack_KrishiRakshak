from flask import Blueprint,render_template
bp = Blueprint('routes', __name__,template_folder='template',static_folder='static')

@bp.route('/')
@bp.route('/home')
def home():
    print("Server Started") 
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')