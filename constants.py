#Configure the CDR dataset path, config cluster dataset path here:
import os

#Path to home directory
HOME_DIR = os.environ['HOME']

CDR_RELATIVE_PATH  = 'Documents/Project-Data/P_CDR_REC.csv'

CLUSTER_CONFIG_RELATIVE_PATH = 'Downloads/All_CUCM-Config-Data'



CDR_PATH = os.path.join(HOME_DIR,CDR_RELATIVE_PATH)

CLUSTER_CONFIG_PATH = os.path.join(HOME_DIR,CLUSTER_CONFIG_RELATIVE_PATH)



CAUSE_CODES = {
0: 'No error', 1: 'Unallocated (unassigned) number', 2: 'No route to specified transit network (national use)', 3 : 'No route to destination', 4: 'Send special information tone', 5: 'Misdialed trunk prefix (national use)', 6: 'Channel unacceptable', 7:
'Call awarded and being delivered in an established channel',  8: 'Preemption' , 9: 'Preemption—circuit reserved for reuse' , 16: 'Normal call clearing', 17: 'User busy', 18:
'No user responding',19: 'No answer from user (If "No Answer Ring duration" value is greater than the T301 Timer value and after T301 Timer expiry, Call Forwarding No Answer(CFNA) Feature would be invoked).', 20: 'Subscriber absent', 21: 'Call rejected', 22: 
'Number changed', 26: 'Non-selected user clearing', 27: 'Destination out of order', 28: 'Invalid number format (address incomplete)', 29: 'Facility rejected',  30: 'Response to STATUS ENQUIRY', 31: 'Normal, unspecified', 34: 'No circuit/channel available', 38: 'Network out of order', 39: 'Permanent frame mode connection out of service',
                   40: 'Permanent frame mode connection operational', 41: 'Temporary failure', 42: 'Switching equipment congestion', 43: 'Access information discarded', 44: 'Requested circuit/channel not available', 46: 'Precedence call blocked', 47: 'Resource unavailable, unspecified', 49: 'Quality of Service not available', 
                    50: 'Requested facility not subscribed', 53: 'Service operation violated', 54: 'Incoming calls barred', 55: 'Incoming calls barred within Closed User Group (CUG)', 57: 'Bearer capability not authorized', 58: 'Bearer capability not presently available', 62: 'Inconsistency in designated outgoing access information and subscriber class', 63: 'Service or option not available, unspecified',
                    65: 'Bearer capability not implemented', 66: 'Channel type not implemented', 69: 'Requested facility not implemented', 70: 'Only restricted digital information bearer capability is available (national use)', 
                    79: 'Service or option not implemented, unspecified', 81: 'Invalid call reference value', 82: 'Identified channel does not exist', 83: 'A suspended call exists, but this call identity does not',84: 'Call identity in use', 85: 'No call suspended', 86: 'Call having the requested call identity has been cleared',
87: 'User not member of CUG Closed User Group', 88: 'Incompatible destination',
                    90: 'Destination number missing and DC not subscribed', 91: 'Invalid transit network selection (national use)', 95: 'Invalid message, unspecified', 96: 'Mandatory information element is missing’, 97: ‘Message type nonexistent or not implemented’, 98: ‘Message is not compatible with the call state, or the message type is nonexistent or not implemented', 99: 'An information element or parameter does not exist or is not implemented', 100: 'Invalid information element contents',
                    101: 'The message is not compatible with the call state', 102: 'Call terminated when timer expired; a recovery routine executed to recover from the error', 103: 'Parameter nonexistent or not implemented - passed on (national use)', 110: 'Message with unrecognized parameter discarded', 111: 'Protocol error, unspecified', 122: 'Precedence Level Exceeded', 123: 'Device not Preemptable', 125: 'Out of bandwidth (Cisco specific)', 126: 'Call split (Cisco specific)', 
                    127: 'Interworking, unspecified', 129: 'Precedence out of bandwidth', 131: 'Call Control Discovery PSTN Failover (Cisco specific)', 132: 'IME QOS Fallback (Cisco specific)', 133: 'PSTN Fallback locate Call Error (Cisco specific)', 134: 'PSTN Fallback wait for DTMF Timeout (Cisco specific)', 135: 'IME Failed Connection Timed out (Cisco specific)', 136: 'IME Failed not enrolled (Cisco specific)', 137: 'IME Failed socket error (Cisco specific)', 138: 'IME Failed domain blacklisted (Cisco specific)', 139: 'IME Failed prefix blacklisted (Cisco specific)',
                    140: 'IME Failed expired ticket (Cisco specific)', 141: 'IME Failed remote no matching route (Cisco specific)', 142: 'IME Failed remote unregistered (Cisco specific)', 143: 'IME Failed remote IME disabled (Cisco specific)', 144: 'IME Failed remote invalid IME trunk URI (Cisco specific)' , 145: 'IME Failed remote URI not E164 (Cisco specific)',
146: 'IME Failed remote called number not available (Cisco specific)', 147: 'IME Failed Invalid Ticket (Cisco specific)',148: 'IME Failed unknown (Cisco specific)'
	} 

#List of symbols to be exported when import * is used on this module
__all__ = ['CDR_PATH','CLUSTER_CONFIG_PATH','CAUSE_CODES']