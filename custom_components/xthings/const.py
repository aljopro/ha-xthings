"""Constants for the Xthings (U-tec) integration."""

DOMAIN = "xthings"

# OAuth2
OAUTH2_AUTHORIZE_URL = "https://oauth.u-tec.com/authorize"
OAUTH2_TOKEN_URL = "https://oauth.u-tec.com/token"

# API
API_BASE_URL = "https://api.u-tec.com/action"
HTTP_OK = 200

# Polling
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Xthings API namespaces
NS_USER = "Uhome.User"
NS_DEVICE = "Uhome.Device"
NS_CONFIGURE = "Uhome.Configure"
NS_NOTIFICATION = "Uhome.Notification"

# Xthings API actions
ACTION_GET = "Get"
ACTION_LOGOUT = "Logout"
ACTION_DISCOVERY = "Discovery"
ACTION_QUERY = "Query"
ACTION_COMMAND = "Command"
ACTION_SET = "Set"

# Capabilities
CAP_HEALTH_CHECK = "st.healthCheck"
CAP_LOCK = "st.lock"
CAP_LOCK_STATE = "st.Lock"  # Note: capital L in query responses
CAP_BATTERY_LEVEL = "st.BatteryLevel"
CAP_LOCK_USER = "st.lockUser"
CAP_DEFERRED_RESPONSE = "st.deferredResponse"
CAP_DOOR_SENSOR = "st.DoorSensor"

# Device categories
CATEGORY_LOCK = "LOCK"

# Handler types
HANDLER_LOCK = "utec-lock"
HANDLER_LOCK_SENSOR = "utec-lock-sensor"

# Lock handler types that we support
SUPPORTED_LOCK_HANDLERS = {HANDLER_LOCK, HANDLER_LOCK_SENSOR}
