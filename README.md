# Tomozart Art Gallery Web Site
![Example Image](static/images/responsiveviews.jpg)
## Introduction:
### Welcome to Tomo's Art Gallery, the official online art space of Thomas A Overment, also known as Tomo. This web page showcases a vibrant collection of Tomo's artwork, ranging from dynamic spray paintings to intricate mixed media canvas works. Whether you're an art enthusiast or simply curious, this gallery offers a window into the creative world of Tomo.

## Overview:
### Tomo's Art Gallery is a personal project designed to provide an accessible platform for viewing, sharing, and appreciating Tomo's diverse artistic creations. Visitors can explore a variety of artworks, learn more about the artist, and stay updated with the latest additions to the collection.


View live site here : https://tomozart22-7e604b91f7b3.herokuapp.com/

## Contents:

## Features:

### View Art on the Gallery Page: 
Admins upload images and descriptions via the Django admin panel. The gallery is automatically organized with Bootstrap and is responsive to different screen sizes.

### Add a Post: 
Users can create posts with an optional image through the add post page. These posts can be viewed on the home page, edited on the edit post page, and deleted if necessary.

### Profiles: 
Users can view their draft and published posts on their profile page, where links to edit or delete these posts are provided.

### Register: 
Users can register to gain the ability to add posts and, in the future, join an optional mailing list.
Receive Notifications: Users are informed about the success or failure of their actions and their login status.

### The Blog: 
Users can view all posts but can only edit or delete their own posts.


Tomozart Gallery is accessible through all browsers and is fully responsive to different screen sizes. It meets the minimum viable product (MVP) requirements, providing a solid foundation to build upon and engage with an audience effectively.

# UX - User Experience

## Design Inspiration
The inspiration for this product comes from my experience in the art industry. It is something I have wanted to do but not been able untill this piont. I look forward too furthur developing my skills to add features to this and new projects.

The colour scheme is predominantly greyscale as neutural colours won't clash with any artwork uploaded. The header and footer are black, similar to standard black frames for artwork, because it draws attension. The background features a near-white gradient, dark at the top and light at the bottom, emulating a blue sky and resembling an artist's mount, which draws attention to the artwork. Green is used throughout as it is a productive color, symbolizing progress and action, akin to "go."

The logo features the initials of my name in green, consistent with the color scheme used throughout the site. I plan to update this logo in the future using Adobe Illustrator instead of the current version created with logo.com for time-saving purposes.

The intention behind this color scheme is to create a visually cohesive and unobtrusive environment that highlights the artwork. By using neutral and green tones, the design ensures that the viewer's attention is directed towards the art pieces themselves, enhancing their viewing experience without distractions. This thoughtful use of colors not only complements the artwork but also reinforces the gallery's aesthetic appeal and functionality.

# Colours
![Colour Scheme](static/images/colours.png)

- **8abe53 - Pistachio:**
    - Used for the Logo. A tone of green I regularly use in artwork.

- **000000 - White:**
    - Used for the Logo. A tone of green I regularly use in artwork.


- **000000 - Black:**
    - Used for the Navbar and footer and some text.

- **Fe9ecef - Anti-flash White:**
    - Used for

- **9fa6b2 - Cadet Grey:**
    - Used for

- **9188181 - Teal:**
    - Used for

- **acafaf - Silver:**
    - Used for 

- **4a4a4f - Davey's Grey:**
    - Used for 

- **e84610 - Golden Gate Bridge:**
    - Used for 

## Font

I used the Lato font, imported from Google Fonts, to maintain a clean and unobtrusive look. This choice ensures that the font does not distract from the content, allowing the artwork and other elements to take center stage.

![Lato](static/images/lato.jpg)


# Project Planning

## Strategy

The Tomozart project was approached using a blend of Agile methodology, user stories, and Kanban to ensure a flexible, user-focused, and efficient development process. This strategy allowed me to prioritize user needs, adapt to changes quickly, and maintain a steady workflow.

