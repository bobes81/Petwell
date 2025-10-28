# 🐾 PetWell — E-commerce Platform for Pet Wellness

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/main-picture.png?raw=true" 
       alt="PetWell Homepage Preview" width="750"/>
</p>

**PetWell** is a full-stack Django e-commerce platform dedicated to promoting pet wellness, compassion, and mindful care.  
Developed as **Portfolio Project 5** for the *Code Institute Full Stack Software Development Diploma*, it demonstrates advanced Django e-commerce principles, Agile methodology, cloud deployment, and professional design integration.  

---

## 🌟 Overview
PetWell creates a calming and inspiring experience for pet owners who value wellness and mindful living.  
It integrates **Shop**, **Blog**, **Cart**, and **Checkout** apps in a modular Django architecture, combining empathy with functionality.

---

## 💡 User Experience (UX)
Simple, logical navigation ensures users find what they need effortlessly.  
Mobile-first design with Bootstrap, accessibility (WCAG compliance), and friendly colors build a sense of emotional connection.  
Forms include validation and helpful feedback; all pages are responsive and consistent.

---

## 🎨 Design
PetWell uses a **white and blue (#EAF3FF)** color palette symbolizing trust and serenity.  
Icons from Bootstrap and optimized Cloudinary images enhance visual clarity.  
Subtle transitions and soft typography create a mindful aesthetic reflecting the harmony between humans and animals.

---

## 📣 Facebook Business Mockup
A Facebook Business Page mockup (made in Canva) demonstrates digital marketing tone and visual identity.  

> “Because every wag, purr, and tail deserves wellness.”

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/facebook-mockup-petwell.png?raw=true" 
       alt="PetWell Facebook Business Page Mockup" width="700"/>
</p>

---

## ⚙️ Features
- **Shop:** Browse curated pet wellness products  
- **Blog:** Read, create, edit, and delete posts  
- **Cart:** Persistent shopping cart using Django sessions  
- **Checkout:** Stripe-ready secure order process  
- **Newsletter:** Subscribe via email for updates  
- **Custom 404 Page:** Branded and friendly user experience  

---

## 🛍️ Blog
CRUD functionality for posts, including Cloudinary image upload and safe edit validation.  
Front-end forms allow creation and editing without admin access.  
Pagination and SEO-optimized URLs improve usability and discoverability.

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/main-picture.png?raw=true" 
       alt="PetWell Homepage Preview" width="750"/>

---

## 💌 Newsletter Signup
The footer includes a **newsletter signup form**, storing emails in a custom `Subscriber` model.  
This supports marketing engagement and satisfies Code Institute’s *digital marketing requirement*.  
Each submission triggers a success message and prevents duplicate entries.

---

## 🧭 Agile Methodology
Agile workflow tracked via GitHub Project board:  
[👉 PetWell Agile Board](https://github.com/users/bobes81/projects)

| ID | User Story | Epic | Status |
|----|-------------|------|--------|
| 1 | Browse products | Shop | ✅ Done |
| 2 | Create blog posts | Blog | ✅ Done |
| 3 | Update cart dynamically | Cart | ✅ Done |
| 4 | Checkout securely | Checkout | ✅ Done |
| 5 | Newsletter signup | Marketing | ✅ Done |

This ensures full traceability, iterative development, and professional project management.

---

## 🚫 Custom 404 Page
> “Looks like this paw wandered off — let’s guide you home.”

The `404.html` template maintains brand consistency with humor and kindness, improving UX even in error states.  
Configured via `handler404` in `urls.py`.

<p align="center">
  <img src="https://github.com/bobes81/Petwell/blob/main/static/images/404.jpg?raw=true" 
       alt="PetWell 404 Page" width="600"/>
</p>

---

## 🌍 Marketing & SEO Strategy
PetWell includes a `robots.txt` and `sitemap.xml` for better crawling.  
Meta descriptions, alt tags, and semantic HTML improve visibility.  
Social media presence (Facebook & Instagram) strengthens brand trust.  
Tone of voice focuses on empathy and positivity — key emotional drivers for customer retention.

---

## 🧠 Manual Testing Summary
| Feature | Test | Expected Result | Status |
|----------|------|-----------------|--------|
| Add to Cart | Click Add | Item appears in cart | ✅ Pass |
| Edit Blog Post | Submit valid data | Updates successfully | ✅ Pass |
| Delete Blog Post | Confirm deletion | Post removed | ✅ Pass |
| Checkout | Submit order | Redirect to success | ✅ Pass |
| Newsletter | Submit email | Confirmation message | ✅ Pass |
| 404 | Invalid route | Custom error shows | ✅ Pass |

---

## 🔐 Security Features
- `DEBUG = False` in production  
- CSRF protection and secure forms  
- All secrets in Heroku Config Vars  
- HTTPS enforced  
- Role-based permissions (admin vs user)  

---

## 🚀 Deployment
Deployed on **Heroku** with GitHub CI/CD integration.  
- **Static files:** Whitenoise  
- **Media:** Cloudinary  
- **Database:** PostgreSQL  
- **Environment keys:** Stored securely in Heroku Config Vars  

---

## 🧰 Technologies Used
Backend: Django, Python  
Frontend: HTML5, CSS3, Bootstrap 5, JS  
Database: PostgreSQL  
Hosting: Heroku  
Media: Cloudinary  
Version Control: Git/GitHub  

---

## 🙏 Credits
Thanks to **Code Institute**, **Bootstrap Icons**, **Cloudinary**, and **Canva**.  
Special gratitude to **ChatGPT (Alex)** for assistance with debugging, documentation, and deployment polishing.

---

##  Acknowledgements
Created by **Ivan Kimpl** with love and dedication to all living beings.  
PetWell is more than code — it’s a message of compassion, balance, and light.  
“Caring for pets means caring for life itself.” 🐾

EOF

git add README.md
git commit -m "Add final README with all section texts and visual image links"
git push origin main
