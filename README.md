# **Find Your Next…**

A simple recommendation app that helps users decide **what to watch or read next** using books, movies, and genre-based matching.

# **Contributors**
* Amelia E., Maia B. Kendal S., Najmo M.

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


---

##  Architecture Overview

### **Frontend**

* HTML templates: `index.html`, `results.html`, `detail.html`
* Dynamic results UI (posters, plots, cards)
* Responsive layout 

### **Backend (Flask)**

* Calls Big Book API + TMDB API
* Maps book genres → movie genres using `GenreMap`
* Returns recommendations as JSON

---

##  External APIs

* **Big Book API** (books + genres)
* **TMDB API** (movies, posters, genres)
* **OpenLibrary Covers API** (book covers)

