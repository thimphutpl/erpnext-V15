from __future__ import unicode_literals
import json
import frappe
import requests, base64
from xml.etree import ElementTree
from frappe import _
from frappe.utils import cint, flt, get_bench_path, get_datetime
class BankAPI:
    pass

@frappe.whitelist()
def encrypt_credential(api):
    doc = frappe.get_doc("API Detail", str(api))

    url = doc.api_link
    api_key = ""

    for a in doc.item:
        if a.param == "X-BoB-Api-Key":
            api_key = a.defined_value
    header_bytes = api_key.strip()


    return header_bytes, url

@frappe.whitelist()
def intra_payment(from_acc, trans_amount, promo_no, to_acc, unique_transaction_no):
    # frappe.throw(str(promo_no))
    if not frappe.db.get_value('Bank Payment Settings', "BOBL", 'enable_one_to_one'):
        return
  
    api_key, url = encrypt_credential(api="ONE TO ONE - INTRA BANK")
    amount = "{:.2f}".format(flt(trans_amount))

    payload = {
                "SvcRq": {
                    "DepAcctFundXferRq": {
                    "RqHeader": {
                        "Filler1": "NS",
                        "MsgLen": "NS",
                        "Filler2": "NS",
                        "MsgTyp": "NS",
                        "Filler3": "NS",
                        "CycNum": "NS",
                        "MsgNum": "NS",
                        "SegNum": "NS",
                        "SegNum2": "NS",
                        "FrontEndNum": "-999",
                        "TermlNum": "NS",
                        "InstNum": "-999",
                        "BrchNum": "-999",
                        "WorkstationNum": "-999",
                        "TellerNum": "28",
                        "TranNum": "-999",
                        "JrnlNum": "-999",
                        "HdrDt": "NS",
                        "Filler4": "NS",
                        "Filler5": "-999",
                        "Filler6": "NS",
                        "Flag1": "NS",
                        "Flag2": "NS",
                        "Flag3": "NS",
                        "Flag4": "NS",
                        "Flag5": "NS",
                        "Flag6": "NS",
                        "Flag7": "-999",
                        "SprvsrID": "-999",
                        "SupDate": "NS",
                        "CheckerID1": "-999",
                        "ParentBlinkJrnlNum": "-999",
                        "CheckerID2": "-999",
                        "BlinkJrnlNum": "-999",
                        "UUIDSource": "NS",
                        "UUIDNUM": "NS",
                        "UUIDSeqNo": "-999"
                    },
                    "Data": {
                        "FrmAcctNum": from_acc,
                        "Amt": amount,
                        "PromoNum":promo_no,
                        "ToAcctNum": to_acc,
                        "TrnAmt": amount,
                        "StmtNarr": unique_transaction_no
                    }
                    }
                }
            }
    

    
    headers = {
        'X-BoB-Api-Key': api_key,
        "delChannel":"BOB",
        'accept': 'application/json',
        'Content-Type': 'application/json',
      
    }
   
#    # frappe.throw(str(payload))
    response = requests.request("POST", url, headers=headers, json=payload)
#     # response_data = response.json()
#     try:
#         response_data = response.json()
#     except ValueError:
#         return {
#             "jrnl_no": "",
#             "status": "Failed",
#             "message": "Invalid JSON response from bank API"
#         }

#     svc = response_data.get("SvcRs", {}).get("DepAcctFundXferRs", {})
#     header = svc.get("RsHeader", {})
#     stat = svc.get("Stat", {})
#     frappe.throw(str(response_data))

#     jrnl_no = header.get("JrnlNum", "")

#     if "OkMessage" in stat:
#         ok = stat["OkMessage"]
#         return {
#             "jrnl_no": jrnl_no,
#             "status": "Success",
#             "message": ok.get("RcptData", "")
#         }

#     if "ErrorMessage" in stat:
#         err = stat["ErrorMessage"]

#         if isinstance(err, dict):
#             message = err.get("ErrorMessage", "")
#         else:
#             message = str(err)

