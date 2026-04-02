import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.models.prediction import CustomerData, PredictionResponse
from app.services.predictor import PredictorService

# Lấy thư mục chứa file này (thư mục app)
app_dir = os.path.dirname(os.path.abspath(__file__))

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="Purchase Prediction API")

# Gắn thư mục chứa file tĩnh (dùng đường dẫn tuyệt đối)
static_dir = os.path.join(app_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Cấu hình thư mục chứa template (dùng đường dẫn tuyệt đối)
templates_dir = os.path.join(app_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Tạo đường dẫn tuyệt đối đến file mô hình

base_dir = os.path.dirname(app_dir)
model_path = os.path.join(base_dir, "downloaded_model", "purchase_prediction_model.pkl")

# Khởi tạo dịch vụ dự đoán với đường dẫn mô hình tuyệt đối
predictor_service = PredictorService(model_path)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Trang chủ"""
    return templates.TemplateResponse("base.html", {"request": request})

@app.post("/predict")
async def predict(data: CustomerData):
    """API endpoint để dự đoán"""
    return predictor_service.predict(data)

@app.get("/predict-view", response_class=HTMLResponse)
async def predict_form(request: Request):
    """Giao diện web để nhập dữ liệu dự đoán"""
    return templates.TemplateResponse("prediction_form.html", {"request": request})

@app.post("/predict-view", response_class=HTMLResponse)
async def predict_form_submit(
    request: Request,
    age: float = Form(...),
    time_spent_on_site: float = Form(...),
    pages_visited: int = Form(...),
    previous_purchases: int = Form(...),
    cart_value: float = Form(...),
    is_returning_customer: int = Form(...),
    days_since_last_visit: float = Form(...)
):
    """Xử lý form và hiển thị kết quả"""
    # Tạo đối tượng CustomerData từ dữ liệu nhập trên form
    data = CustomerData(
        age=age,
        time_spent_on_site=time_spent_on_site,
        pages_visited=pages_visited,
        previous_purchases=previous_purchases,
        cart_value=cart_value,
        is_returning_customer=is_returning_customer,
        days_since_last_visit=days_since_last_visit
    )
    
    # Dự đoán kết quả
    result = predictor_service.predict(data)
    
    # Trả về form kèm kết quả dự đoán
    return templates.TemplateResponse(
        "prediction_form.html",
        {
            "request": request, 
            "result": result,
            "form_data": data.dict()
        }
    )
