#pragma once

#include <stddef.h>
#include <stdint.h>

bool openCommunication();
bool sendData(const uint8_t* data, size_t length);
bool closeCommunication();
uint8_t getNodeId();

typedef uint8_t (*RequestHandler)(const char* command, const uint8_t* params, 
                                   size_t paramLength);

void setRequestHandler(RequestHandler handler);
void handleRequest();
bool sendResponseData(uint32_t requestId, const uint8_t* data, size_t length);
bool sendResponseString(uint32_t requestId, const char* str);
bool sendOk(uint32_t requestId);
bool sendOkWithValue(uint32_t requestId, uint32_t value);
bool sendError(uint32_t requestId);
bool sendErrorWithCode(uint32_t requestId, uint8_t code);
bool sendStreamingResponse(uint32_t requestId, const uint8_t* data, size_t length);


