import unittest
from datetime import datetime
from app import app, db, User, Event, Category, bcrypt
from werkzeug.security import generate_password_hash


# უნდა შექმნათ მინიმუმ 3 unit test Flask-ის pytest ან unittest
# გამოყენებით.
# 1. Route ტესტი
# 2. Login ტესტი
# 3. უფლებების ტესტი (სხვისი პოსტის შეცვლა/წაშლა)

class route_test(unittest.TestCase):
    def setUp(self):  # ავტომატურად ეშება ტესტირების დაწყებისას
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'   # ამას ვწერთ იმისთვის, რომ რეალური ბაზა არ შეიცვალოს ტესტირების დროს და შეიქმნას დროებითი ბაზა, რომელიც ტესტირების დასურლების მერე წაიშლება
        app.config['WTF_CSRF_ENABLED'] = False

        self.app = app.test_client()

        with app.app_context():
            db.create_all()                   # დროებით ბაზაში თავიდან ქმნის ყველა ცხრილს

            # სატესტო მონაცემები
            category = Category(name='category1')
            user1 = User(username='user1', email='user1@gmail.com', password = bcrypt.generate_password_hash('password123').decode('utf-8'))
            user2 = User(username='user2', email='user2@gmail.com', password = bcrypt.generate_password_hash('password123').decode('utf-8'))
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(category)
            db.session.commit()
            event = Event(title='Event1', short_description='Short description', long_description='Long description', location='Tbilisi', event_date=datetime(2024, 12, 31, 18, 0, 0), price=10.0, organizer='Organizer', user_id=user1.id, category_id=category.id)
            db.session.add(event)
            db.session.commit()

            self.event_id = event.id


    def tearDown(self):
        #  ყოველი ტესტის შემდეგ ასუფთავებს დროებით ბაზას
        with app.app_context():
            db.session.remove()
            db.drop_all()



    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.post('/login', data =dict(email='user1@gmail.com', password='password123'), follow_redirects=True) 
        self.assertEqual(response.status_code, 200)

    def test_incorrect_login(self):
        response = self.app.post('/login', data =dict(email='user1@gmail.com', password='blabla'), follow_redirects=True)
        self.assertIn(b'alert-danger', response.data) 

    
    def test_unauthorized_edit(self):
       
        self.app.post('/login', data=dict(
            email='user2@gmail.com', 
            password='password123'
        ), follow_redirects=True)

       
        response = self.app.post(f'/event/{self.event_id}/edit', data=dict(
            title='event2',
            description='description2',
            location='batumi',
            price=20.0
        ), follow_redirects=True)

    
        with app.app_context():
            event = db.session.get(Event, self.event_id)
            self.assertEqual(event.title, 'Event1')
            self.assertNotEqual(event.title, 'event2')



if __name__ == '__main__':
    unittest.main()