1. Defining the Vision and Goals
The first step in the strategy was to establish a clear vision and set of goals for the Tomozart project. The vision focused on creating an online art gallery that showcases vibrant and diverse artwork while providing an intuitive and engaging user experience. Key goals included:

Showcase artwork in a visually appealing manner.
Enable users to interact with the content by adding posts with comments and images.
Ensure accessibility across all devices and browsers.
Implement a user-friendly and aesthetically pleasing design.

2. User Stories Development
User stories were created to capture the functionalities and features from the perspective of the end users. Each user story was written in a simple format: "As a [user role], I want [feature or action] so that [reason or benefit]." This approach ensured that all features aligned with user needs and provided clear, actionable items for the development team.

### User Stories:
- Contacting the Artist: As a user, I want to use social media links to ask questions or request commissions, so that I can communicate directly with the artist.
Success Criteria:
Criterion 1: Include social media in the footer.
Criterion 2: Have a template that shows social media links on every page.

- Registration: As a user I want to sign up and register, so that I can use exclusive site features.
Success Criteria:
Criterion 1: User registration.
Criterion 2: The user should receive a confirmation email upon registration.
Criterion 3: Display error messages for invalid inputs.

- Add posts: As a user I want to easily add posts to the blog, so that I can leave interact.
Success Criteria:
Criterion 1: Add post page.
Criterion 2: Upload images as well as comment.
Criterion 3: See the uploaded posts.

- Profile: As a user, I want to , be able to register and see my posts, so that I can easily find my interaction.
Success Criteria:
Criterion 1: Have draft and published posts
Criterion 2: Only see users own posts on the profile page.
Criterion 3: Easily update or delete posts from profile page.

- Gallery: As a owner, I want to upload artwork, so that visitors can easily browse the portfolio.
Success Criteria
Criterion 1: be able to add descriptions and titles to my artwork
Criterion 2: View art individually.
Criterion 3: Easily upload from the admin panel.

- Blog: As a user I want to post updates and blog articles about work and events, so that I can keep the website updated.
Success Criteria
Criterion 1: The blog must have crud functionality.
Criterion 2: Time and date of posts.
Criterion 3: Post images as well as comments.

3. Kanban Board
![Kanban Board](static/images/kanbanUS.png)

A Kanban board was set up to map out and manage the development process visually. The board was organized into columns that depicted various stages of the workflow: To Do, In Progress, and Done. Each user story transitioned through these columns as work progressed.

Kanban Workflow:

To Do: Tasks selected as priorities for the current iteration were added to the "To Do" column, indicating they were ready to be worked on.

In Progress: Tasks currently under development were moved to this column, indicating active work.

Done: After being completed tasks were placed in the "Done" column, marking their finalization.

## Agile Practices:
Agile methodology was adopted to encourage adaptability and ongoing enhancement. The project was broken down into brief iterations, with each cycle concentrating on delivering particular features or improvements.

Iteration Planning: At the start of each iteration, I assessed the backlog and chose user stories to prioritize, considering both their importance and the resources at hand.
Retrospectives: Upon completing each iteration, I reflected on the successes and areas for improvement, identifying actionable steps to enhance future iterations.

#### User Feedback and Iteration

User feedback was regularly gathered through informal reviews and testing sessions. This input was crucial for refining and adjusting the project, ensuring that the final product aligned with user expectations and needs.

#### Improvement
I dedicated myself to continuous improvement by consistently evaluating processes and results. This involved refining user stories, enhancing the Kanban workflow, and adjusting Agile practices to better align with the project's evolving needs.

#### Conclusion
The strategy for the Tomozart project, using Agile methodology, user stories, and Kanban, allowed for a structured yet flexible approach to development. This approach ensured that the project stayed aligned with user needs, adapted to changes efficiently, and delivered a high-quality product that met the project's goals.

## Agile Methodologies - Project Management

Adopting Agile methodologies was pivotal in managing the Kanban Board Project. Agile principles emphasize iterative development, flexibility, and customer feedback, which align perfectly with the project's goals. Utilizing [Github Projects Board ](https://github.com/users/wgwhitecoding/projects/8/views/1), for planning and documenting my work was particularly beneficial. As I was developing a Kanban board application, using a similar tool for project management proved to be both inspirational and practical.

