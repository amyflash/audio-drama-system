"""
SSO 单点登录 API 路由
直接验证来自 jwt-auth 的 token，不做本地用户存储
"""
from fastapi import APIRouter, HTTPException, status, Request, Header
from fastapi.responses import HTMLResponse
from typing import Optional
from pydantic import BaseModel
from urllib.parse import quote, urlencode
import json

from app.core.config import settings
from app.core.sso import decode_external_token

router = APIRouter(prefix="/auth/sso", tags=["SSO登录"])


class UserInfo(BaseModel):
    """从 jwt-auth token 解析出的用户信息"""
    id: int
    username: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class SuccessResponse(BaseModel):
    success: bool
    data: str


def get_sso_login_url(redirect_uri: str) -> str:
    """
    生成 SSO 登录跳转 URL

    Args:
        redirect_uri: 登录成功后的回调地址

    Returns:
        jwt-auth 的登录页面 URL
    """
    params = {
        "sso": "true",
        "redirect_uri": redirect_uri
    }
    return f"{settings.SSO_JWT_AUTH_URL}/auth/sso-login?{urlencode(params)}"


def get_current_user_from_token(request: Request) -> UserInfo:
    """
    从请求中提取并验证 token，返回用户信息
    供其他路由使用
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]
    payload = decode_external_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserInfo(
        id=int(payload.get("sub", 0)),
        username=payload.get("username", "unknown"),
        role=payload.get("role", "user")
    )


def require_admin(request: Request) -> UserInfo:
    """验证管理员权限"""
    user = get_current_user_from_token(request)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user


@router.get("/login-url")
async def get_login_url(request: Request):
    """
    获取 SSO 登录跳转 URL

    前端跳转到此 URL 即可进入 jwt-auth 登录页面
    """
    if not settings.SSO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO 登录已禁用"
        )

    redirect_uri = request.query_params.get("redirect_uri", "/")

    # 构建回调 URL（对 redirect_uri 进行 URL 编码）
    encoded_redirect_uri = quote(redirect_uri, safe='')
    callback_url = f"{request.base_url}api/auth/sso/callback?redirect_uri={encoded_redirect_uri}"

    return {
        "login_url": get_sso_login_url(callback_url),
        "callback_url": callback_url
    }


def _validate_token_and_build_response(token: str) -> LoginResponse:
    """
    验证 SSO token 并构建登录响应

    Args:
        token: JWT token 字符串

    Returns:
        LoginResponse 对象

    Raises:
        HTTPException: token 无效时抛出 401 异常
    """
    payload = decode_external_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 SSO token"
        )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_SECONDS,
        user=UserInfo(
            id=int(payload.get("sub", 0)),
            username=payload.get("username", "unknown"),
            role=payload.get("role", "user")
        )
    )


@router.get("/callback")
async def sso_callback_get(
    request: Request,
    token: str = "",
    redirect_uri: str = "/",
):
    """
    SSO 登录回调接口 (GET)

    jwt-auth 登录成功后会重定向到此端点，token 通过 query 参数传递
    返回一个 HTML 页面，自动将 token 存储到 localStorage 并跳转到目标页面
    """
    if not settings.SSO_ENABLED:
        # FIX: was `raise HTMLResponse(...)`, must be `return`
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>登录失败</title></head>
        <body>
            <h1>SSO 登录已禁用</h1>
            <p>请联系管理员启用 SSO 登录。</p>
        </body>
        </html>
        """, status_code=400)

    if not token:
        # FIX: was `raise HTMLResponse(...)`, must be `return`
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>登录失败</title></head>
        <body>
            <h1>缺少 token 参数</h1>
            <p>登录验证失败，请重新登录。</p>
        </body>
        </html>
        """, status_code=400)

    payload = decode_external_token(token)
    if payload is None:
        # FIX: was `raise HTMLResponse(...)`, must be `return`
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>登录失败</title></head>
        <body>
            <h1>无效的 Token</h1>
            <p>登录验证失败，Token 无效或已过期。</p>
        </body>
        </html>
        """, status_code=401)

    user_info = UserInfo(
        id=int(payload.get("sub", 0)),
        username=payload.get("username", "unknown"),
        role=payload.get("role", "user")
    )

    final_redirect = redirect_uri if redirect_uri else "/"

    # FIX: 使用 json.dumps 序列化数据后注入 JS，避免 XSS
    user_info_json = json.dumps({
        "id": user_info.id,
        "username": user_info.username,
        "role": user_info.role
    })
    token_json = json.dumps(token)
    user_id_json = json.dumps(str(user_info.id))
    username_json = json.dumps(user_info.username)
    role_json = json.dumps(user_info.role)
    redirect_json = json.dumps(final_redirect)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>登录成功</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 2rem 3rem;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
            }}
            h1 {{ color: #4CAF50; margin-bottom: 1rem; }}
            p {{ color: #666; margin-bottom: 0.5rem; }}
            .username {{ font-size: 1.2rem; font-weight: bold; color: #333; }}
            .loading {{ color: #999; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ 登录成功</h1>
            <p>欢迎回来，<span class="username" id="uname"></span>！</p>
            <p class="loading">正在跳转到首页...</p>
        </div>
        <script>
            var token     = {token_json};
            var userId    = {user_id_json};
            var username  = {username_json};
            var role      = {role_json};
            var userInfo  = {user_info_json};
            var redirectUri = {redirect_json};

            document.getElementById('uname').textContent = username;

            localStorage.setItem('token',    token);
            localStorage.setItem('user_id',  userId);
            localStorage.setItem('username', username);
            localStorage.setItem('role',     role);
            localStorage.setItem('user',     JSON.stringify(userInfo));

            setTimeout(function() {{
                window.location.href = redirectUri;
            }}, 800);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/callback", response_model=LoginResponse)
async def sso_callback_post(
    request: Request,
    redirect_uri: str = "/",
):
    """
    SSO 登录回调接口 (POST)

    前端从 jwt-auth 重定向后提取 token，然后 POST 到此端点验证
    """
    if not settings.SSO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO 登录已禁用"
        )

    body = await request.json()
    token = body.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少 token 参数"
        )

    return _validate_token_and_build_response(token)


@router.post("/verify", response_model=SuccessResponse)
async def verify_token(
    request: Request,
):
    """
    验证 SSO token

    用于检查 token 是否有效
    """
    if not settings.SSO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO 登录已禁用"
        )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证凭据"
        )

    token = auth_header[7:]
    payload = decode_external_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 SSO token"
        )

    return SuccessResponse(
        success=True,
        data=f"Token 有效，用户: {payload.get('username')}"
    )


@router.get("/status")
async def sso_status():
    """
    获取 SSO 状态

    返回 SSO 是否启用以及 jwt-auth 服务地址
    """
    return {
        "sso_enabled": settings.SSO_ENABLED,
        "local_login_enabled": settings.LOCAL_LOGIN_ENABLED,
        "jwt_auth_url": settings.SSO_JWT_AUTH_URL
    }