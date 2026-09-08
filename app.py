from venv import logger
import requests

from flask  import Flask, abort, render_template, redirect, request, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import PIL
import secrets
from PIL import Image
from models import db, User, Event, Category
from forms import EventForm, RegistrationForm, LoginForm, UpdateProfileForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'   # თუ მომხმარებელს სურს მიწვდეს ისეთ როუთს, რომელსაც ავტორიზაცია სჭირდება, მაგრამ არ არის ავტორიზებული, ის ავტომატურად გადამისამართდება ლოგინის გვერდზე.
login_manager.login_message = 'გთხოვთ, გაიაროთ ავტორიზაცია, რომ შეძლოთ ამ გვერდზე წვდომა.'  # შეტყობინება, რომელიც გამოჩნდება მომხმარებელს, როდესაც ის გადამისამართდება ლოგინის გვერდზე.
login_manager.login_message_category = 'warning'


logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    encoding ='utf-8',
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)


@login_manager.user_loader  # შეგვიძლია ვაკონტროლოთ სესიები და ვინ არის შემოსული. 
def load_user(user_id):
    return User.query.get(int(user_id))





@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, username=form.username.data, mobile=form.mobile.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('რეგისტრაცია წარმატებით დასრულდა! ახლა გაიარეთ ავტორიზაცია.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='რეგისტრაცია', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            logger.info(f"წარმატებული ავტორიზაცია: {user.email}")
            flash('წარმატებით გაიარეთ ავტორიზაცია!', 'success')
            return redirect(url_for('events'))
        else:
            logger.warning(f"წარუმატებელი ავტორიზაცია: {form.email.data}")
            flash('შეყვანილი მონაცემები არასწორია. გთხოვთ, სცადეთ თავიდან.', 'danger')
    return render_template('login.html', title='ავტორიზაცია', form=form)



@app.route('/logout')
def logout():
    logger.info(f"{current_user.username} სისტემიდან გავიდა.")
    logout_user()
    flash('თქვენ წარმატებით გამოხვედით სისტემიდან.', 'success')
    return redirect(url_for('login'))



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
   
    form = UpdateProfileForm(obj=current_user)
    user_events = Event.query.filter_by(user_id=current_user.id).order_by(Event.create_date.desc()).all()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file 

        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()
        logger.info(f" {current_user.username}-ის პროფილი განახლდა.")
        flash('თქვენი პროფილი წარმატებით განახლდა!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', title='პროფილი',profile_user=current_user, is_own_profile=True, form=form, user_events=user_events)




@app.route('/user/<string:username>')
def user_profile(username):

    if current_user.is_authenticated and username == current_user.username:
        return redirect(url_for('profile'))

    user = User.query.filter_by(username=username).first_or_404()
    user_events = Event.query.filter_by(user_id=user.id).order_by(Event.create_date.desc()).all()

    return render_template(
        'profile.html',
        title=f"{user.username}-ის პროფილი",
        form=None,
        profile_user=user,
        is_own_profile=False,
        user_events=user_events
    )



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename) # ვყოფთ სახელსა და გაფართოებას 
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(app.root_path, 'static', 'pictures', picture_filename)
    
    img = Image.open(form_picture)
    img.thumbnail((150, 150)) 
    img.save(picture_path)
    return picture_filename





@app.route('/')  # მთავარი გვერდი, ღონისძიებების ჩამონათვალი
@app.route('/events')
def events():
    category_id = request.args.get('category', type=int)
    if category_id:
        events_list = Event.query.filter_by(category_id=category_id).order_by(Event.create_date.desc()).all()
    else:
        events_list = Event.query.order_by(Event.create_date.desc()).all()

    categories = Category.query.all()
    return render_template('index.html', events=events_list, categories=categories, selected_category=category_id, title='ღონისძიებები')



@app.route('/about')
def about():
    return render_template('about.html', title='ჩვენ შესახებ')




@app.route('/my_events')   # მომხმარებლის ღონისძიებების ჩამონათვალი
@login_required
def my_events():
    user_events = Event.query.filter_by(user_id=current_user.id).order_by(Event.create_date.desc()).all()
    return render_template('index.html', events=user_events, title='ჩემი ღონისძიებები')



@app.route('/add_event', methods=['GET', 'POST'])  # დამატება
@login_required
def add_event():
    form = EventForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            short_description=form.short_description.data,
            long_description=form.long_description.data,
            location=form.location.data,
            event_date=form.event_date.data,
            price=form.price.data,
            organizer=form.organizer.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        logger.info(f"'{event.title}' შეიქმნა {current_user.username}-ის მიერ.")
        flash('ღონისძიება წარმატებით დაემატა!', 'success')
        return redirect(url_for('events'))
        
    return render_template('add_event.html', title='ღონისძიების დამატება', form=form)






@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])  # ღონისძიების რედაქტირება (მხოლოდ ავტორს შეუძლია)
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)

    form = EventForm(obj=event)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        event.title = form.title.data
        event.short_description = form.short_description.data
        event.long_description = form.long_description.data
        event.location = form.location.data
        event.event_date = form.event_date.data
        event.price = form.price.data
        event.organizer = form.organizer.data
        event.category_id = form.category_id.data

        db.session.commit()
        logger.info(f"ღონისძიება ID {event.id} განახლდა {current_user.username}-ის მიერ.")
        flash('ღონისძიება წარმატებით განახლდა!', 'success')
        return redirect(url_for('event_detail', event_id=event.id))

    return render_template('add_event.html', title='რედაქტირება', form=form)





# ღონისძიების წაშლა 
@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.author != current_user:
        abort(403)

    db.session.delete(event)
    logger.info(f" ღონისძიება ID {event_id} წაიშალა {current_user.username}-ის მიერ.")
    db.session.commit()
    flash('ღონისძიება წარმატებით წაიშალა!', 'success')
    return redirect(url_for('events'))


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    migebuli_monacemebi = get_weather(event.location)
    return render_template('about_event.html', event=event, monacemebi=migebuli_monacemebi, title=event.title)





def get_weather(location):
    api_key = app.config.get('WEATHER_API_KEY')
    if not api_key or not location:
        return None


    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric&lang=ka"
    
    try:
        response = requests.get(url, timeout=5)   # timeout გვჭირდება იმისთვის, რომ თუ საიტზე ხარვეზია და ინფორმაცია ვერ მოაქვს უსასრულოდ არ ელოდოს. 
        if response.status_code == 200:
            data = response.json()
            return {
                "ქალაქი": data['name'],
                "ტემპერატურა": round(data['main']['temp']),
                "აღწერა": data['weather'][0]['description'],
                "სურათი": data['weather'][0]['icon']
            }
        else:
            logging.error(f"Weather API Error: Status code {response.status_code} for location '{location}'")
            return None
    except Exception as e:     # გვჭირდება იმისთვის, რომ თუ API-ს ვერ დაუკავშირდა, openweathermap  საიტი გაითიშა ან სხვა პრობლემა შეიქმნა მთლიანი საიტი არ გაითიშოს. 
        logging.error(f"Weather API Request Failed: {e}")
        return None



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500








with app.app_context():
    db.create_all()
    if not Category.query.first():
        default_categories = [
            Category(name='კონცერტი'),
            Category(name='სპორტი'),
            Category(name='განათლება'),
            Category(name='თეატრი'),
            Category(name='კინო'),
            Category(name='კონფერენცია'),
            Category(name='სხვა')
        ]
        db.session.add_all(default_categories)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)