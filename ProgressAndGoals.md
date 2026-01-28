# Progress and Goals

## 1. Completed Work

### Backend and API
- Created an API server for a geographic database consisting of countries, cities, and states
- Implemented 12+ CRUD API endpoints for countries, cities, and states
- Implemented unit tests for each API endpoint
- Wrote Swagger documentation for each endpoint
- Deployed backend on PythonAnywhere using CI/CD
- Cached data in RAM for countries, cities, and states

### Requirements Met
- RESTful API design
- Persistent data storage
- Automated testing
- API documentation
- Deployment and CI/CD
- Performance optimization through caching

## 2. Goals for This Semester

### Global Exploration and Journaling
- Event finder based on user location
- Restaurant locator
- Travel information lookup
- Museum discovery
- Photo journaling that ties photos to the user’s geographic location
- World API integration for globe-based visualization with photos and text
- Library and book discovery using WorldCat (https://search.worldcat.org/)

### Development Goals
- Learn full-stack development
- Collaborate effectively and divide work equally
- Build a React frontend
- Implement frontend unit testing
- Link frontend to backend APIs
- Deploy frontend using Vercel

## 3. User Requirements for AXiS Student Marketplace

### General
- Homepage displaying available items listed by students within proximity or school affiliation
- Location-aware browsing and search
- Support for buying, selling, pickup, and drop-off transactions

### Nice-to-Haves
- Optional map or globe-based visualization
- Items can be searched and filtered by distance radius (e.g., within 1 mile)
- Items can be searched by ZIP code or geographic coordinates
- Items can be filtered by school affiliation or dorm
- Recommend items based on proximity to the user
- Automatically derive item location from photo metadata when available

### Users
- Target audience: students
- Inspiration: NYU Swap Store
- Users can create accounts to post items, browse items, and filter by school affiliation
- Users can edit and delete their own accounts and posts
- User authentication is required for posting items
- Passwords are stored using secure hashing
- Each user provides school affiliation and a verified school email address
- School email is validated using the world university domain database
- Each user provides a default location or dorm

### Items
- Each item includes a title
- Each item includes a description
- Each item includes one or more images
- Each item includes a transaction type (buy, sell, pickup, or drop-off)
- Each item includes a geographic location (ZIP code or latitude/longitude)
- Each item is associated with the user who posted it
- Users can create, edit, and delete their own item listings
- Items are stored in a shared, global database

### Transactions
- Each item clearly indicates its transaction method
- Transaction methods include buy, sell, pickup, and drop-off
- Nice-to-have: users receive notifications or confirmations when a transaction is completed

## 4. User Requirements for the Museum Photo App

### General
- Digital museum built from user-captured photos of art pieces
- The app identifies the geographic source location of a photo
- Each photo becomes a museum-style exhibit with contextual information
- The app supports exploration by location, theme, and time

### Users
- Users can create an account
- Users can take and upload photos
- Users can view exhibits they have created
- Users can explore public exhibits created by others
- Users can edit and delete their own exhibits

### Photos and Exhibits
- Uploading or taking a photo creates an exhibit
- Each exhibit includes a photo
- Each exhibit includes the capture date and time
- Each exhibit includes geographic location
- Each exhibit includes a title and optional description
- Each exhibit includes historical background information
- Exhibits may include facts when available
- Artist, architect, or creator credits are shown when available
- Exhibits are stored in a centralized database