#         return {
#             "jrnl_no": jrnl_no,
#             "status": "Failed",
#             "message": message
#         }

#     return {
#         "jrnl_no": jrnl_no,
#         "status": "Failed",
#         "message": "Unknown response from bank API"
#     }
    try:
        response_data = response.json()
        # frappe.throw(str(response_data))
    except ValueError:
            
            return {
                "jrnl_no": "",
                "status": "Failed",
                "message": "Invalid JSON response from bank API"
            }


    # Handle INTERNAL_SERVER_ERROR response
    if response_data.get("status") == "INTERNAL_SERVER_ERROR":

            error_data = json.loads(response_data["errors"][0])

            if "errorDetails" in error_data:
                description = error_data["errorDetails"][0]["description"]

            elif "errorMessageList" in error_data:
                description = error_data["errorMessageList"][0]["description"]

            return {
                "status": "Failed",
                "message": description
            }



    # Handle successful response
    svc = response_data.get("SvcRs", {}).get("DepAcctFundXferRs", {})

    header = svc.get("RsHeader", {})
    stat = svc.get("Stat", {})

    jrnl_no = header.get("JrnlNum", "")


    # Success response
    if "OkMessage" in stat:

        ok_message = stat["OkMessage"]

        return {
            "jrnl_no": jrnl_no,
            "status": "Success",
            "message": ok_message.get("RcptData", "")
        }


    # Bank returned failure inside Stat
    if "ErrorMessage" in stat:

        error_message = stat["ErrorMessage"]

        if isinstance(error_message, dict):
            message = error_message.get(
                "ErrorMessage",
                "Payment failed"
            )
        else:
            message = str(error_message)

        return {
            "jrnl_no": jrnl_no,
            "status": "Failed",
            "message": message
        }


    # Unexpected response - stop immediately
    frappe.throw(
        f"Unexpected response from bank API: {response_data}"
    )
  
