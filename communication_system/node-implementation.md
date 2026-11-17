# requestCommand & requestParams Explained

## The hub sends

```cpp
struct RequestMessage {
    MessageType type;      MessageType::Request
    uint32_t requestId;    // unique ID
    uint8_t commandLength; // bytes in the command string
    uint8_t paramLength;   // num bytes in the parameters
    // actual data follows: [command string] + [binary params]
};
```

## For example

Hub tells Node #2 to water

**RequestMessage header:**
- `requestId = 42` (this request is #42)
- `commandLength = 15`
- `paramLength = 2`

**Followed by:**
- `requestCommand = "water_plant"`
- `requestParams = [50, 0]` (50ml of water)

**requestCommand** = The operation name  
**requestParams** = The arguments for that operation

## In the node you set up a handler function

(I used AI to make parts of the example, I have edited it, but handle with care)

```cpp
void setup() {
    openCommunication();  // Start ESP-NOW radio
    
    // Register nodes own handler function
    setRequestHandler(myCommandHandler);
}

uint8_t myCommandHandler(const char* command, const uint8_t* params, size_t paramLength) {
    if (strcmp(command, "water_plant") == 0) {

        uint16_t amountMl = params[1] * 256 + params[0];
        
        //do the watering
        pumpWater(amountMl);
        
        //send response back to hub
        sendOk(requestId);
        return 0;  //success
    }
    else if (strcmp(command, "read_sensor") == 0) {
        int reading = readWeight();
        
        //snd the sensor reading back to hub
        sendOkWithValue(requestId, reading);
        return 0;
    }
    
    return 255;  // Unknown command
}

void loop() {
    handleRequest();  // Check if a request arrived and process it
    // Your other code
}
```

## Request Processing Flow

1. `handleRequest()` checks if `requestReceived` flag is set

2. If yes, it calls `processRequest()`

3. `processRequest()` calls your handler with the command and params

4. **Your handler must call a send function to return data:**
   - `sendOk(requestId)` - Send "ok"
   - `sendOkWithValue(requestId, value)` - Send "ok:value"
   - `sendError(requestId)` - Send "error"
   - `sendErrorWithCode(requestId, code)` - Send "error:code"
   - `sendResponseString(requestId, str)` - Send custom text
   - `sendResponseData(requestId, data, length)` - Send binary data

5. Your handler's return value is optional (0-255 status code)

**Important:** The `requestId` is a global variable that gets set when a request arrives. Use it in the send functions to match the response with the original request.

**Example of sending different response types:**
```cpp
// if just acknowledge you got it
sendOk(requestId);

// if send a numeric value back
sendOkWithValue(requestId, 500);

// send string
sendResponseString(requestId, "temperature:25.5");

// send binary data
uint8_t data[4] = {0x01, 0x02, 0x03, 0x04};
sendResponseData(requestId, data, 4);
```

sendResponseData)=) is used for sending images for example or many values.
sendOk is used when we just want to ack the hub and say that we recieved, but we dont actually will get anything to replyu
and sendOkWithValue() is used for returning a simple measurement like a weight.
sendError() is used when we know nothing about the erorr.
sendErrorWithCode() when we wand to separate different errors from eachother, we can give it a code
