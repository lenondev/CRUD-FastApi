from fastapi import FastAPI, Depends, Body, Path, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, List
from unidecode import unidecode
from jwt_manager import create_jwt_token, validate_token

# Create an instance of FastAPI
app = FastAPI()
app.title = "My First API"
app.version = "0.0.1"

# validate JWT token
class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if not data:
            raise HTTPException(status_code=401, detail="Invalid authorization code")

# Create a User model
class User(BaseModel):
    email: str
    password: str

# Create a Movie model
class Movie(BaseModel):
    id: Optional[int] = Field(default=None)
    title: str = Field(default="Nueva película", min_length=5 , max_length=50)
    overview: str = Field(default="Sinopsis de la película", max_length=500)
    year: int = Field(default=2000, ge=2000, le=2023)
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    category: str = Field(default="Acción", max_length=20)

# Create a list of movies
movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': 2009,
        'rating': 7.8,
        'category': 'Acción'    
    },
    {
        'id': 2,
        'title': 'Terminator',
        'overview': "Maquina de acción creada por los humanos ...",
        'year': 2006,
        'rating': 8.5,
        'category': 'Acción'    
    }
]

# Home
@app.get("/", tags=["home"])
async def message():
    return HTMLResponse('<h1>My movie API</h1>')

# Login
@app.post("/login", tags=["auth"], response_model=dict, status_code=200)
def login(user: User) -> dict:
    if user.email == 'lenon@admin.com' and user.password == 'admin':
        token = create_jwt_token(dict(user))
        response = {
            'message': 'User logged in successfully',
            'token': token
        }
        return JSONResponse(status_code=200, content=response)
    else:
        response = {
            'message': 'Invalid credentials',
            'token': None
        }
        return JSONResponse(status_code=401, content=response)

# Get all movies
@app.get("/movies", tags=["movies"], response_model=List[Movie], status_code=200)
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)

# Get a movie by id
@app.get("/movies/{movie_id}", tags=["movies"], response_model=Movie, status_code=200)
def get_movie(movie_id: int = Path(ge=1, le=50)) -> Movie:
    for movie in movies:
        if movie['id'] == movie_id:
            return JSONResponse(status_code=200 ,content=movie)
    return JSONResponse(status_code=404, content=[])

# Filter movies by category
@app.get("/movies/", tags=["movies"], response_model=List[Movie], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=20)) -> List[Movie]:
    normalized_category = unidecode(category.lower())
    movies_by_category = []
    for movie in movies:
        if unidecode(movie['category'].lower()) == normalized_category:
            movies_by_category.append(movie)
    return JSONResponse(status_code=200, content=movies_by_category)

# Add a new movie
@app.post("/movies", tags=["movies"], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def add_movie(movie: Movie):
    movies.append(dict(movie))
    
    response = {
        'message': 'Movie added successfully',
        'movies': movies
    }
    
    return JSONResponse(status_code=201 ,content=response)

# Update just a few fields
@app.patch("/movies/{movie_id}", tags=["movies"], response_model=dict, status_code=200)
def patch_movie(movie_id: int, updated_movie: dict) -> dict:
    movie_to_update = None

    for movie in movies:
        if movie['id'] == movie_id:
            movie_to_update = movie
            break

    for key, value in updated_movie.items():
        if key in movie_to_update:
            movie_to_update[key] = value

    response = {
        'message': 'Movie updated successfully',
        'updated_movie': movie_to_update,
        'movies': movies
    }

    return JSONResponse(status_code=200, content=response)

# Update all fields
@app.put("/movies/{movie_id}", tags=["movies"], response_model=dict, status_code=200)
def put_movie(movie_id: int, movie: Movie) -> dict:
    movie_to_update = None

    for m in movies:
        if m['id'] == movie_id:
            movie_to_update = m
            break

    for key, value in dict(movie).items():
        if key in movie_to_update:
            movie_to_update[key] = value

    response = {
        'message': 'Movie updated successfully',
        'updated_movie': movie_to_update,
        'movies': movies
    }

    return JSONResponse(status_code=200, content=response)

# Delete a movie
@app.delete("/movies/{movie_id}", tags=["movies"], response_model=dict, status_code=200)
def delete_movie(movie_id: int) -> dict:
    movie_to_delete = None

    for movie in movies:
        if movie['id'] == movie_id:
            movie_to_delete = movie
            break

    if movie_to_delete is not None:
        movies.remove(movie_to_delete)
        response = {
            'message': 'Movie deleted successfully',
            'movies': movies
        }
    else:
        response = {
            'message': 'Movie not found',
            'movies': movies
        }
        return JSONResponse(status_code=404, content=response)

    return JSONResponse(status_code=200, content=response)
