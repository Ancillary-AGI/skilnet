"""
Discussion forums API endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.social_learning import ForumPost, DiscussionForum
from app.models.user import User
from app.schemas.discussion import (
    DiscussionPostCreate,
    DiscussionPostResponse,
    DiscussionPostUpdate,
    DiscussionReplyCreate,
    DiscussionReplyResponse
)
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DiscussionPostResponse])
async def get_discussion_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    course_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get discussion posts with optional filtering"""
    query = db.query(ForumPost).filter(ForumPost.is_deleted == False)

    if course_id:
        query = query.join(DiscussionForum).filter(DiscussionForum.course_id == course_id)

    posts = query.offset(skip).limit(limit).all()

    # Convert to response format
    response_posts = []
    for post in posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        response_posts.append(DiscussionPostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author.full_name if author else "Unknown",
            author_avatar=author.avatar_url if author and hasattr(author, 'avatar_url') else None,
            timestamp=post.created_at,
            likes=post.upvotes,
            replies_count=post.reply_count,
            post_type=post.post_type
        ))

    return response_posts

@router.post("/", response_model=DiscussionPostResponse)
async def create_discussion_post(
    post: DiscussionPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new discussion post"""
    # Find or create discussion forum
    forum = None
    if post.course_id:
        forum = db.query(DiscussionForum).filter(
            DiscussionForum.course_id == post.course_id
        ).first()

        if not forum:
            # Create default forum for the course
            forum = DiscussionForum(
                title=f"Course {post.course_id} Discussion",
                course_id=post.course_id,
                created_by=current_user.id
            )
            db.add(forum)
            db.commit()
            db.refresh(forum)

    db_post = ForumPost(
        forum_id=forum.id if forum else None,
        author_id=current_user.id,
        title=post.title,
        content=post.content,
        post_type=post.post_type or "discussion",
        thread_id="",  # Will be set after creation
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    # Set thread_id to post id for root posts
    db_post.thread_id = db_post.id
    db.commit()

    return DiscussionPostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author=current_user.full_name,
        author_avatar=getattr(current_user, 'avatar_url', None),
        timestamp=db_post.created_at,
        likes=0,
        replies_count=0,
        post_type=db_post.post_type
    )

@router.post("/{post_id}/reply", response_model=DiscussionReplyResponse)
async def create_discussion_reply(
    post_id: str,
    reply: DiscussionReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a reply to a discussion post"""
    # Check if parent post exists
    parent_post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not parent_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create reply
    db_reply = ForumPost(
        forum_id=parent_post.forum_id,
        author_id=current_user.id,
        title="",  # Replies don't have titles
        content=reply.content,
        post_type="reply",
        parent_post_id=post_id,
        thread_id=parent_post.thread_id or parent_post.id
    )

    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)

    # Update reply count on parent post
    parent_post.reply_count += 1
    db.commit()

    return DiscussionReplyResponse(
        id=db_reply.id,
        content=db_reply.content,
        author=current_user.full_name,
        author_avatar=getattr(current_user, 'avatar_url', None),
        timestamp=db_reply.created_at
    )

@router.put("/{post_id}/like")
async def like_discussion_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like or unlike a discussion post"""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # For simplicity, just increment likes (in real app, track user likes)
    post.upvotes += 1
    db.commit()

    return {"message": "Post liked", "likes": post.upvotes}

@router.get("/{post_id}/replies", response_model=List[DiscussionReplyResponse])
async def get_discussion_replies(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get replies for a discussion post"""
    replies = db.query(ForumPost).filter(
        ForumPost.parent_post_id == post_id,
        ForumPost.is_deleted == False
    ).all()

    response_replies = []
    for reply in replies:
        author = db.query(User).filter(User.id == reply.author_id).first()
        response_replies.append(DiscussionReplyResponse(
            id=reply.id,
            content=reply.content,
            author=author.full_name if author else "Unknown",
            author_avatar=getattr(author, 'avatar_url', None) if author else None,
            timestamp=reply.created_at
        ))

    return response_replies
