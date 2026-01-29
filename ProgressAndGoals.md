# Project Progress and Goals

---

## Completed Work

### Backend and API

- Created an API server for a geographic database consisting of countries, cities, and states
- Implemented 12+ CRUD API endpoints for countries, cities, and states
- Implemented unit tests for each API endpoint
- Wrote Swagger documentation for each endpoint
- Deployed backend on PythonAnywhere using CI/CD (found [here](https://xinyanc.pythonanywhere.com/))
  - GitHub repo found [here](https://github.com/XinYanC/AXiS)
- Cached data in RAM for countries, cities, and states

### Requirements Met

- RESTful API design
- Persistent data storage
- Automated testing
- API documentation
- Deployment and CI/CD
- Performance optimization through caching

---

## Goals for This Semester

### Development Goals

- [ ] Design and develop the full-stack web application
- [ ] Collaborate effectively and divide work equally
- [ ] Build a React frontend
  - GitHub repo found [here](https://github.com/XinYanC/AXiS_Website)
- [ ] Implement frontend unit testing
- [ ] Link frontend to backend APIs
- [ ] Deploy frontend using Vercel

---

## User Requirements for AXiS Student Marketplace

### General

- **Inspiration**: NYU Swap Store
- Homepage displaying available items listed by students within proximity or school affiliation
- Location-aware browsing and search
- Support for buying, selling, pickup, and drop-off transactions

### Users

- **Target audience**: students
- Users can create accounts to post items, browse items, and filter by school affiliation and/or location
- Users can edit and delete their own accounts and posts
- User authentication is required for transactions of an item (posting, buying, etc.)
  - Passwords are stored using secure hashing
- Each user provides:
  - school affiliation and a verified school email address
    - School email is validated using a [world university domain database](https://github.com/Hipo/university-domains-list)
  - a default location or dorm

### Item Post

- Each item post includes:
  - a title
  - description
  - one or more images
  - transaction type (buy, sell, pickup, or drop-off)
  - a geographic location (ZIP code or latitude/longitude)
- Each item is associated with the user who posted it
- Users can create, edit, and delete their own item listings
- Items are stored in a shared, global database

### Transactions

- Each item clearly indicates its transaction method
- Transaction methods include:
  - buy
  - sell
  - donation
  - pickup
  - drop-off
- **Stretch goal**: users receive notifications or confirmations when a transaction is completed

### Stretch Goals

- Map or globe-based visualization
- Items can be searched and filtered by distance radius (e.g., within 1 mile)
- Items can be searched by ZIP code or geographic coordinates
- Items can be filtered by school affiliation or dorm
- Recommend items based on proximity to the user
- Automatically derive item location from photo metadata when available
- Transaction notifications

---

## User Requirements for the Museum Photo App

### General

- Digital museum built from user-captured photos of art pieces
- The app identifies the geographic source location of a photo
- Each photo becomes a museum-style exhibit with contextual information
- The app supports exploration by location, theme, and time

### Users

- Users can:
  - create an account
  - take and upload photos
  - view exhibits they have created
  - explore public exhibits created by others
  - edit and delete their own exhibits

### Photos and Exhibits

- Uploading or taking a photo creates an _exhibit_
- Each exhibit includes:
  - a photo
  - the capture date and time
  - geographic location
  - a title and optional description
  - historical background information
- Exhibits may include the following if available:
  - fun facts
  - artist(s), architect(s), or creator credits
- Exhibits are stored in a centralized database
