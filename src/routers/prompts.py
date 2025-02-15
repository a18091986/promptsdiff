from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm import PromptORM
from difflib import ndiff

from utils import important_print

class Category(BaseModel):
    category: str

class PromptCreate(Category):
    prompt: str


class Prompt(BaseModel):
    prompt: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PromptsWithDiff(BaseModel):
    prompts: list[Prompt]
    
    @computed_field
    def difference(self) -> str:
        if len(self.prompts) > 1:
            diff = ndiff(self.prompts[1].prompt.split(" "), self.prompts[0].prompt.split(" "))
            return "\n".join(diff)
        else:
            return ""


router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.post("/create", response_model=Prompt)
async def create_prompt(prompt: PromptCreate, db: AsyncSession = Depends(get_db)):
    try:
        prompt = await PromptORM.add_prompt(prompt.model_dump(), db)
        important_print(prompt)
        return Prompt.model_validate(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-prompts", response_model=PromptsWithDiff)
async def get_prompts(category: str, with_history: bool = False, db: AsyncSession = Depends(get_db)):
    try:
        prompts = await PromptORM.get_version(category, with_history, db)
        important_print(prompts)
        if prompts:
            if with_history:
                return PromptsWithDiff(prompts=[Prompt.model_validate(prompt) for prompt in prompts])
            else:
                return PromptsWithDiff(prompts=[Prompt.model_validate(prompt) for prompt in prompts])
        else:
            raise HTTPException(status_code=404, detail="Prompt not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))