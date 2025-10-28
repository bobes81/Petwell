cat > README.md << 'EOF'
# 🐾 PetWell — E-commerce Platform for Pet Wellness

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/main-picture.png?raw=true" 
       alt="PetWell Homepage Preview" width="750"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/Deployed%20on-Heroku-7056bf?logo=heroku&logoColor=white"/>
  <img src="https://img.shields.io/badge/Cloudinary-Integrated-blueviolet?logo=cloudinary&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey"/>
</p>

**PetWell** is a full-stack Django e-commerce platform designed to promote holistic pet wellness and mindful living.  
Created as **Portfolio Project 5** for the *Code Institute Diploma in Full Stack Software Development*, it demonstrates advanced Django architecture, user-centered design, and marketing automation via newsletter integration.  
Every part of this project — from code to content — was developed with empathy, functionality, and sustainability in mind. PetWell offers a professional and calming digital environment for users seeking quality wellness products for their pets while fostering trust, education, and compassion.

---

## 🌟 Overview
PetWell is built around a modular Django structure that connects multiple apps into one cohesive platform: **Shop**, **Cart**, **Checkout**, **Blog**, and **Newsletter**.  
Each app plays a specific role in creating a seamless user experience. The Shop lets users browse items; the Cart stores their selections; the Checkout ensures secure payment and confirmation; the Blog inspires and educates; and the Newsletter keeps the connection alive beyond the website visit.  
This platform isn’t just about transactions — it’s about relationships and long-term engagement. The architecture follows Django’s MTV (Model-Template-View) pattern, separating logic from presentation and ensuring maintainability.  
Data is stored in a **PostgreSQL** database hosted on Heroku, while images are delivered through **Cloudinary** to optimize speed and reliability.  
The result is a platform that combines the practicality of e-commerce with the warmth of a digital sanctuary for pet lovers.  

---

