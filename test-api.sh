#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://talibhussain-todo-app-deploy.hf.space"

echo -e "${YELLOW}Testing Hugging Face API Deployment${NC}"
echo "========================================"
echo ""

# Test 1: Check if API is responding
echo -e "${YELLOW}1. Checking API health...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API is responding (HTTP $HEALTH_RESPONSE)${NC}"
    HEALTH_DATA=$(curl -s $API_URL)
    echo "Response: $HEALTH_DATA"
else
    echo -e "${RED}❌ API not ready yet (HTTP $HEALTH_RESPONSE)${NC}"
    echo ""
    echo "The Space is still building. Please wait a few minutes and try again."
    echo "Monitor build progress at: https://huggingface.co/spaces/TalibHussain/todo-app-deploy"
    exit 1
fi

echo ""

# Test 2: Check API docs
echo -e "${YELLOW}2. Checking API documentation...${NC}"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/docs)

if [ "$DOCS_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API docs available${NC}"
    echo "View docs at: $API_URL/docs"
else
    echo -e "${RED}❌ API docs not accessible (HTTP $DOCS_RESPONSE)${NC}"
fi

echo ""

# Test 3: Test user signup
echo -e "${YELLOW}3. Testing user signup endpoint...${NC}"
SIGNUP_RESPONSE=$(curl -s -X POST $API_URL/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test User",
        "email": "test_'$(date +%s)'@example.com",
        "password": "SecurePass123!"
    }')

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Signup working${NC}"
    echo "Response: ${SIGNUP_RESPONSE:0:100}..."
else
    echo -e "${RED}❌ Signup failed${NC}"
    echo "Response: $SIGNUP_RESPONSE"
fi

echo ""

# Test 4: Test user login
echo -e "${YELLOW}4. Testing user login endpoint...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "SecurePass123!"
    }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login working${NC}"

    # Extract token for next test
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

    # Test 5: Test authenticated endpoint
    echo ""
    echo -e "${YELLOW}5. Testing authenticated endpoint (get tasks)...${NC}"
    TASKS_RESPONSE=$(curl -s $API_URL/api/tasks \
        -H "Authorization: Bearer $TOKEN")

    if echo "$TASKS_RESPONSE" | grep -q "\["; then
        echo -e "${GREEN}✅ Authenticated endpoints working${NC}"
        echo "Response: $TASKS_RESPONSE"
    else
        echo -e "${RED}❌ Authenticated endpoint failed${NC}"
        echo "Response: $TASKS_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  Login failed (expected - test user may not exist)${NC}"
    echo "This is normal if you haven't created a user yet."
fi

echo ""
echo "========================================"
echo -e "${GREEN}API Testing Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Visit $API_URL/docs to explore all endpoints"
echo "2. Deploy frontend to Vercel with this API URL"
echo "3. Test the complete application"
