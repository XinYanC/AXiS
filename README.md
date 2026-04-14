# AXiS

AXiS is the backend API service used by the Swapify project.

- Deployed API base URL: `https://xinyanc.pythonanywhere.com/`
- Swapify frontend/project: `https://github.com/XinYanC/Swapify`

This service provides data and business endpoints for location data, users,
listings, login/auth, and frontend location dropdown.

## API Purpose for Swapify

Swapify uses AXiS as its central API layer for:

- CRUD and search across `cities`, `states`, `countries`, `users`, and
  `listings`
- Authentication (`login`)
- Dynamic dropdown/HATEOAS metadata for location-driven forms
- Geo-enabled city data (`latitude`/`longitude`) for the frontend map
- ETL-based data loading into MongoDB

## Data Models

The API defines the following core models in `server/endpoints.py`:

1. `cities`

- Key fields: `name`, `state_code`, `country_code`, `latitude`, `longitude`
- Note: `latitude` and `longitude` were added for map usage in Swapify frontend.

2. `countries`

- Key fields: `name`, `code`

3. `state`

- Key fields: `name`, `code`, `country_code`

4. `user`

- Key fields: `username`, `password` (hashed), `email` (`.edu`),
  `name`, `age`, `bio`, `city`, `state`, `country`, `rating`,
  `saved_listings`, `created_at`

5. `listing`

- Key fields: `title`, `description`, `images`, `transaction_type`,
  `owner`, `city`, `state`, `country`, `price`, `num_likes`, `status`

6. `login`

- Request fields: `email`, `password`
- Used by auth endpoint: `POST /auth/login`

## Endpoint Families

Primary endpoint groups:

- `cities`
- `states`
- `countries`
- `users`
- `listings`

Each resource family exposes a consistent pattern of operations like
`/read`, `/count`, `/search`, `/create`, and `/delete` (plus `/update` where applicable).

```text
https://xinyanc.pythonanywhere.com/
	/cities/{read|count|search|create|delete}
	/states/{read|count|search|create|delete}
	/countries/{read|count|search|create|delete}
	/users/{read|count|search|create|update|delete}
	/listings/{read|count|search|by-user|upload-image|create|update|delete}
	/auth/login
	/system/dropdown-form
	/system/dropdown-options
	/hello
	/endpoints
```

## Dropdown HATEOAS Endpoints

AXiS supports endpoint-driven form options for the frontend.

- `GET /system/dropdown-form`
  - Returns machine-readable form metadata and links.
- `GET /system/dropdown-options`
  - No query params: returns country options.
  - `?country_code=USA`: returns states for that country.
  - `?state_code=NY&country_code=USA`: returns matching cities.

These responses include `_links` to support HATEOAS-style discovery.

## ETL and Database Loads

ETL inputs live in the `ETL/` folder (`cities.tsv`, `states.tsv`,
`countries.tsv`, `users.tsv`, `listings.tsv`).

Load scripts in `ETL/` and data tooling in `data/` are used to ingest these datasets into MongoDB collections used by AXiS endpoints.

```text
ETL/*.tsv -> ETL/load_*.py -> MongoDB collections -> AXiS API endpoints
```

## Quick Health/Discovery Checks

- `GET /hello` returns service liveness.
- `GET /endpoints` returns the currently registered routes.

Example:

```bash
curl https://xinyanc.pythonanywhere.com/hello
curl https://xinyanc.pythonanywhere.com/endpoints
```
