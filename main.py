from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, StudentDB
from pydantic import BaseModel

app = FastAPI()

Base.metadata.create_all(bind=engine)


# فتح اتصال مع قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# شكل البيانات القادمة من المستخدم
class Student(BaseModel):
    name: str
    age: int


@app.get("/")
def home():
    return {"message": "Hello Bashayer!"}


@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI"}


# إضافة طالب جديد إلى PostgreSQL
@app.post("/students")
def add_student(student: Student, db: Session = Depends(get_db)):

    new_student = StudentDB(
        name=student.name,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student added",
        "student": {
            "id": new_student.id,
            "name": new_student.name,
            "age": new_student.age
        }
    }


# عرض جميع الطلاب من PostgreSQL
@app.get("/students")
def get_students(db: Session = Depends(get_db)):

    students = db.query(StudentDB).all()

    return students


# تعديل طالب باستخدام id
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: Student,
    db: Session = Depends(get_db)
):

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_student.name = student.name
    existing_student.age = student.age

    db.commit()
    db.refresh(existing_student)

    return {
        "message": "Student updated",
        "student": {
            "id": existing_student.id,
            "name": existing_student.name,
            "age": existing_student.age
        }
    }


# حذف طالب باستخدام id
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(existing_student)
    db.commit()

    return {
        "message": "Student deleted",
        "student": {
            "id": existing_student.id,
            "name": existing_student.name,
            "age": existing_student.age
        }
    }