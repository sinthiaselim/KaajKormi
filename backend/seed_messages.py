import mysql.connector
from db import get_db_connection
import random
from datetime import datetime, timedelta

def seed_messages():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database.")
        return

    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all customers and workers with their categories
        cursor.execute("SELECT id, name FROM users WHERE role = 'customer'")
        customers = cursor.fetchall()
        
        cursor.execute("SELECT w.user_id, u.name, w.job_category FROM workers w JOIN users u ON w.user_id = u.id")
        workers = cursor.fetchall()
        
        if not customers or not workers:
            print("No customers or workers found to seed messages.")
            return

        print(f"Found {len(customers)} customers and {len(workers)} workers.")
        print("Seeding messages...")
        
        generic_inquiries = [
            "Hi, are you available?",
            "Hello, I need some help with a task.",
            "Can you work this week?",
            "I saw your profile and I'm interested in your service.",
            "Are you currently taking new bookings?",
            "Hi, someone recommended you to me. Are you free?"
        ]
        
        category_chats = {
            "electrician": [
                ("I have a flickering light in my living room. Can you check it?", "Sure, sounds like a loose connection. I can take a look."),
                ("My circuit breaker keeps tripping.", "That might be an overload or a short. I'll need to inspect the panel."),
                ("Can you install a new ceiling fan?", "Yes, I've done many of those. It usually takes about an hour.")
            ],
            "plumber": [
                ("My kitchen sink is leaking.", "I can fix that. Is it the pipe or the faucet?"),
                ("The toilet won't stop running.", "Probably a faulty flapper valve. I can replace it today."),
                ("There's no hot water in my shower.", "I'll need to check your water heater. Could be the heating element.")
            ],
            "house_help": [
                ("Are you available for general house cleaning tomorrow?", "Yes, what time would you like me to come?"),
                ("Can you help with laundry and ironing?", "Of course, that's part of my service."),
                ("I need help with deep cleaning before a party.", "I can definitely help with that. Which day is the party?")
            ],
            "driver": [
                ("Are you free for a trip to the airport tomorrow morning?", "Yes, what time is your flight?"),
                ("I need a driver for a full day trip to Comilla.", "I'm available. We should discuss the fuel and lunch arrangements."),
                ("Can you drive my kids to school for a week?", "I can do that. What's the schedule?")
            ],
            "ac_repair": [
                ("My AC isn't cooling well.", "It might need a gas recharge or a filter cleaning."),
                ("There's a strange noise coming from my outdoor unit.", "I should check the fan motor and compressor."),
                ("Can you do a seasonal servicing for two ACs?", "Yes, I offer a package deal for multiple units.")
            ],
            "painter": [
                ("I want to repaint my bedroom.", "What kind of finish are you looking for? Glossy or matte?"),
                ("How much do you charge for painting a 3-bedroom flat?", "It depends on the paint quality and the state of the walls."),
                ("Can you fix some damp spots before painting?", "Yes, I'll need to treat the dampness first so the paint lasts.")
            ],
            "tutor": [
                ("Do you teach Math for Class 8 students?", "Yes, I specialize in Science and Math for middle school."),
                ("Are you available for home tutoring in the evening?", "Yes, I have a slot open at 6 PM on weekdays."),
                ("Can you help my son prepare for his O-Level exams?", "I have experience with the Edexcel and Cambridge curriculum.")
            ]
        }
        
        closing_messages = [
            "Great, let's do it. I'll book the service now.",
            "Okay, thanks for the info. I'll get back to you.",
            "Sounds good. See you then!",
            "Perfect. I'll confirm the details in the request.",
            "Thank you! Looking forward to it."
        ]
        
        # 1. Ensure specific conversation between customer1 and worker1 if they exist
        c1 = next((u for u in customers if u['id'] == 31), customers[0]) # customer1@example.com usually gets ID 31 in seed_data
        w1 = next((w for w in workers if w['user_id'] == 1), workers[0]) # worker1@example.com usually gets ID 1
        
        def create_convo(c_id, w_info, num_msgs=3):
            cat = w_info['job_category']
            w_id = w_info['user_id']
            base_time = datetime.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            
            # Start with a category inquiry or generic
            if cat in category_chats and random.random() < 0.7:
                chat_pair = random.choice(category_chats[cat])
                messages = [chat_pair[0], chat_pair[1]]
                if num_msgs > 2:
                    messages.append(random.choice(closing_messages))
            else:
                messages = [random.choice(generic_inquiries), "Yes, I can help with that.", random.choice(closing_messages)]
            
            for i, msg_text in enumerate(messages[:num_msgs]):
                sender = c_id if i % 2 == 0 else w_id
                receiver = w_id if i % 2 == 0 else c_id
                msg_time = base_time + timedelta(minutes=i * 5)
                
                cursor.execute(
                    "INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)",
                    (sender, receiver, msg_text, msg_time)
                )

        # Create the specific test conversation
        create_convo(c1['id'], w1, 4)
        
        # 2. Create more random conversations
        for _ in range(25):
            cust = random.choice(customers)
            work = random.choice(workers)
            create_convo(cust['id'], work, random.randint(2, 4))
        
        conn.commit()
        print("Successfully seeded enhanced messages!")
        
        conn.commit()
        print("Successfully seeded messages!")
        
    except Exception as e:
        print(f"Error seeding messages: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_messages()
