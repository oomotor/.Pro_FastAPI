from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("get.html", {"request": request})

@app.get("/dot-pro")
def read_dot_pro():
    return "Hello, dot-pro!"

@app.get("/profile")
def read_profile():
    return "Hello, Ryozo!"

@app.get("/index", response_class=HTMLResponse)
def read_html():
    html_path = Path("templates/index.html")
    return html_path.read_text(encoding="utf-8")

@app.get("/hello", response_class=HTMLResponse)
def read_hello(request: Request):
    return templates.TemplateResponse("hello.html", {"request": request, "name": "FastAPI"})

@app.get("/conditional", response_class=HTMLResponse)
def read_conditional(request: Request, name: str = "Guest"):
    return templates.TemplateResponse("conditional.html", {"request": request, "name": name})

@app.get("/fizzbuzz", response_class=HTMLResponse)
def read_fizzbuzz(request: Request, number: int):
    if number % 15 == 0:
        result = "FizzBuzz"
    elif number % 5 == 0:
        result = "Buzz"
    elif number % 3 == 0:
        result = "Fizz"
    else:
        result = str(number)

    return templates.TemplateResponse(
        "fizzbuzz.html",
        {
            "request": request,
            "fizzbuzz_result": result,
            "input_number": number
        }
    )

@app.get("/greet", response_class=HTMLResponse)
def greet_user(request: Request, name: str):
    return templates.TemplateResponse("get.html", {"reqest": request, "name": name})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)