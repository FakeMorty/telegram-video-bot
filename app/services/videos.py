import random
from sqlalchemy import select
from app.database.session import SessionLocal
from app.database.models import Video, User, VideoView, VideoRating


async def get_user_by_telegram_id(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def video_exists(file_unique_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(Video.telegram_file_unique_id == file_unique_id)
        )
        return result.scalar_one_or_none()


async def save_video(
    uploader_telegram_id: int,
    file_id: str,
    file_unique_id: str,
    duration: int | None = None,
    file_size: int | None = None,
):
    async with SessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == uploader_telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return None, "user_not_found"

        existing = await session.execute(
            select(Video).where(Video.telegram_file_unique_id == file_unique_id)
        )
        if existing.scalar_one_or_none():
            return None, "duplicate"

        video = Video(
            uploader_user_id=user.id,
            telegram_file_id=file_id,
            telegram_file_unique_id=file_unique_id,
            status="pending",
            duration_seconds=duration,
            file_size=file_size,
        )
        session.add(video)
        await session.commit()
        await session.refresh(video)
        return video, None


async def get_next_pending_video():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(Video.status == "pending").order_by(Video.id.asc())
        )
        return result.scalars().first()


async def approve_video(video_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            return None

        video.status = "approved"
        await session.commit()
        await session.refresh(video)
        return video


async def reject_video(video_id: int, reason: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            return None

        video.status = "rejected"
        video.rejection_reason = reason
        await session.commit()
        await session.refresh(video)
        return video


async def get_video_with_uploader(video_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video, User)
            .join(User, User.id == Video.uploader_user_id)
            .where(Video.id == video_id)
        )
        return result.first()


async def get_random_video_for_user(telegram_user_id: int):
    async with SessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None, "user_not_found"

        viewed_result = await session.execute(
            select(VideoView.video_id).where(VideoView.user_id == user.id)
        )
        viewed_ids = [row[0] for row in viewed_result.all()]

        result = await session.execute(
            select(Video).where(
                Video.status == "approved",
                Video.uploader_user_id != user.id,
                Video.id.not_in(viewed_ids) if viewed_ids else True
            )
        )
        videos = result.scalars().all()

        if not videos:
            return None, "no_videos"

        return random.choice(videos), None


async def mark_video_viewed(telegram_user_id: int, video_id: int):
    async with SessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        existing = await session.execute(
            select(VideoView).where(
                VideoView.user_id == user.id,
                VideoView.video_id == video_id
            )
        )
        if existing.scalar_one_or_none():
            return None

        view = VideoView(
            user_id=user.id,
            video_id=video_id
        )
        session.add(view)
        await session.commit()
        await session.refresh(view)
        return view


async def rate_video(telegram_user_id: int, video_id: int, rating_value: int):
    async with SessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None, "user_not_found"

        existing_result = await session.execute(
            select(VideoRating).where(
                VideoRating.user_id == user.id,
                VideoRating.video_id == video_id
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.rating = rating_value
            await session.commit()
            await session.refresh(existing)
            return existing, None

        rating = VideoRating(
            user_id=user.id,
            video_id=video_id,
            rating=rating_value
        )
        session.add(rating)
        await session.commit()
        await session.refresh(rating)
        return rating, None