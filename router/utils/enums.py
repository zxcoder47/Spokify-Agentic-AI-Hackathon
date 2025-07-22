from enum import Enum


class WSMessageType(Enum):
    AGENT_REGISTER = "agent_register"
    AGENT_UNREGISTER = "agent_unregister"
    AGENT_INVOKE = "agent_invoke"
    AGENT_RESPONSE = "agent_response"
    AGENT_ERROR = "agent_error"
    AGENT_LOG = "agent_log"
    ML_INVOKE = "ml_invoke"


class MasterServerName(Enum):
    MASTER_SERVER_BE = "master_server_be"
    MASTER_SERVER_ML = "master_server_ml"


class ErrorType(Enum):
    AGENT_UUID_ERROR = "AgentUUIDError"
    AGENT_GENERAL_ERROR = "AgentGeneralError"
    AGENT_NOT_ACTIVE = "AgentNotActive"
    INVALID_JSON_REQUEST_FORMAT = "InvalidJSONRequestFormat"
    NO_REQUEST_PAYLOAD = "NoRequestPayload"
