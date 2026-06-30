"""美妆达人 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.deps import get_db
from backend.app.models.influencer import Influencer
from backend.app.schemas.influencer import InfluencerResponse

router = APIRouter(prefix="/influencers", tags=["美妆达人"])


@router.get("/", response_model=list[InfluencerResponse])
def list_influencers(
    category: str = Query("all"),
    db: Session = Depends(get_db),
):
    query = select(Influencer)
    if category and category != "all":
        query = query.where(Influencer.category == category)
    influencers = db.execute(query).scalars().all()
    return [i.to_dict() for i in influencers]
