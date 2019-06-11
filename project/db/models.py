# coding=utf-8

from sqlalchemy import Column, Integer, String, DateTime, func, text, Boolean, UniqueConstraint, Index

from .database import Base


class AIScreeningInfo(Base):
    """
    AI筛查信息中间表
    """
    __tablename__ = "ai_screening_info"
    id = Column(Integer, primary_key=True)
    seriesuid = Column(String(128), index=True, nullable=False,doc=u'')
    studyuid = Column(String(128), index=True, nullable=False, doc=u'')
    hospcode = Column(String(128), index=True, nullable=False, doc=u'机构代码')

    studyuuid = Column(String(128), unique=True, index=True, doc=u'上传系统内部对应的序列唯一ID')
    seriesuuid = Column(String(128), unique=True, index=True, doc=u'上传系统内部对应的检查唯一ID')
    imagetype = Column(String(128), doc=u'影像类型(DICOM,JPG)')

    imagenos = Column(String(1024), nullable=False, doc=u'序列中所有图片instanceno拼接起来的字符串，分隔符是英文逗号')
    seriestime = Column(String(128), doc=u'序列日期 YYYY-MM-DD hh:mm:ss')
    modality = Column(String(128), doc=u'设备类型')
    bodypart = Column(String(256), doc=u'身体部位')
    screeningtype = Column(Integer, doc=u'病灶筛查类型(0:肺结节、2:X光片、3:骨龄)')

    airesults = Column(String(1024), doc=u'AI分析结果')
    aistatus = Column(Integer, doc=u'筛查结果阴阳性，1:阳 0:阴')

    filename = Column(String(1024), doc=u'上传原始文件名称')
    uploadinfo = Column(String(2048), doc=u'上传文件中间信息')

    upload_state = Column(Integer, server_default=text("0"))  # 0:未处理，1:成功, -1失败
    upload_code = Column(String(128), doc=u"上传返回状态码")
    aiupload_msg = Column(String(1024), doc=u'失败原因/返回状态信息')

    outpatient_state = Column(Integer, server_default=text("0"))  # 0:未处理，1:成功, -1失败
    outpatient_msg = Column(String(1024), doc=u'病例上传情况')

    aianalyse_msg = Column(String(1024), doc=u'AI分析情况')
    airesult_state = Column(Integer, server_default=text("0"))  # 0:未处理，1:成功, -1失败
    airesult_msg = Column(String(1024), doc=u'AI分析结果情况')

    uploadtime = Column(DateTime, doc=u'文件上传时间')
    inserttime = Column(DateTime, server_default=func.now())
    updatetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('seriesuid', 'studyuid', 'hospcode', name='uix_seriesuid_studyuid_hospcode'),
    )


class AIUploadReportInfo(Base):
    __tablename__ = "ai_upload_report_info"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(128), doc=u'上传报告文件名，包含路径')

    upload_state = Column(Integer, server_default=text("0"))   # 增量报告上传状态,0:未处理，1:成功, -1失败
    statedesc = Column(String(128), doc=u'失败原因')

    inserttime = Column(DateTime, server_default=func.now())
    updatetime = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AIUploadStudyInfo(Base):
    __tablename__ = "ai_upload_study_info"

    id = Column(Integer, primary_key=True)
    studyuid = Column(String(128), index=True,  doc=u'检查实例号')
    filename = Column(String(128), doc=u'上传文件名, 包含文件名后缀')

    upload_state = Column(Integer, server_default=text("0"))  # 增量报告上传状态,0:未处理，1:成功, -1失败
    statedesc = Column(String(128), doc=u'失败原因')

    inserttime = Column(DateTime, server_default=func.now())
    updatetime = Column(DateTime, server_default=func.now(), onupdate=func.now())