The GitHub Projects board provided a clear visual representation of tasks, progress, and priorities. This not only kept me organized but also allowed me to experience firsthand the benefits of a well-structured Kanban board. Every day, as I moved tasks from 'To Do' to 'In Progress' and finally to 'Done,' I gained insights and ideas that directly influenced the development of the Kanban Board Project.

The iterative nature of Agile allowed me to continuously improve the project. Regular reviews and adjustments ensured that the application evolved in line with user needs and feedback. This approach fostered a dynamic development environment, where adaptability and ongoing enhancement were key.

Using the GitHub Projects board for this project was a testament to the effectiveness of Kanban boards in managing workflows and maintaining productivity. It reinforced the importance of Agile methodologies in software development, driving home the value of iterative progress and constant refinement.


![kanban](static/readme/kanban.png)

### MoSCoW Prioritization

To efficiently prioritize tasks in my project, I utilized the MoSCoW method along with color-coded labels. Each task was assigned a priority level—Low, Medium, or High—based on its importance, using specific labels to clearly indicate its priority status.

This system of visual prioritization maintains clarity and focus, ensuring that the highest-priority tasks are addressed first.


## Scope Plane

As I began this project, I recognized it as an opportunity for both learning and personal development. Without any prior coding experience, I invested time in careful planning.

- Creating a user-friendly interface to enhance the overall user experience
- Implementing a responsive design to ensure accessibility across mobile, tablet, and desktop devices
- Integrating user authentication for secure access
- Developing blog management with comprehensive CRUD (Create, Read, Update, Delete) functionality
- Incorporating task management features, including task creation, editing, deletion, and prioritization
- Enabling profile management to facilitate user interaction
- Providing notifications to keep users informed

## Wireframe Template

This wireframe shows the basic structure and layout of the application. It provides a visual guide for the placement of elements. The wireframe was created using Balsamiq.

![Wireframe Home page](static/images/Wireframe.png)
## Site Layout

## Modals

Several modals are implemented throughout the application.
 
![Post](static/images/postmod.PNG)
- **Post Modal** : Provides option for user to add posts.

![Comment](static/images/commentmod.PNG)
- **Comment Modal**: Provides options for user to edit  their own posts.

![Artwork](static/images/artworkmod.PNG)
- **Artwork Modal**: For admin to upload to the Gallery.

#### Database Schema

![Database Schema](static/images/database.png)

### CSRF Tokens

CSRF (Cross-Site Request Forgery) tokens are embedded in every form to authenticate the request with the server upon submission. Without these tokens, the site could be exposed to attacks where unauthorized actions might be performed on behalf of the user, potentially compromising user data.

# Responsiveness 
The application is built to be fully responsive, ensuring accessibility across mobile, tablet, and desktop devices. It leverages Bootstrap to manage the responsive layout, ensuring that the interface adapts seamlessly to various screen sizes.

**Mobile Devices**

![Mobile](static/images/phone.PNG)

**Tablets**

![Tablet](static/images/tablet.PNG)

**Laptops**

![Laptop](static/images/laptop.PNG)

# Django Admin Interface

# Future Features

# Technologies Used

- **Django**
- **HTML**
- **JavaScript**
- **CSS**
- **SQL**
- **Git**
- **GitHub**
- **Cloudinary**
- **Heroku**

## Libraries & Frameworks

- asgiref==3.8.1
- cloudinary==1.36.0
- crispy-bootstrap5==2024.2
- cryptography==43.0.0
- dj-database-url==2.2.0
- dj3-cloudinary-storage==0.0.6
- Django==5.0.6
- django-allauth==0.63.3
- django-crispy-forms==2.2
- gunicorn==20.1.0
- pillow==10.2.0
- psycopg==3.2.1
- psycopg2==2.9.9
- PyJWT==2.8.0
- setuptools==71.1.0
- sqlparse==0.5.0
- urllib3==1.26.19
- whitenoise==6.7.0

# Testing


   


