"""/api/v1
/oauth/token - POST
/oauth/register - POST
/oauth/forgot-password - POST
/oauth/reset-password - POST

/users/me - GET
/users/me - PUT
/admin/users - GET
/admin/users/{id} - PUT
/admin/users/{id} - DELETE

/products/{id} - GET
/products - GET

/admin/products/{id} - PUT, DELETE
/admin/products - POST

/merchant/me - GET
/merchant/products - GET
/merchant/products/{id} - GET, (PUT, DELETE только для магазинов)
/merchant/products - POST(только для магазинов)

/categories - GET
/categories/{id} - GET
/admin/categories - POST
/admin/categories/{id} - PUT, DELETE

/cart - GET
/cart/items - POST добавление товара
/cart/items/{id} - PUT изменение количества товара, DELETE
/cart/clear - POST очистка корзины


"""

import sys
import os

# from fastapi.responses import RedirectResponse

app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, app_dir)

from fastapi import FastAPI#, Request
from backend.auth.router import router as auth_router
# from fastapi.staticfiles import StaticFiles


app = FastAPI(docs_url="/docs/api")

# app.mount('/static', StaticFiles(directory='app/static'), 'static')
app.include_router(prefix="/oauth", router=auth_router)

# @app.get("/", response_class=RedirectResponse)
# def home_page():
#     return "/pages"
