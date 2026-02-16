
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

**PetWell** PetWell is a full-stack Django e-commerce platform focused on holistic pet wellness and mindful living.
It showcases a scalable e-commerce architecture built with Django, featuring secure Stripe payment integration, newsletter automation, structured Agile development workflow, and cloud deployment.

The platform is designed to provide a seamless and trustworthy online experience where customers can explore products, access educational content, and engage with a brand built on compassion and responsible pet care.
---

## 🌟 Overview
PetWell integrates five Django apps — **Shop**, **Cart**, **Checkout**, **Blog**, and **Newsletter** — forming a cohesive and responsive platform.  
The site combines functionality with emotional design, merging commerce with community storytelling.  
Built with the **MTV architecture**, it ensures modular development, maintainability, and data integrity.  
All media files are managed through **Cloudinary**, and the live app is powered by **Heroku PostgreSQL**.  
The entire structure was designed to achieve a seamless user journey, from discovery to purchase and engagement beyond the transaction.

---

## 💡 User Experience (UX)
PetWell provides intuitive navigation through the navbar linking Home, Shop, Blog, Cart, and Checkout.  
UX testing focused on clarity, emotional appeal, and consistency across devices.  
The interface maintains balance between functionality and empathy, emphasizing **trust, wellness, and warmth**.  
Responsive design ensures smooth operation on mobile, tablet, and desktop.  
Accessibility testing confirmed compliance with **WCAG 2.1** standards.  
Soft colors (#EAF3FF), white space, and rounded shapes evoke calmness and compassion.  
Every element serves both purpose and feeling — embodying mindful design.  

---

## 🎨 Design
PetWell’s interface harmonizes beauty and usability.  
Typography: **Open Sans** and **Poppins** for clarity and warmth.  
Icons: Bootstrap Icons for consistent branding.  
Cloudinary optimizes images dynamically.  
All forms and buttons use high-contrast and accessible focus states.  
Error pages like `404.html` are gentle and friendly, maintaining tone even during user mistakes.  
The visual system builds emotional safety — turning digital interaction into a caring experience.

---

## 🛍️ Shop
The **Shop app** displays curated products from the PostgreSQL database with CRUD control for admins.  
Each product includes Cloudinary image, description, price, and category.  
Dynamic filtering allows users to browse by wellness category or cost.  
Admin users can add or edit products through Django Admin or a custom interface.  
ORM queries ensure fast and scalable performance.  
The system was tested for form validation, ensuring data accuracy and proper feedback messages.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/shop.jpeg?raw=true" width="700"/>
</p>

---

## 🧺 Cart
The **Cart app** uses Django’s session framework to store temporary cart data.  
When a user adds a product, the cart updates dynamically with item count and total cost.  
The design encourages a sense of control — users can modify quantities, remove items, or clear the cart entirely.  
Validation prevents invalid entries and negative quantities.  
All operations are handled server-side for security and consistency.

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/cart.jpg?raw=true" width="700"/>
</p>

---

## 💳 Checkout
The **Checkout app** integrates **Stripe** for secure payments.  
Each transaction generates an Order record stored in PostgreSQL, linked with user and payment metadata.  
Stripe Webhooks validate payments to prevent fraud.  
After success, users receive a confirmation email via SendGrid and are redirected to an order summary.  
Admins can view orders via Django Admin.  
Testing confirmed payment accuracy, CSRF protection, and email delivery.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/checkout.jpg?raw=true" width="700"/>
</p>

---

## 🧠 Blog
The **Blog app** supports CRUD (Create, Read, Update, Delete) functionality for articles.  
Admins can create educational or healing content promoting compassion, awareness, and trust.  
Each article includes author, title, body, and optional image.  
Posts are ordered by creation date and displayed on a responsive grid layout.  
Form validation ensures quality and consistency of content.  

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/blog.jpg?raw=true" width="700"/>
</p>

---

## 💌 Newsletter & Email System
The **Newsletter** system connects directly to the user experience through the footer form.  
Each submission validates unique emails and stores them in a `Subscriber` model.  
Successful signups trigger automatic **welcome emails** via **SendGrid**.  
This fulfills the *Digital Marketing* requirement of the Code Institute project.  
It demonstrates end-to-end integration: form validation, database logic, and live email communication.  

---

## 💼 E-commerce Business Model & Marketing Strategy
PetWell operates under a **B2C (Business to Consumer)** model, offering physical and digital wellness products for pets.  
The marketing approach combines **content marketing (Blog)**, **email marketing (Newsletter)**, and **social media presence (Facebook/Instagram)**.  
The blog enhances SEO ranking and authority, newsletters improve retention, and social channels attract new customers through emotional engagement.  
Trust, compassion, and education form the core of PetWell’s strategy — creating a meaningful, ethical, and lasting customer relationship.

---

## 🧭 Agile Methodology
Development followed Agile methodology using **GitHub Projects** Kanban board.  
Each **User Story** included acceptance criteria and was linked to Epics (Shop, Checkout, Blog, Marketing).  
Work was organized in sprints with continuous iteration and testing.  
📋 Agile Board: [View on GitHub Projects](https://github.com/users/bobes81/projects)  

| ID | User Story | Epic | Status |
|----|-------------|------|--------|
| 1 | Browse products | Shop | ✅ Done |
| 2 | Add to cart | Cart | ✅ Done |
| 3 | Secure checkout | Checkout | ✅ Done |
| 4 | Read blog posts | Blog | ✅ Done |
| 5 | Subscribe to newsletter | Marketing | ✅ Done |

---

## 🧪 Detailed Testing

### Manual Testing Summary
| Feature | Action | Expected Result | Status |
|----------|--------|-----------------|--------|
| Add Product | Submit valid form | Product added to DB | ✅ |
| Cart Update | Modify quantity | Updated immediately | ✅ |
| Checkout | Complete test payment | Confirmation email sent | ✅ |
| Newsletter | Submit duplicate email | Validation error displayed | ✅ |
| Blog CRUD | Create/Edit/Delete posts | Reflects instantly | ✅ |
| User Auth | Login/Logout/Register | Works seamlessly | ✅ |
| 404 Page | Enter invalid URL | Custom page displayed | ✅ |

### Validation
- **HTML/CSS** validated via [W3C Validator](https://validator.w3.org/).  
- **JavaScript** validated via [JSHint](https://jshint.com/).  
- **Python** validated with `flake8` for PEP8 compliance.  

### Accessibility
- Tested with **Chrome Lighthouse** (18/21 Accessibility, 6/6 Best Practices, 5/5 SEO).  
- ARIA labels verified on all forms, buttons, and navigation.  

### Browser & Device Testing
Tested successfully on **Chrome**, **Safari**, and **Edge** across **mobile, tablet, and desktop** resolutions.  
All layouts remained responsive via Bootstrap grid system.

---

## ⚙️ Environment Setup
Create a `.env` file in the project root with:

SECRET_KEY=your_django_secret_key  
CLOUDINARY_URL=your_cloudinary_url  
STRIPE_PUBLIC_KEY=your_stripe_public_key  
STRIPE_SECRET_KEY=your_stripe_secret_key  
STRIPE_WH_SECRET=your_stripe_webhook_secret  
EMAIL_HOST_USER=apikey  
EMAIL_HOST_PASSWORD=your_sendgrid_api_key  
DATABASE_URL=your_postgresql_database_url  
DEBUG=False  

---

## 🧩 Run the Project Locally

git clone https://github.com/bobes81/Petwell.git  
cd Petwell  
python3 -m venv venv  
source venv/bin/activate (macOS/Linux)  
venv\Scripts\activate (Windows)  
pip install -r requirements.txt  
python manage.py migrate  
python manage.py createsuperuser  
python manage.py runserver  

🌐 Visit: http://localhost:8000  
🔑 Admin: http://localhost:8000/admin  

---

## 🚀 Deployment
PetWell was deployed on **Heroku** connected to GitHub.  
Automatic deployment is triggered from the `main` branch.  
Static files managed by **Whitenoise**, media by **Cloudinary**, and database by **Heroku PostgreSQL**.  
All keys and credentials stored securely in **Heroku Config Vars**.  
Deployment verified via build logs, Stripe test mode, and manual user testing.

---

##  Future Enhancements
- Password reset & recovery emails  
- User profiles with avatars and order history  
- Wishlist & product reviews  
- Admin dashboard with analytics  
- Multi-currency and multi-language support  
- Celery async tasks & Redis caching  
- Loyalty program and discount coupons  
- AI-driven wellness recommendations  

---

##  Acknowledgements
  
PetWell is dedicated to compassion — not just for pets, but for all living beings.  

> “Caring for pets means caring for life itself.” 🐾
EOF
