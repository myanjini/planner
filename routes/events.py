from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlmodel import select
from auth.authenticate import authenticate
from database.connection import get_session
from models.events import Event, EventUpdate


event_router = APIRouter(tags=["Event"])

events = []


# 이벤트 전체 조회  /events/ => retrive_all_events()
@event_router.get("/", response_model=List[Event])
async def retrive_all_events(session = Depends(get_session)) -> List[Event]:
   statement = select(Event)
   events = session.exec(statement)
   return events

# 이벤트 상세 조회  /events/{event_id} => retrive_event(event_id)
@event_router.get("/{event_id}", response_model=Event)
async def retrive_event(event_id: int, session = Depends(get_session)) -> Event:
    # for event in events:
    #     if event.id == event_id:
    #         return event
    event = session.get(Event, event_id)
    if event:
        return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트를 찾을 수 없습니다."
    )

# 이벤트 등록       /events/ => create_event()
@event_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(data: Event = Body(...), user_id = Depends(authenticate), session = Depends(get_session)) -> dict:
    data.user_id = user_id
    session.add(data)
    session.commit()
    session.refresh(data)

    return {"message": "이벤트 등록이 완료되었습니다."}

# 이벤트 하나 삭제  /events/{event_id} => delete_event(event_id)
@event_router.delete("/{event_id}")
async def delete_event(event_id: int, session = Depends(get_session)) -> dict:
    # for event in events:
    #     if event.id == event_id:
    #         events.remove(event)
    #         return {"message": "이벤트 삭제가 완료되었습니다."}
    event = session.get(Event, event_id)
    if event:
        session.delete(event)
        session.commit()
        return {"message": "이벤트 삭제가 완료되었습니다."}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트를 찾을 수 없습니다."
    )

# 이벤트 전체 삭제  /events/ => delete_all_events()
@event_router.delete("/")
async def delete_all_events(session = Depends(get_session)) -> dict:
    # events.clear()
    statement = select(Event)
    events = session.exec(statement)
    for event in events:
        session.delete(event)
    session.commit()

    return {"message": "이벤트 전체 삭제가 완료되었습니다."}

# 이벤트 수정      /events/{event_id} => update_event(event_id)
@event_router.put("/{event_id}", response_model=Event)
async def update_event(data: EventUpdate, event_id: int = Path(...), session = Depends(get_session)) -> Event:
    event = session.get(Event, event_id)
    if event:
        # 요청 본문으로 전달된 데이터 중 값이 없는 부분을 제외
        # event_data = data.dict(exclude_unset=True)
        event_data = data.model_dump(exclude_unset=True)

        for key, value in event_data.items():
            setattr(event, key, value)

        session.add(event)
        session.commit()    
        session.refresh(event)

        return event
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트를 찾을 수 없습니다."
    )