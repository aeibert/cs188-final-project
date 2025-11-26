# **Find Your Next…**

A simple recommendation app that helps users decide **what to watch or read next** using books, movies, and genre-based matching.

# **Contributors**
* Amelia E., Maia B., Kendall S., Najmo M.

##  What It Does

People often struggle to pick their next movie or book. **Find Your Next…** solves this by giving smart recommendations across both mediums.

* Enter a **book → get a movie**
* Enter a **movie → get a book**
* Or stay within the same medium
* Get genre, plot details, posters/covers, and similar titles

---

##  Features

### **Core**

* Book → Movie
* Book → Book
* Movie → Movie
* Movie → Book
* Title search
* Genre + plot display
* Similar recommendation results

### **Basic**

* Clean UI with buttons + color themes
* Posters and book covers
* Sort by rating
* Customizable number of results


---

##  Architecture Overview

### **Frontend**

* jinja HTML templates: `index.html`, `results.html`, `detail.html`
* Dynamic results UI (posters, plots, cards) using css.
* Responsive layout 

### **Backend (Flask)**

Calls Big Book API + TMDB API + OpenLibrary Covers API
* For within same medium: both Big Book and TMDB API's have built in 'recommender' functions.
* For cross-medium: maps book genres → movie genres for recommendation functions using `GenreMap`, SQL table in Azure
* Returns: recommendations as JSON

---

##  External APIs

* **Big Book API** (search for books by title/genre - returns details)
* **TMDB API** (search for movies by title/genre - returns details (including poster))
* **OpenLibrary Covers API** (uses ISBN from Big Book API to search for book covers)

