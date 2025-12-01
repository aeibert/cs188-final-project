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

---
##  Getting Started

### **1. Clone the Repository**

Clone the project into any directory you want:

```bash
git clone https://github.com/aeibert/cs188-final-project.git
cd final-project
```

### **2. Create a Virtual Environment**
```python3 -m venv .venv```

Activate it:

macOS / Linux:

```source .venv/bin/activate```


Windows (PowerShell):

```.venv\Scripts\Activate.ps1```

### **3. Install Dependencies**

```pip install -r requirements.txt```

### **4. Add Your Environment Variables**

Create a file named:

.secret.env


Inside it, add your API keys and Azure connection string:

- AZURE_SQL_CONNECTIONSTRING=your-connection-string-here

- TMDB_API_KEY=your-tmdb-api-key

- BIGBOOK_API_KEY=your-bigbook-api-key


These values are required for the app to connect to APIs and the database.

### **5. Run the App**

```uv run app.py```


Then open the app in your browser if testing locally:

http://127.0.0.1:5000

### **6. Running Tests**

This project uses pytest for backend testing.

Run all tests with:

```pytest -v```


Tests are located in:

test_app.py


All external API calls and database operations are mocked for reliability.

##  Deploying to Azure Web App

This project can be deployed using **Azure App Service** to host the Flask backend.

### **1. Prepare the Project for Deployment**
Make sure the following files are included in the repository:

- `requirements.txt` — Python dependencies  
- `startup.txt` or `startup.sh` — tells Azure how to run the app (example below)  
- `.secret.env` (NOT committed to GitHub — upload values in Azure instead)

Azure automatically detects Python apps but requires a startup command.

---

### **2. Configure Environment Variables**

In the Azure Portal, go to:

**App Service → Configuration → Application Settings**

Add the following keys:

- AZURE_SQL_CONNECTIONSTRING

- TMDB_API_KEY

- BIGBOOK_API_KEY

### **4. Deploy the Code**

You can deploy using:

- **GitHub Actions** 
- **VS Code Azure extension**
- **Zip deploy**
- or simply **push to GitHub** if connected to Azure

Once deployed, Azure will build your environment, install dependencies, and start the app.

### **5. Access the app**

Azure will provide a URL:

https://\<your-app-name\>.azurewebsites.net

