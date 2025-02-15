from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.schema import Category, Prompt
from dataclasses import dataclass
from utils import important_print



@dataclass
class PromptORM():
    @staticmethod
    async def add_prompt(prompt: dict, db: AsyncSession) -> Prompt:
        category = await db.execute(select(Category).where(Category.category == prompt.get("category")))
        category = category.scalar_one_or_none()
        if not category:
            category = Category(category=prompt.get("category"))    
            db.add(category)
            await db.flush()
        new_prompt = Prompt(category_id=category.id, prompt=prompt.get("prompt"))
        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)
        return new_prompt

    @staticmethod
    async def get_version(category: str, with_history: bool, db: AsyncSession) -> list[Prompt] | None:
        try:
            category = await db.execute(select(Category).where(Category.category == category))
            category = category.scalar_one_or_none()
            if not category:
                return None
            if with_history:
                prompts = await db.execute(select(Prompt).where(Prompt.category_id == category.id).order_by(Prompt.created_at.desc()))
                prompts = prompts.scalars().all()[:2]
                return prompts
            else:
                prompt = await db.execute(select(Prompt).where(Prompt.category_id == category.id).order_by(Prompt.created_at.desc()))
                prompt = prompt.scalars().first()
                return [prompt]
        except Exception as e:
            print(e)
            return None


    # @staticmethod
    # async def get_prompt(prompt_id: int, db: AsyncSession):
    #     return await db.query(Prompt).filter(Prompt.id == prompt_id).first()