from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request
import math
from starlette.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return templates.TemplateResponse("get.html", {"request": request, "name": name})

@app.get("/get")
def check_prime(number: int):
    """
    numberというクエリパラメータを受け取り、素数判定の結果を返すAPIエンドポイント。
    """

    is_prime_result = is_prime(number)

    # 判定結果を辞書形式で返す
    return  {
        "input_number": number,
        "is_prime": is_prime_result,
        "message": f"{number}は素数です。" if is_prime_result else f"{number}は素数ではありません。"
    }





def is_prime(number: int) -> bool:
    """与えられた整数が素数であるかを判定する関数"""
    if number <= 1:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    # 3からsqrt(number)までの奇数が割り切れるかチェック
    for i in range(3, math.isqrt(number) + 1, 2):
        if number % i == 0:
            return False

    return True

@app.get("/prime_check", response_class=HTMLResponse)
def prime_checker_page(request: Request, number: int | None = None):
    result_message = None

    # numberがクエリパラメータとして渡された場合のみ判定処理を行う
    if number is not None:
        if number <= 0:
            message = f"**{number}**は正の整数ではありません。判定できません"
            result_message = f'<span style="color: red;">{message}</span>'
        else:
            is_prime_result = is_prime(number)

            if is_prime_result:
                message = f"**{number}** は**素数**です！"
                result_message = f'<span style="color: green; font-weight: bold;">{message}</span>'
            else:
                message = f"**{number}** は**素数ではありません**。"
                result_message = f'<span style="color: red;">{message}</span>'

    # テンプレートをレンダリングして返す
    return templates.TemplateResponse(
        "prime_checker.html",
        {
            "request": request,
            "result_message": result_message,
            "input_number": number
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)