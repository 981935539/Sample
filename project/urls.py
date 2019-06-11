# coding=utf-8

from handlers import IndexHandler
# from ai import OutPatientHandler, AIAnalyseHandler, AIResultHandler


HADNLERS = [
    (r"/", IndexHandler),
    # (r"/api/patient/outPatient", OutPatientHandler),
    # (r"/api/ai/request", AIAnalyseHandler),
    # (r"/api/ai/result", AIResultHandler),
]