@frappe.whitelist()
def inter_payment(Amt, PayeeAcctNum, BnfcryAcct, BnfcryName, BnfcryAcctTyp, BnfcryRmrk, RemitterName, BfscCode, RemitterAcctType, PEMSRefNum,posting_date):
  
    if not frappe.db.get_value('Bank Payment Settings', "BOBL", 'enable_one_to_one'):
        return

    api_key, url = encrypt_credential(api="ONE TO ONE - INTER BANK")

    if Amt > 1000000:
        clearingType = 1
    else:
        clearingType = 3
    
    payload = {
                "skipErrorIds": [
                    1384086
                ],
                "initiatePayment": {
                    "messageHeader": {
                        "messageType": 4033,
                        "initiatingChannelReference": 3,
                        "initiatingBranchReference": "20",
                        "externalUserID": "28"
                    },
                    "remDetails": {
                        "instrumentId": 1,
                        "requestedExecutionDate": posting_date,
                        "transferAmountCurrency": "BTN",
                        "transferAmount": Amt,
                        "waiveChargeFlag": 1,
                        "debtorAccountType": RemitterAcctType,
                        "transactionReference": PEMSRefNum,
                        "debtorAccount": PayeeAcctNum,
                        "orderingCustomerName": RemitterName,
                        "direction": 2,
                        "orderType": 101
                    },
                    "pymntDetails": {
                        "clearingType": clearingType,
                        "beneficiaryName": BnfcryName,
                        "beneficiaryIdentifierType": 5,
                        "beneficiaryAccountType": BnfcryAcctTyp,
                        "beneficiaryAccount": BnfcryAcct,
                        "beneficiaryBankIdentifierType": 150,
                        "beneficiaryBankIdentifier": BfscCode
                    },
                    "additionalDetails": {
                    "remittanceInfoLine1": PEMSRefNum
                    }
                }
            }
    headers = {
        'X-BoB-Api-Key': api_key,
        "delChannel":"BOB",
        'accept': 'application/json',
        'Content-Type': 'application/json',
      
    }

    # try:
    #     response = requests.post(
    #         url,
    #         headers=headers,
    #         json=payload,
    #         timeout=60
    #     )

    #     data = response.json()
    #     frappe.throw(str(data))

    #     payment_response = data.get("initiatePaymentResponse", {})
    #     status = payment_response.get("status", {})
    #     payment = payment_response.get("response", {})

    #     # Success
    #     if status.get("successFlag") == 1:
    #         return {
    #             "status": "Success",
    #             "payment_reference": payment.get("pymntReference"),
    #             "transaction_reference": payment.get("transactionReference"),
    #             "execution_date": payment_response.get("CLS_CT_REM", {}).get("EXEC_DT"),
    #             "response": data
    #         }

    #     # Failed
    #     error_code = None
    #     error_description = "Payment Failed"

    #     errors = data.get("errors", [])

    #     if errors:
    #         try:
    #             error_data = json.loads(errors[0])
    #             detail = error_data.get("errorDetails", [{}])[0]

    #             error_code = detail.get("errorCode")
    #             error_description = detail.get("description")

    #         except Exception:
    #             pass

    #     return {
    #         "status": "Failed",
    #         "error_code": error_code,
    #         "error_description": error_description,
    #         "response": data
    #     }

    # except requests.exceptions.RequestException as e:
    #     frappe.log_error(
    #         frappe.get_traceback(),
    #         "BOBL Inter Payment API"
    #     )
    #     frappe.throw(str(e))

    # except ValueError:
    #     frappe.throw(response.text)
    try:
        response = requests.request("POST", url, headers=headers, json=payload)

        try:
            response_data = response.json()

        except ValueError:
            return {
                "status": "Failed",
                "message": "Invalid JSON response from bank API"
            }


        # Handle Success Response
        payment_response = response_data.get("initiatePaymentResponse", {})

        status = payment_response.get("status", {})
        payment = payment_response.get("response", {})

        if status.get("successFlag") == 1:
            return {
                "status": "Success",
                "payment_reference": payment.get("pymntReference"),
                "transaction_reference": payment.get("transactionReference"),
                "execution_date": payment_response.get("CLS_CT_REM", {}).get("EXEC_DT"),
                "response": response_data
            }


        # Handle INTERNAL_SERVER_ERROR Response
        if response_data.get("status") == "INTERNAL_SERVER_ERROR":

            error_data = json.loads(response_data["errors"][0])

            if "errorDetails" in error_data:
                description = error_data["errorDetails"][0]["description"]

            elif "errorMessageList" in error_data:
                description = error_data["errorMessageList"][0]["description"]

            return {
                "status": "Failed",
                "message": description
            }


        # Unexpected response
        frappe.throw(
            f"Unexpected response from bank API: {response_data}"
        )


    except requests.exceptions.RequestException as e:

        frappe.log_error(
            frappe.get_traceback(),
            "BOBL Payment API"
        )

        frappe.throw(str(e))

    

    
