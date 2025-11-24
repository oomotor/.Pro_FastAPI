from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
import math
from starlette.staticfiles import StaticFiles
from sqlalchemy.orm import Session  # Sessionを追加
from sqlalchemy import desc
from starlette.status import HTTP_303_SEE_OTHER


# ★★★ データベース関連のインポート（models.pyから） ★★★
# models.pyに記述されているUser, SessionLocal, Baseをインポート
from models import User, SessionLocal, Base, engine

# データベースにテーブルを作成
# models.pyで定義したBaseのメタデータを使って、全てのテーブルを作成します
Base.metadata.create_all(bind=engine)


# --------------------
# データベース接続のための依存性注入関数
# --------------------
def get_db():
    """リクエストごとに新しいDBセッションを提供し、終了時にセッションをクローズする"""
    db = SessionLocal()
    try:
        # yieldでセッションを提供（依存性注入）
        yield db
    finally:
        # 処理が完了したらセッションを閉じる
        db.close()


# --------------------

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# 以前のメモリ内リスト user_data は削除

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ----------------------------------------------------
# ★★★ DB対応版 ユーザー管理エンドポイント ★★★
# ----------------------------------------------------

# 共通処理用の関数を定義
def render_user_list(request: Request, db: Session):
    users = db.query(User).order_by(User.id.desc()).all() # 1.降順で取得
    count = len(users)           # 2.計算
    # 3.表示
    return templates.TemplateResponse("post.html", {
        "request": request,
        "users": users,
        "user_count": count
    })


# /form (GET): ユーザー登録フォームとユーザー一覧を表示
@app.get("/form", response_class=HTMLResponse)
def show_form(request: Request, db: Session = Depends(get_db)):
    """ユーザー登録フォームと、DBから取得した全ユーザー一覧を表示"""
    # テンプレートにユーザー一覧を渡す
    return render_user_list(request, db)

# /users/ (POST): フォームデータを受け取り、DBに登録
@app.post("/users/", response_class=HTMLResponse)
def add_user(
        request: Request,
        name: str = Form(...),
        age: int = Form(...),
        hobby: str = Form(...),
        db: Session = Depends(get_db)  # DBセッションを依存性注入
):
    """フォームデータを受け取り、新しいユーザーをDBに登録する"""
    # 新しいUserオブジェクトを作成
    user = User(name=name, age=age, hobby=hobby)

    # データベースに追加・コミット
    db.add(user)
    db.commit()
    #return render_user_list(request, db)
    # 直接HTMLを返さず、「/form に移動して」と命令する
    return RedirectResponse(url="/form", status_code=HTTP_303_SEE_OTHER)

# ユーザー情報の削除
@app.post("/users/delete/{user_id}", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    db.delete(user)
    db.commit()

    # users = db.query(User).all()  # 更新後のユーザー一覧を取得
    #return render_user_list(request, db)
    return RedirectResponse(url="/form", status_code=HTTP_303_SEE_OTHER)


# ----------------------------------------------------
# 既存のその他のエンドポイント（変更なし）
# ----------------------------------------------------

# 以前の /form (GET) が /form (DB対応) に置き換わっています
# 以前の /form (POST) は /users/ (DB対応) に置き換わっています

@app.get("/dot-pro")
def read_dot_pro():
    return "Hello, dot-pro!"


@app.get("/profile")
def read_profile():
    return "Hello, Ryozo!"


@app.get("/index", response_class=HTMLResponse)
def read_html():
    html_path = Path("templates/index.html")
    if not html_path.exists():
        return HTMLResponse("<h1>Error: templates/index.html not found</h1>", status_code=404)
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
    is_prime_result = is_prime(number)
    return {
        "input_number": number,
        "is_prime": is_prime_result,
        "message": f"{number}は素数です。" if is_prime_result else f"{number}は素数ではありません。"
    }


def is_prime(number: int) -> bool:
    if number <= 1:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    for i in range(3, math.isqrt(number) + 1, 2):
        if number % i == 0:
            return False
    return True


@app.get("/prime_check", response_class=HTMLResponse)
def prime_checker_page(request: Request, number: int | None = None):
    result_message = None

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