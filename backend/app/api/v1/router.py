from fastapi import APIRouter

from app.api.v1.endpoints.account_security import router as account_security_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.application_documents import router as application_documents_router
from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.calendar import router as calendar_router
from app.api.v1.endpoints.calendar_integration import router as calendar_integration_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.document_improvements import router as document_improvements_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.gmail_integration import router as gmail_integration_router
from app.api.v1.endpoints.job_analysis import router as job_analysis_router
from app.api.v1.endpoints.job_match import router as job_match_router
from app.api.v1.endpoints.job_recommendation_automation import router as job_recommendation_automation_router
from app.api.v1.endpoints.job_recommendations import router as job_recommendations_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.oauth import router as oauth_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.resumes import router as resumes_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(account_security_router)
api_router.include_router(ai_router)
api_router.include_router(application_documents_router)
api_router.include_router(applications_router)
api_router.include_router(calendar_router)
api_router.include_router(calendar_integration_router)
api_router.include_router(dashboard_router)
api_router.include_router(document_improvements_router)
api_router.include_router(health_router, tags=["health"])
api_router.include_router(gmail_integration_router)
api_router.include_router(job_analysis_router)
api_router.include_router(job_match_router)
api_router.include_router(job_recommendation_automation_router)
api_router.include_router(job_recommendations_router)
api_router.include_router(jobs_router)
api_router.include_router(notifications_router)
api_router.include_router(oauth_router)
api_router.include_router(profiles_router)
api_router.include_router(resumes_router)
