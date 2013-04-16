from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class Article(Base):
    __tablename__ = 'articles'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    title = Column(String(200), unique=True)
    date = Column(Date())
    preview = Column(Text())
    content = Column(Text())

    def __init__(self, title=None, date=None, preview=None, content=None):
        self.title = title
        self.date = date
        self.preview = preview
        self.content = content

    def __repr__(self):
        return '<Article - %r' % (self.title)