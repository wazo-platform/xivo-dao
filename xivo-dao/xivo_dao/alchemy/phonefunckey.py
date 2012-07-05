from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from xivo_dao.alchemy.base import Base


class PhoneFunckey(Base):
    __tablename__ = 'phonefunckey'

    iduserfeatures = Column(Integer, nullable=False, primary_key=True)
    fknum = Column(Integer, nullable=False, primary_key=True)
    exten = Column(String(40))
    typevalextenumbers = Column(String(255))
    typevalextenumbersright = Column(String(255))
    label = Column(String(32))
    typeextenumbers = Column(String(16))
    supervision = Column(Integer, nullable=False, default=0)
    progfunckey = Column(Integer, nullable=False, default=0)
    typeextenumbersright = Column(String(16))
