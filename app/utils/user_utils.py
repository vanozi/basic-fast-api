from app.sql_app import schemas, models
from app.sql_app import crud


def get_user_response(db, user_id) -> schemas.User:
    user = crud.get_user(db=db, user_id=user_id)
    user_roles = crud.get_user_roles(db=db, user_id=user_id)
    role_names = [r.role for r in user_roles]
    response = schemas.User(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=role_names
    )
    return response


def get_all_users_response(db, skip: int, limit: int) -> schemas.User:
    users = crud.get_users(db=db, skip=skip, limit=limit)
    users_data = []
    for user in users:
        user_roles = crud.get_user_roles(db=db, user_id=user.id)
        role_names = [r.role for r in user_roles]
        user_data = schemas.User(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            roles=role_names
        )
        users_data.append(user_data)
    return users_data
