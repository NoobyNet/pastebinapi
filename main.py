from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import auth, paste
from exceptions import (
    PastebinAPIError,
    AuthenticationError,
    PasteListError,
    PasteCreationError,
    InvalidRequestError
)

app = FastAPI(title="Pastebin API Wrapper")


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Authentication Error", "detail": exc.message}
    )


@app.exception_handler(InvalidRequestError)
async def invalid_request_error_handler(request: Request, exc: InvalidRequestError):
    """Handle invalid request errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid Request", "detail": exc.message}
    )


@app.exception_handler(PasteListError)
async def paste_list_error_handler(request: Request, exc: PasteListError):
    """Handle paste listing errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Paste List Error", "detail": exc.message}
    )


@app.exception_handler(PasteCreationError)
async def paste_creation_error_handler(request: Request, exc: PasteCreationError):
    """Handle paste creation errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Paste Creation Error", "detail": exc.message}
    )


@app.exception_handler(PastebinAPIError)
async def pastebin_api_error_handler(request: Request, exc: PastebinAPIError):
    """Handle generic Pastebin API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Pastebin API Error", "detail": exc.message}
    )


app.include_router(auth.router)
app.include_router(paste.router)