## 💡 User Experience (UX)
PetWell was designed following UX principles emphasizing simplicity, emotional connection, and accessibility.  
The **navigation bar** provides clear paths to all major sections — Home, Shop, Blog, Cart, and Checkout — with visual feedback to keep users oriented.  
A fixed footer with quick links and the newsletter subscription ensures consistent interaction opportunities.  
The **color palette** of soft whites and pastel blues (#EAF3FF) creates a peaceful tone aligned with pet wellness themes.  
UX research guided every step: intuitive placement of buttons, clear cart visibility, mobile-first layout, and responsive Bootstrap 5 components guarantee comfort across devices.  
WCAG accessibility guidelines were respected, including contrast ratios, ARIA labels, and semantic HTML for assistive technologies.  
The design evokes safety, compassion, and care — precisely what PetWell stands for.  

---

## 🎨 Design
PetWell’s design blends aesthetics with emotional storytelling.  
The homepage introduces users to a balanced, airy interface featuring animal imagery, soft gradients, and rounded corners.  
Typography uses **Open Sans** for readability and **Poppins** for headers, ensuring visual harmony and modern appeal.  
Bootstrap icons simplify navigation while maintaining consistency.  
Animations are subtle — hover highlights, fade-ins, and soft transitions — ensuring elegance without distraction.  
Cloudinary handles image optimization dynamically, reducing load time while maintaining quality.  
Every design choice aligns with the goal: to make users feel calm, respected, and connected with their pets.  
Even error pages follow the same brand tone — gentle and reassuring instead of technical or alarming.  

---

## 🛍️ Shop
The **Shop app** is the heart of PetWell’s commercial system.  
It retrieves product data from the PostgreSQL database and displays it dynamically on the front end.  
Each product has a name, description, price, category, and Cloudinary image, making it easy for admins to manage and for users to explore.  
Filtering and sorting functions help users find products by category or price, improving usability and reducing friction.  
The Shop uses Django ORM queries to fetch products efficiently, ensuring scalability even with hundreds of entries.  
Administrators can add or edit products directly in the Django admin dashboard or through custom forms with validation.  
The clean product layout and consistent formatting maintain visual coherence across the catalog.  
This module ensures PetWell’s primary goal — promoting mindful pet wellness through trusted, well-presented products — is achieved both technically and emotionally.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/shop.jpeg?raw=true" 
       alt="PetWell Shop Page" width="700"/>
</p>

---

## 🧺 Cart
The **Cart app** handles session-based item management.  
When a user clicks “Add to Cart”, the product ID, quantity, and price are stored temporarily in the browser session, allowing navigation between pages without data loss.  
Real-time cart counters and update buttons give users instant feedback, improving engagement and trust.  
The cart view dynamically calculates total costs and handles quantity changes or removals without reloading the page.  
This functionality was built with Django’s session framework — lightweight and secure for temporary data storage.  
Form validation prevents invalid entries or negative quantities, maintaining data consistency.  
From a UX standpoint, the cart experience is smooth and frustration-free, ensuring customers feel in control of their choices.  
The cart connects directly to Checkout, transferring verified order data to the payment gateway securely.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/cart.jpg?raw=true" 
       alt="PetWell Cart Page" width="700"/>
</p>

---

## 💳 Checkout
The **Checkout app** integrates **Stripe** for secure online payments.  
When the user proceeds to checkout, order details are validated, and Stripe’s client-side API handles card authentication.  
Upon success, Stripe returns a confirmation token which Django saves in the database alongside the order details.  
The system sends an automated email receipt confirming the purchase, ensuring transparency and trust.  
Customers are redirected to a success page showing order summary and estimated delivery details.  
Admins can view all transactions from the Django admin interface.  
Stripe’s sandbox keys were used during development, while production keys are safely stored in Heroku Config Vars for deployment.  
The checkout flow follows strict PCI compliance standards, guaranteeing user data protection.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/checkout.jpg?raw=true" 
       alt="PetWell Checkout Page" width="700"/>
</p>

---

## 🧠 Blog
The **Blog app** supports CRUD (Create, Read, Update, Delete) functionality, allowing admins or authorized users to post wellness-related articles.  
Each post includes a title, content, author, and optional Cloudinary image for visual impact.  
Visitors can read full posts or browse summaries from the main blog page.  
The app promotes user education and emotional connection, bridging product marketing and community storytelling.  
Behind the scenes, Django ORM manages database interactions, ensuring posts are stored efficiently and ordered by date.  
Security is maintained with user-based permissions — only logged-in admins can create or edit posts.  
The goal of the blog is not only content creation but community building, offering ongoing value beyond commerce.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/blog.jpg?raw=true" 
       alt="PetWell Blog Page" width="700"/>
</p>

---

## 💌 Newsletter & Email Confirmation
The newsletter feature completes PetWell’s marketing ecosystem.  
At the bottom of every page, users find a **simple subscription form** to enter their email address.  
Once submitted, Django validates the entry and stores it in the `Subscriber` model within the Blog app.  
To prevent duplicates, the form checks if the email already exists in the database before saving.  
After successful subscription, the user receives an automatic **welcome email** sent via SendGrid SMTP integration.  
This email system was tested and confirmed functional in Heroku’s environment using secure API credentials.  
The system improves engagement, fulfills Code Institute’s *Digital Marketing* requirement, and sets the foundation for future campaigns such as promotions or wellness tips.  
The newsletter is a perfect example of backend logic, frontend validation, and real email communication working seamlessly together.  

---

## 🧩 How to Run This Project Locally
Follow these steps to clone, configure, and run **PetWell** locally:  

git clone https://github.com/bobes81/Petwell.git  
cd Petwell  
python3 -m venv venv  
source venv/bin/activate  # macOS/Linux  
venv\Scripts\activate     # Windows  
pip install -r requirements.txt  

Create a `.env` file in the project root with the following keys:  

SECRET_KEY=your_django_secret_key  
CLOUDINARY_URL=your_cloudinary_url  
STRIPE_PUBLIC_KEY=your_stripe_public_key  
STRIPE_SECRET_KEY=your_stripe_secret_key  
STRIPE_WH_SECRET=your_stripe_webhook_secret  
EMAIL_HOST_USER=apikey  
EMAIL_HOST_PASSWORD=your_sendgrid_api_key  
DATABASE_URL=your_postgresql_database_url  
DEBUG=True  

Then apply migrations and start the development server:  

python manage.py migrate  
python manage.py createsuperuser  
python manage.py runserver  

Once the server is running, visit:  
🌐 http://localhost:8000  
🔑 http://localhost:8000/admin  

---

## 🔮 Future Enhancements
PetWell is designed to evolve further with planned features:  

• Password reset & recovery emails via SendGrid  
• User profiles with order history and avatars  
• Wishlist for favorite products  
• Product reviews and comments  
• Admin analytics dashboard  
• Loyalty points and discount coupons  
• Multi-language & currency support  
• Redis caching and Celery async tasks  
• Automated marketing emails with templates  
• AI-driven product recommendations  

---

## Acknowledgements
  
Special thanks to ChatGPT for guidance, debugging, and creative support during development.  
PetWell is dedicated to compassion — not just for pets, but for all living beings.  

> “Caring for pets means caring for life itself.” 🐾
