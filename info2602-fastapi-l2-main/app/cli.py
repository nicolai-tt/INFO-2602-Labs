import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()


@cli.command()
def initialize():
    """Reset database and create default user"""
    with get_session() as db:
        drop_all()
        create_db_and_tables()
        bob = User("bob", "bob@mail.com", "bobpass")
        db.add(bob)
        db.commit()
        db.refresh(bob)
        print("Database Initialized")


@cli.command()
def get_user(
    username: str = typer.Argument(..., help="Username to search for")
):
    """Get a user by username"""
    with get_session() as db:
        user = db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            print(f"{username} not found!")
            return

        print(user)


@cli.command()
def get_all_users():
    """Get all users"""
    with get_session() as db:
        users = db.exec(select(User)).all()

        if not users:
            print("No users found")
            return

        for user in users:
            print(user)


# Exercise 1
@cli.command()
def find_user(
    query: str = typer.Argument(..., help="Part of username or email")
):
    """Find user by partial username or email"""
    with get_session() as db:
        users = db.exec(
            select(User).where(
                (User.username.contains(query)) |
                (User.email.contains(query))
            )
        ).all()

        if not users:
            print("No users found")
            return

        for user in users:
            print(user)


# Exercise 2
@cli.command()
def list_users(
    limit: int = typer.Option(10, help="Number of users"),
    offset: int = typer.Option(0, help="Users to skip")
):
    """List users with limit and offset"""
    with get_session() as db:
        users = db.exec(
            select(User).offset(offset).limit(limit)
        ).all()

        if not users:
            print("No users found")
            return

        for user in users:
            print(user)


@cli.command()
def change_email(
    username: str = typer.Argument(..., help="Username"),
    new_email: str = typer.Argument(..., help="New email")
):
    """Change a user's email"""
    with get_session() as db:
        user = db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            print(f"{username} not found!")
            return

        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {username}'s email")


@cli.command()
def create_user(
    username: str = typer.Argument(..., help="Username"),
    email: str = typer.Argument(..., help="Email"),
    password: str = typer.Argument(..., help="Password")
):
    """Create a new user"""
    with get_session() as db:
        user = User(username, email, password)
        try:
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Username or email already taken!")
            return

        print(user)


@cli.command()
def delete_user(
    username: str = typer.Argument(..., help="Username")
):
    """Delete a user"""
    with get_session() as db:
        user = db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            print(f"{username} not found!")
            return

        db.delete(user)
        db.commit()
        print(f"{username} deleted")


if __name__ == "__main__":
    cli()