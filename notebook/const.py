HR_TRAIN_PATH = '../data/hr_train.csv'
HR_IL_PATH = '../data/hr_il.csv'
HR_GT_PATH = '../data/hr_gt.csv'
HR_BPMN_PATH = '../data/hr.xml'
HR_XES_OUT_PATH = '../out/hr_xes_out.csv'


PTP_TRAIN_PATH = '../data/ptp_train.csv'
PTP_IL_PATH = '../data/ptp_il.csv'
PTP_GT_PATH = '../data/ptp_gt.csv'
PTP_BPMN_PATH = '../data/ptp.xml'
PTP_XES_OUT_PATH = '../out/ptp_xes_out.csv'

HR_ATTRIBUTES = ["applicant_id", "activity_id"]
PTP_ATTRIBUTES = ["sale_order_id", "sale_order_line_id", "purchase_requisition_id", "purchase_requisition_line_id", ]

HR_CASE_ID_PRIMARY = "applicant_id"
PTP_CASE_ID_PRIMARY = "sale_order_line_id_case_id"