@frappe.whitelist()
def inr_remittance(AcctNum, Amt, BnfcryAcct, BnfcryName, BnfcryAddr1, IFSC, BankCode, PurpCode, RemittersName, RemittersAddr1, ComsnOpt, PromoCode, PemsRefNum):
    if not frappe.db.get_value('Bank Payment Settings', "BOBL", 'enable_one_to_one'):
        return
    
    header_credential, url = encrypt_credential(api="ONE TO ONE - INR Remmittance")
    '''
    doc = frappe.get_doc("API Detail", "ONE TO ONE - INR Remmittance")
    url = doc.api_link
    for a in doc.item:
        if a.param == "user_id":
            user_id = a.defined_value
        elif a.param == "password":
            password = a.defined_value
    '''
    #url = "http://10.30.30.195:8088/INRRemittanceByTransferSecured/INRRemittanceByTransferSecuredInterfaceHttpService"
    payload = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:v1="http://BaNCS.TCS.com/webservice/INRRemittanceByTransferSecuredInterface/v1" 
    xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
    <soapenv:Header/>
    <soapenv:Body>
        <v1:iNRRemittanceByTransferSecured>
            <INRRemittanceByXferRq>
                <ban:RqHeader>
                <!--Optional:-->
                <ban:Filler1></ban:Filler1>
                <!--Optional:-->
                <ban:MsgLen></ban:MsgLen>
                <!--Optional:-->
                <ban:Filler2></ban:Filler2>
                <!--Optional:-->
                <ban:MsgTyp></ban:MsgTyp>
                <!--Optional:-->
                <ban:Filler3></ban:Filler3>
                <!--Optional:-->
                <ban:CycNum></ban:CycNum>
                <!--Optional:-->
                <ban:MsgNum></ban:MsgNum>
                <!--Optional:-->
                <ban:SegNum></ban:SegNum>
                <!--Optional:-->
                <ban:SegNum2></ban:SegNum2>
                <!--Optional:-->
                <ban:FrontEndNum></ban:FrontEndNum>
                <!--Optional:-->
                <ban:TermlNum></ban:TermlNum>
                <!--Optional:-->
                    <ban:InstNum>03</ban:InstNum>
                <ban:BrchNum>00010</ban:BrchNum>
                <!--Optional:-->
                <ban:WorkstationNum></ban:WorkstationNum>
                <!--Optional:-->
                <ban:TellerNum>8882</ban:TellerNum>
                <!--Optional:-->
                <ban:TranNum></ban:TranNum>
                <!--Optional:-->
                <ban:JrnlNum></ban:JrnlNum>
                <!--Optional:-->
                <ban:HdrDt></ban:HdrDt>
                <!--Optional:-->
                <ban:Filler4></ban:Filler4>
                <!--Optional:-->
                <ban:Filler5></ban:Filler5>
                <!--Optional:-->
                <ban:Filler6></ban:Filler6>
                <!--Optional:-->
                <ban:Flag1></ban:Flag1>
                <!--Optional:-->
                <ban:Flag2></ban:Flag2>
                <!--Optional:-->
                <ban:Flag3></ban:Flag3>
                <!--Optional:-->
                <ban:Flag4>W</ban:Flag4>
                <ban:Flag5>Y</ban:Flag5>
                <!--Optional:-->
                <ban:Flag6></ban:Flag6>
                <!--Optional:-->
                <ban:Flag7></ban:Flag7>
                <!--Optional:-->
                <ban:SprvsrID></ban:SprvsrID>
                <!--Optional:-->
                <ban:SupDate></ban:SupDate>
                <!--Optional:-->
                <ban:CheckerID1></ban:CheckerID1>
                <!--Optional:-->
                <ban:ParentBlinkJrnlNum></ban:ParentBlinkJrnlNum>
                <!--Optional:-->
                <ban:CheckerID2></ban:CheckerID2>
                <!--Optional:-->
                <ban:BlinkJrnlNum></ban:BlinkJrnlNum>
                <ban:UUIDSource></ban:UUIDSource>
                <ban:UUIDNUM></ban:UUIDNUM>
                <!--Optional:-->
                <ban:UUIDSeqNo></ban:UUIDSeqNo>
                </ban:RqHeader>
            <ban:Data>
                <ban:AcctNum>{0}</ban:AcctNum>
                <!--Optional:-->
                <ban:CustName></ban:CustName>
                <!--Optional:-->
                <ban:Bal></ban:Bal>
                <!--Optional:-->
                <ban:ModeOfPay></ban:ModeOfPay>
                <ban:Amt>{1}</ban:Amt>
                <!--Optional:-->
                <ban:AmtCur></ban:AmtCur>
                <!--Optional:-->
                <ban:Comsn>2</ban:Comsn>
                <!--Optional:-->
                <ban:TtlAmt></ban:TtlAmt>
                <!--Optional:-->
                <ban:TtlAmtCur>BTN</ban:TtlAmtCur>
                <ban:BnfcryAcct>{2}</ban:BnfcryAcct>
                <ban:BnfcryName>{3}</ban:BnfcryName>
                <ban:BnfcryAddr1>{4}</ban:BnfcryAddr1>
                <!--Optional:-->
                <ban:BnfcryAddr2></ban:BnfcryAddr2>
                <!--Optional:-->
                <ban:BnfcryAddr3></ban:BnfcryAddr3>
                <ban:IFSC>{5}</ban:IFSC>
                <ban:BankCode>{6}</ban:BankCode>
                <ban:PurpCode>{7}</ban:PurpCode>
                <ban:RemittersName>{8}</ban:RemittersName>
                <ban:RemittersAddr1>{9}</ban:RemittersAddr1>
                <!--Optional:-->
                <ban:RemittersAddr2></ban:RemittersAddr2>
                <!-- Optional:-->
                <ban:RemittersAddr3></ban:RemittersAddr3>
                <ban:MailIdMobile></ban:MailIdMobile>
                <!--Optional:-->
                <ban:ComsnOpt>{10}</ban:ComsnOpt>
                <!--Optional:-->
                <ban:PromoCode>{11}</ban:PromoCode>
                <!--Optional:-->
                <ban:PemsRefNum>{12}</ban:PemsRefNum>
                </ban:Data>
            </INRRemittanceByXferRq>
        </v1:iNRRemittanceByTransferSecured>
    </soapenv:Body>""".format(AcctNum, Amt, BnfcryAcct, BnfcryName, BnfcryAddr1, IFSC, BankCode, PurpCode, RemittersName, RemittersAddr1, ComsnOpt, PromoCode, PemsRefNum)

    headers = {
    'Authorization': 'Basic RVBBWUNEQ0w6cGFzc3dvcmQxMjMk',
    'Content-Type': 'application/xml'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ns2': 'http://TCS.BANCS.Adapter/BANCSSchema',
        'ns3': 'http://BaNCS.TCS.com/webservice/INRRemittanceByTransferSecuredInterface/v1'
    }

    JrnlNum=""
    errorMessage=""
    successMessage= ""
    dom = ElementTree.fromstring(response.text)
    for name in dom.findall('./soap:Body/ns3:iNRRemittanceByTransferSecuredResponse/INRRemittanceByXferRs/ns2:RsHeader/ns2:JrnlNum', namespaces):
        JrnlNum = name.text
    for name in dom.findall('./soap:Body/ns3:iNRRemittanceByTransferSecuredResponse/INRRemittanceByXferRs/ns2:Stat/ns2:ErrorMessage/ns2:ErrorMessage', namespaces):
        errorMessage = name.text
    for name in dom.findall('./soap:Body/ns3:iNRRemittanceByTransferSecuredResponse/INRRemittanceByXferRs/ns2:Stat/ns2:OkMessage/ns2:RcptData', namespaces):
        successMessage = name.text

    if successMessage:
        message = successMessage
        status = "Success"
    else:
        message = errorMessage
        status = "Failed"

    return {"jrnl_no":JrnlNum, "status":status, "message":message}
    
@frappe.whitelist()
def fetch_balance(accountId):

    if not accountId:
        return {"message":"Please provide account no"}
    if not frappe.db.get_value('Bank Payment Settings', "BOBL", 'enable_one_to_one'):
        return
    api_key, url = encrypt_credential(api="BOB Customer Balance Enquiry")

    payload = {
        "accountId": accountId
    }
    headers = {
        'X-BoB-Api-Key': api_key,
        "delChannel":"BOB",
        'accept': 'application/json',
        'Content-Type': 'application/json',
      
    }
    try:
        response = requests.request("POST", url, headers=headers, json=payload, timeout=5)
        response_data = response.json()
        data = response_data.get("accountDetailsWithAddress", {})
        return {'status':'0','account_holder':data.get("accountName"), "balance_amount":data.get("currentBalance"), "message": "Success"} 
        
    except requests.exceptions.RequestException as err:
        return {'status':'1', 'message':'Respomnse time out', 'error': err}
